from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models
from backend.core.security import get_current_user, require_roles
from backend.database import get_db
from backend.schemas.service_request import (
    ChargeUnitsRequest,
    PaymentMethodSelection,
    RequestChargeRequest,
    RequestChargeResponse,
    ServiceRequestResponse,
)
from backend.services.dispatch_service import assign_charge_request, request_payload
from backend.services.realtime_service import manager

router = APIRouter(prefix="/requests", tags=["requests"])
legacy_router = APIRouter(tags=["requests"])


def request_charge_response(service_request: models.ServiceRequest, distance_km: float, eta_minutes: int) -> dict:
    provider = service_request.provider
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
        },
        "estimated_distance_km": round(distance_km, 2),
        "estimated_eta_minutes": eta_minutes,
        "estimated_price": service_request.total_price or 0,
    }


def create_charge_request(request: RequestChargeRequest, db: Session, user_id: Optional[int] = None):
    service_request, distance_km, eta_minutes = assign_charge_request(
        db,
        user_id=user_id if user_id is not None else request.user_id,
        pickup_lat=request.pickup_lat,
        pickup_lng=request.pickup_lng,
        provider_id=request.provider_id,
    )
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
    return request_payload(service_request)


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
    db.commit()
    db.refresh(service_request)
    return request_payload(service_request)


def start_request_charging(request_id: int, db: Session, provider_user_id: Optional[int] = None):
    service_request = load_request_or_404(request_id, db)
    if provider_user_id is not None and service_request.provider and service_request.provider.user_id != provider_user_id:
        raise HTTPException(status_code=403, detail="This request is assigned to another provider")
    if service_request.status not in {"arrived", "charging"}:
        raise HTTPException(status_code=400, detail="Charging can only start after the driver has reached")

    service_request.status = "charging"
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

    rate = float(service_request.provider.price_per_kwh or 20.0)
    service_request.charged_units_kwh = round(float(data.charged_units_kwh), 2)
    service_request.total_price = round(service_request.charged_units_kwh * rate, 2)
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("provider", "admin")),
):
    provider_user_id = None if current_user.role == "admin" else current_user.id
    response = start_request_charging(request_id, db, provider_user_id=provider_user_id)
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
