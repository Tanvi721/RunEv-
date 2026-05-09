from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from backend import models
from backend.core.security import require_roles
from backend.database import get_db
from backend.schemas.tracking import ProviderLocationResponse, ProviderLocationUpdate
from backend.services.dispatch_service import ACTIVE_TRIP_STATUSES, ARRIVAL_DISTANCE_KM, request_payload
from backend.services.geo_service import calculate_distance
from backend.services.realtime_service import manager

router = APIRouter(prefix="/tracking", tags=["tracking"])
ws_router = APIRouter(tags=["tracking"])


@router.put("/provider/location", response_model=ProviderLocationResponse)
async def update_provider_location(
    data: ProviderLocationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("provider", "admin")),
):
    if current_user.role == "admin":
        if data.provider_id is None:
            raise HTTPException(status_code=400, detail="Admin location updates require provider_id")
        provider_query = db.query(models.Provider).filter(models.Provider.id == data.provider_id)
    else:
        provider_query = db.query(models.Provider).filter(models.Provider.user_id == current_user.id)
        if data.provider_id is not None:
            provider_query = provider_query.filter(models.Provider.id == data.provider_id)
    provider = provider_query.first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found")

    provider.current_lat = data.current_lat
    provider.current_lng = data.current_lng
    if data.address is not None:
        provider.address = data.address
    if data.is_available is not None:
        provider.is_available = data.is_available

    db.commit()
    db.refresh(provider)

    response = {
        "provider_id": provider.id,
        "current_lat": provider.current_lat,
        "current_lng": provider.current_lng,
        "address": provider.address,
        "is_available": provider.is_available,
    }

    await manager.broadcast_provider(provider.id, {"type": "provider.location_updated", "data": response})

    active_requests = db.query(models.ServiceRequest).filter(
        models.ServiceRequest.provider_id == provider.id,
        models.ServiceRequest.status.in_(ACTIVE_TRIP_STATUSES),
    ).all()
    for service_request in active_requests:
        distance_km = calculate_distance(
            service_request.pickup_lat,
            service_request.pickup_lng,
            provider.current_lat,
            provider.current_lng,
        )
        event_type = "request.location_updated"
        if service_request.status in {"accepted", "en_route"} and distance_km <= ARRIVAL_DISTANCE_KM:
            service_request.status = "arrived"
            db.commit()
            db.refresh(service_request)
            event_type = "request.arrived"
        await manager.broadcast_request(
            service_request.id,
            {"type": event_type, "data": request_payload(service_request)},
        )

    return response


@ws_router.websocket("/ws/requests/{request_id}")
async def request_updates(websocket: WebSocket, request_id: int):
    await manager.connect_request(request_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_request(request_id, websocket)


@ws_router.websocket("/ws/providers/{provider_id}")
async def provider_updates(websocket: WebSocket, provider_id: int):
    await manager.connect_provider(provider_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_provider(provider_id, websocket)
