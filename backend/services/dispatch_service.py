from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend import models
from backend.services.geo_service import calculate_distance, estimate_eta_minutes

ACTIVE_TRIP_STATUSES = ("pending", "en_route", "accepted", "arrived", "charging", "awaiting_payment")
ARRIVAL_DISTANCE_KM = 0.2


def find_available_provider(
    db: Session,
    pickup_lat: float,
    pickup_lng: float,
    provider_id: Optional[int] = None,
) -> models.Provider:
    query = db.query(models.Provider).filter(
        models.Provider.is_available == True,
        models.Provider.current_lat != None,
        models.Provider.current_lng != None,
    )

    if provider_id is not None:
        provider = query.filter(models.Provider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Selected van is not available right now")
        return provider

    providers = query.all()
    if not providers:
        raise HTTPException(status_code=404, detail="No available charging vans at the moment")

    return min(
        providers,
        key=lambda provider: calculate_distance(
            pickup_lat,
            pickup_lng,
            provider.current_lat,
            provider.current_lng,
        ),
    )


def assign_charge_request(
    db: Session,
    user_id: Optional[int],
    pickup_lat: float,
    pickup_lng: float,
    provider_id: Optional[int] = None,
) -> tuple[models.ServiceRequest, float, int]:
    provider = find_available_provider(db, pickup_lat, pickup_lng, provider_id)
    distance_km = calculate_distance(pickup_lat, pickup_lng, provider.current_lat, provider.current_lng)

    service_request = models.ServiceRequest(
        user_id=user_id,
        provider_id=provider.id,
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        status="pending",
        total_price=None,
    )
    provider.is_available = False
    db.add(service_request)
    db.commit()
    db.refresh(service_request)

    return service_request, distance_km, estimate_eta_minutes(distance_km)


def request_payload(service_request: models.ServiceRequest, include_otp: bool = False) -> dict:
    provider = service_request.provider
    user = service_request.user
    distance_km = None
    eta_minutes = None
    provider_payload = None
    user_payload = None

    if provider:
        rating_count = len(provider.ratings)
        average_rating = (
            round(sum(rating.score for rating in provider.ratings) / rating_count, 1)
            if rating_count
            else None
        )
        provider_payload = {
            "id": provider.id,
            "user_id": provider.user_id,
            "vehicle_number": provider.vehicle_number,
            "current_lat": provider.current_lat,
            "current_lng": provider.current_lng,
            "is_available": provider.is_available,
            "charging_speed": provider.charging_speed,
            "connector_types": provider.connector_types,
            "price_per_kwh": provider.price_per_kwh,
            "driver_name": provider.driver_name,
            "address": provider.address,
            "phone": provider.user.phone if provider.user else None,
            "average_rating": average_rating,
            "rating_count": rating_count,
        }
        if provider.current_lat is not None and provider.current_lng is not None:
            distance_km = calculate_distance(
                service_request.pickup_lat,
                service_request.pickup_lng,
                provider.current_lat,
                provider.current_lng,
            )
            eta_minutes = estimate_eta_minutes(distance_km)

    if user:
        user_payload = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
        }

    notification_message, route_status_label = trip_message(service_request.status, provider, distance_km, eta_minutes)

    payload = {
        "id": service_request.id,
        "user_id": service_request.user_id,
        "provider_id": service_request.provider_id,
        "pickup_lat": service_request.pickup_lat,
        "pickup_lng": service_request.pickup_lng,
        "status": service_request.status,
        "request_time": service_request.request_time,
        "payment_method": service_request.payment_method,
        "charged_units_kwh": service_request.charged_units_kwh,
        "total_price": service_request.total_price,
        "otp_verified_at": service_request.otp_verified_at,
        "provider": provider_payload,
        "user": user_payload,
        "estimated_distance_km": round(distance_km, 2) if distance_km is not None else None,
        "estimated_eta_minutes": eta_minutes,
        "notification_message": notification_message,
        "route_status_label": route_status_label,
    }
    if include_otp:
        payload["otp_code"] = service_request.otp_code
    return payload


def trip_message(
    status: str | None,
    provider: models.Provider | None,
    distance_km: float | None,
    eta_minutes: int | None,
) -> tuple[str, str]:
    driver = provider.driver_name if provider and provider.driver_name else "Your RunEV driver"
    vehicle = provider.vehicle_number if provider and provider.vehicle_number else "charging van"
    normalized = status or "pending"

    if normalized == "pending":
        return f"{vehicle} is assigned. Waiting for the driver to confirm.", "Assigned"
    if normalized in {"accepted", "en_route"}:
        eta = f"{eta_minutes} min" if eta_minutes is not None else "a few minutes"
        distance = f" ({distance_km:.2f} km away)" if distance_km is not None else ""
        return f"{driver} is on the way in {vehicle}. ETA {eta}{distance}.", "In Route"
    if normalized == "arrived":
        return f"{driver} has reached your pickup location.", "Reached"
    if normalized == "charging":
        return "Charging has started. You can relax while the session runs.", "Charging"
    if normalized == "awaiting_payment":
        return "Charging is complete. Your bill is ready for payment.", "Bill Ready"
    if normalized == "completed":
        return "Payment complete. Thanks for choosing RunEV.", "Completed"
    if normalized == "cancelled":
        return "This charging request was cancelled.", "Cancelled"
    return f"Trip status updated to {normalized.replace('_', ' ').title()}.", normalized.replace("_", " ").title()
