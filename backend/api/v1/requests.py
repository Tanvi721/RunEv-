import datetime
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models
from backend.core.security import get_current_user, require_roles
from backend.database import get_db
from backend.schemas.service_request import (
    ChargeUnitsRequest,
    OtpVerificationRequest,
    PaymentMethodSelection,
    RequestChargeRequest,
    RequestChargeResponse,
    ServiceRequestResponse,
)
from backend.services.dispatch_service import assign_charge_request, request_payload
from backend.services.auth_service import send_trip_otp_email
from backend.services.pricing_service import apply_fare_breakdown, calculate_fare_breakdown, get_pricing_settings, request_fare_breakdown
from backend.services.realtime_service import manager

router = APIRouter(prefix="/requests", tags=["requests"])
legacy_router = APIRouter(tags=["requests"])
OTP_ELIGIBLE_STATUSES = {"accepted", "en_route", "arrived"}


def try_send_trip_otp_email(service_request: models.ServiceRequest) -> None:
    if not service_request.user or not service_request.user.email or not service_request.otp_code:
        return
    try:
        send_trip_otp_email(service_request.user.email, service_request.otp_code)
    except HTTPException as exc:
        print(f"RunEV trip OTP email was not sent: {exc.detail}")
        print(f"RunEV trip OTP for request {service_request.id}: {service_request.otp_code}")


def ensure_trip_otp(service_request: models.ServiceRequest, db: Session) -> None:
    if service_request.status in OTP_ELIGIBLE_STATUSES and not service_request.otp_code:
        service_request.otp_code = f"{secrets.randbelow(900000) + 100000}"
        service_request.otp_verified_at = None
        try_send_trip_otp_email(service_request)
        db.commit()
        db.refresh(service_request)


def request_charge_response(service_request: models.ServiceRequest, distance_km: float, eta_minutes: int) -> dict:
    provider = service_request.provider
    rating_count = len(provider.ratings)
    average_rating = (
        round(sum(rating.score for rating in provider.ratings) / rating_count, 1)
        if rating_count
        else None
    )
    return {
        "message": "Request sent successfully",
        "request_id": service_request.id,
        "provider": {
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
            "phone": provider.user.phone if provider.user else None,
            "average_rating": average_rating,
            "rating_count": rating_count,
        },
        "estimated_distance_km": round(distance_km, 2),
        "estimated_eta_minutes": eta_minutes,
        "estimated_price": service_request.total_price or 0,
        "fare_breakdown": request_fare_breakdown(service_request),
    }


def create_charge_request(request: RequestChargeRequest, db: Session, user_id: Optional[int] = None):
    service_request, distance_km, eta_minutes = assign_charge_request(
        db,
        user_id=user_id if user_id is not None else request.user_id,
        pickup_lat=request.pickup_lat,
        pickup_lng=request.pickup_lng,
        provider_id=request.provider_id,
    )
    breakdown = calculate_fare_breakdown(distance_km, settings=get_pricing_settings(db))
    apply_fare_breakdown(service_request, breakdown)
    db.commit()
    db.refresh(service_request)
    return request_charge_response(service_request, distance_km, eta_minutes)


async def broadcast_request_change(service_request: models.ServiceRequest, event_type: str):
    payload = request_payload(service_request)
    await manager.broadcast_request(service_request.id, {"type": event_type, "data": payload})
    if service_request.provider_id is not None:
        await manager.broadcast_provider(
            service_request.provider_id,
            {"type": event_type, "data": payload},
        )


@router.post("/charge", response_model=RequestChargeResponse)
async def request_charge_v1(
    request: RequestChargeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("user", "provider", "admin")),
):
    request_user_id = request.user_id if current_user.role == "admin" else current_user.id
    response = create_charge_request(request, db, user_id=request_user_id)
    service_request = load_request_or_404(response["request_id"], db)
    await broadcast_request_change(service_request, "request.created")
    return response


@legacy_router.post("/request-charge", response_model=RequestChargeResponse)
async def request_charge_legacy(request: RequestChargeRequest, db: Session = Depends(get_db)):
    response = create_charge_request(request, db)
    service_request = load_request_or_404(response["request_id"], db)
    await broadcast_request_change(service_request, "request.created")
    return response


def load_request_or_404(request_id: int, db: Session, user_id: Optional[int] = None):
    query = db.query(models.ServiceRequest).filter(models.ServiceRequest.id == request_id)
    if user_id is not None:
        query = query.filter(models.ServiceRequest.user_id == user_id)
    service_request = query.first()
    if not service_request:
        raise HTTPException(status_code=404, detail="Request not found")
    return service_request


def ensure_request_access(service_request: models.ServiceRequest, current_user: models.User):
    if current_user.role == "admin":
        return
    if current_user.role == "user" and service_request.user_id == current_user.id:
        return
    if (
        current_user.role == "provider"
        and service_request.provider
        and service_request.provider.user_id == current_user.id
    ):
        return
    raise HTTPException(status_code=403, detail="You do not have access to this request")


@router.get("/charge/{request_id}", response_model=ServiceRequestResponse)
def get_request_charge_v1(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    service_request = load_request_or_404(request_id, db)
    ensure_request_access(service_request, current_user)
    ensure_trip_otp(service_request, db)
    show_otp_to_passenger = current_user.role == "user" and service_request.user_id == current_user.id
    return request_payload(service_request, include_otp=show_otp_to_passenger)


@router.get("/mine", response_model=list[ServiceRequestResponse])
def get_my_requests_v1(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("user", "provider", "admin")),
):
    query = db.query(models.ServiceRequest)
    if current_user.role != "admin":
        query = query.filter(models.ServiceRequest.user_id == current_user.id)
    return [
        request_payload(service_request)
        for service_request in query.order_by(models.ServiceRequest.request_time.desc()).all()
    ]


@legacy_router.get("/request-charge/{request_id}", response_model=ServiceRequestResponse)
def get_request_charge_legacy(request_id: int, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    service_request = load_request_or_404(request_id, db, user_id=user_id)
    return request_payload(service_request)


def accept_request(request_id: int, db: Session, provider_user_id: Optional[int] = None):
    service_request = load_request_or_404(request_id, db)
    if provider_user_id is not None and service_request.provider and service_request.provider.user_id != provider_user_id:
        raise HTTPException(status_code=403, detail="This request is assigned to another provider")

    service_request.status = "en_route"
    service_request.otp_code = f"{secrets.randbelow(900000) + 100000}"
    service_request.otp_verified_at = None
    try_send_trip_otp_email(service_request)
    if service_request.provider:
        service_request.provider.is_available = False
    db.commit()
    db.refresh(service_request)
    return request_payload(service_request)


@router.post("/charge/{request_id}/accept", response_model=ServiceRequestResponse)
async def accept_request_charge_v1(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("provider", "admin")),
):
    provider_user_id = None if current_user.role == "admin" else current_user.id
    response = accept_request(request_id, db, provider_user_id=provider_user_id)
    service_request = load_request_or_404(request_id, db)
    await broadcast_request_change(service_request, "request.en_route")
    return response


@legacy_router.post("/request-charge/{request_id}/accept", response_model=ServiceRequestResponse)
async def accept_request_charge_legacy(
    request_id: int,
    provider_user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    response = accept_request(request_id, db, provider_user_id=provider_user_id)
    service_request = load_request_or_404(request_id, db)
    await broadcast_request_change(service_request, "request.en_route")
    return response


def reject_request(request_id: int, db: Session, provider_user_id: Optional[int] = None):
    service_request = load_request_or_404(request_id, db)
    if provider_user_id is not None and service_request.provider and service_request.provider.user_id != provider_user_id:
        raise HTTPException(status_code=403, detail="This request is assigned to another provider")

    service_request.status = "cancelled"
    if service_request.provider:
        service_request.provider.is_available = True
    db.commit()
    db.refresh(service_request)
    return request_payload(service_request)


def complete_request(request_id: int, db: Session, provider_user_id: Optional[int] = None):
    service_request = load_request_or_404(request_id, db)
    if provider_user_id is not None and service_request.provider and service_request.provider.user_id != provider_user_id:
        raise HTTPException(status_code=403, detail="This request is assigned to another provider")

    service_request.status = "completed"
    if service_request.provider:
        service_request.provider.is_available = True
    db.commit()
    db.refresh(service_request)
    return request_payload(service_request)


def mark_request_arrived(request_id: int, db: Session, provider_user_id: Optional[int] = None):
    service_request = load_request_or_404(request_id, db)
    if provider_user_id is not None and service_request.provider and service_request.provider.user_id != provider_user_id:
        raise HTTPException(status_code=403, detail="This request is assigned to another provider")

    service_request.status = "arrived"
    if service_request.provider:
        service_request.provider.current_lat = service_request.pickup_lat
        service_request.provider.current_lng = service_request.pickup_lng
    db.commit()
    db.refresh(service_request)
    return request_payload(service_request)


def start_request_charging(
    request_id: int,
    data: OtpVerificationRequest,
    db: Session,
    provider_user_id: Optional[int] = None,
):
    service_request = load_request_or_404(request_id, db)
    if provider_user_id is not None and service_request.provider and service_request.provider.user_id != provider_user_id:
        raise HTTPException(status_code=403, detail="This request is assigned to another provider")
    if service_request.status not in {"arrived", "charging"}:
        raise HTTPException(status_code=400, detail="Charging can only start after the driver has reached")
    if not service_request.otp_code:
        raise HTTPException(status_code=400, detail="OTP is not available for this request")
    if service_request.otp_verified_at is None and data.otp_code.strip() != service_request.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    service_request.status = "charging"
    if service_request.otp_verified_at is None:
        service_request.otp_verified_at = datetime.datetime.utcnow()
    if service_request.provider:
        service_request.provider.current_lat = service_request.pickup_lat
        service_request.provider.current_lng = service_request.pickup_lng
    db.commit()
    db.refresh(service_request)
    return request_payload(service_request)


def submit_charge_units(
    request_id: int,
    data: ChargeUnitsRequest,
    db: Session,
    provider_user_id: Optional[int] = None,
):
    service_request = load_request_or_404(request_id, db)
    if provider_user_id is not None and service_request.provider and service_request.provider.user_id != provider_user_id:
        raise HTTPException(status_code=403, detail="This request is assigned to another provider")
    if not service_request.provider:
        raise HTTPException(status_code=400, detail="Request does not have an assigned provider")
    if service_request.status != "charging":
        raise HTTPException(status_code=400, detail="Complete charging before generating the bill")
    if data.charged_units_kwh <= 0:
        raise HTTPException(status_code=400, detail="Charged units must be greater than zero")

    service_request.charged_units_kwh = round(float(data.charged_units_kwh), 2)
    distance_km = service_request.estimated_distance_km
    if distance_km is None and service_request.provider.current_lat is not None and service_request.provider.current_lng is not None:
        from backend.services.geo_service import calculate_distance

        distance_km = calculate_distance(
            service_request.pickup_lat,
            service_request.pickup_lng,
            service_request.provider.current_lat,
            service_request.provider.current_lng,
        )
    settings = get_pricing_settings(db)
    if data.emergency_fee > float(settings.emergency_fee_limit or 0):
        raise HTTPException(status_code=400, detail=f"Emergency fee cannot exceed Rs {float(settings.emergency_fee_limit or 0):.2f}")
    if data.night_fee > float(settings.night_fee_limit or 0):
        raise HTTPException(status_code=400, detail=f"Night fee cannot exceed Rs {float(settings.night_fee_limit or 0):.2f}")
    breakdown = calculate_fare_breakdown(
        distance_km or 0,
        energy_kwh=service_request.charged_units_kwh,
        emergency_fee=data.emergency_fee,
        night_fee=data.night_fee,
        settings=settings,
    )
    apply_fare_breakdown(service_request, breakdown)
    service_request.status = "awaiting_payment"
    db.commit()
    db.refresh(service_request)
    return request_payload(service_request)


def select_payment_method(
    request_id: int,
    data: PaymentMethodSelection,
    db: Session,
    user_id: Optional[int] = None,
):
    service_request = load_request_or_404(request_id, db)
    if user_id is not None and service_request.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only pay for your own request")
    if not service_request.total_price:
        raise HTTPException(status_code=400, detail="Driver has not generated the final bill yet")

    payment_method = data.payment_method.upper()
    allowed_methods = {"CASH", "CARD", "UPI", "NETBANKING", "PAY_LATER"}
    if payment_method not in allowed_methods:
        raise HTTPException(status_code=400, detail="Unsupported payment method")

    service_request.payment_method = payment_method
    service_request.status = "completed"
    if service_request.provider:
        service_request.provider.is_available = True

    existing_payment = service_request.payment
    if existing_payment:
        existing_payment.amount = service_request.total_price
        existing_payment.status = "pending" if payment_method in {"PAY_LATER", "CARD", "UPI", "NETBANKING"} else "success"
    else:
        payment = models.Payment(
            request_id=service_request.id,
            user_id=service_request.user_id,
            amount=service_request.total_price,
            status="pending" if payment_method in {"PAY_LATER", "CARD", "UPI", "NETBANKING"} else "success",
        )
        db.add(payment)

    db.commit()
    db.refresh(service_request)
    return request_payload(service_request)


@router.post("/charge/{request_id}/reject", response_model=ServiceRequestResponse)
async def reject_request_charge_v1(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("provider", "admin")),
):
    provider_user_id = None if current_user.role == "admin" else current_user.id
    response = reject_request(request_id, db, provider_user_id=provider_user_id)
    service_request = load_request_or_404(request_id, db)
    await broadcast_request_change(service_request, "request.rejected")
    return response


@router.post("/charge/{request_id}/complete", response_model=ServiceRequestResponse)
async def complete_request_charge_v1(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("provider", "admin")),
):
    provider_user_id = None if current_user.role == "admin" else current_user.id
    response = complete_request(request_id, db, provider_user_id=provider_user_id)
    service_request = load_request_or_404(request_id, db)
    await broadcast_request_change(service_request, "request.completed")
    return response


@router.post("/charge/{request_id}/arrived", response_model=ServiceRequestResponse)
async def mark_request_arrived_v1(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("provider", "admin")),
):
    provider_user_id = None if current_user.role == "admin" else current_user.id
    response = mark_request_arrived(request_id, db, provider_user_id=provider_user_id)
    service_request = load_request_or_404(request_id, db)
    await broadcast_request_change(service_request, "request.arrived")
    return response


@router.post("/charge/{request_id}/start-charging", response_model=ServiceRequestResponse)
async def start_request_charging_v1(
    request_id: int,
    data: OtpVerificationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("provider", "admin")),
):
    provider_user_id = None if current_user.role == "admin" else current_user.id
    response = start_request_charging(request_id, data, db, provider_user_id=provider_user_id)
    service_request = load_request_or_404(request_id, db)
    await broadcast_request_change(service_request, "request.charging_started")
    return response


@router.post("/charge/{request_id}/units", response_model=ServiceRequestResponse)
async def submit_charge_units_v1(
    request_id: int,
    data: ChargeUnitsRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("provider", "admin")),
):
    provider_user_id = None if current_user.role == "admin" else current_user.id
    response = submit_charge_units(request_id, data, db, provider_user_id=provider_user_id)
    service_request = load_request_or_404(request_id, db)
    await broadcast_request_change(service_request, "request.bill_ready")
    return response


@router.post("/charge/{request_id}/payment-method", response_model=ServiceRequestResponse)
async def select_payment_method_v1(
    request_id: int,
    data: PaymentMethodSelection,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("user", "admin")),
):
    user_id = None if current_user.role == "admin" else current_user.id
    response = select_payment_method(request_id, data, db, user_id=user_id)
    service_request = load_request_or_404(request_id, db)
    await broadcast_request_change(service_request, "request.payment_selected")
    return response


@legacy_router.post("/request-charge/{request_id}/reject", response_model=ServiceRequestResponse)
async def reject_request_charge_legacy(
    request_id: int,
    provider_user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    response = reject_request(request_id, db, provider_user_id=provider_user_id)
    service_request = load_request_or_404(request_id, db)
    await broadcast_request_change(service_request, "request.rejected")
    return response


def get_pending_provider_requests(db: Session, provider_user_id: Optional[int] = None):
    query = db.query(models.ServiceRequest).filter(models.ServiceRequest.status == "pending")
    if provider_user_id is not None:
        provider_ids = [
            row.id
            for row in db.query(models.Provider.id).filter(models.Provider.user_id == provider_user_id).all()
        ]
        if not provider_ids:
            raise HTTPException(status_code=404, detail="Provider not found")
        query = query.filter(models.ServiceRequest.provider_id.in_(provider_ids))
    return [request_payload(req) for req in query.order_by(models.ServiceRequest.request_time.desc()).all()]


@router.get("/provider", response_model=list[ServiceRequestResponse])
def get_pending_requests_v1(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("provider", "admin")),
):
    provider_user_id = None if current_user.role == "admin" else current_user.id
    return get_pending_provider_requests(db, provider_user_id=provider_user_id)


@legacy_router.get("/provider/requests", response_model=list[ServiceRequestResponse])
def get_pending_requests_legacy(provider_user_id: Optional[int] = None, db: Session = Depends(get_db)):
    return get_pending_provider_requests(db, provider_user_id=provider_user_id)
