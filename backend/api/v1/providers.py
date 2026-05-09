from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models
from backend.core.security import get_current_user, require_roles
from backend.database import get_db
from backend.schemas.provider import ProviderResponse, ProviderUpdate

router = APIRouter(prefix="/providers", tags=["providers"])
legacy_router = APIRouter(tags=["providers"])


def provider_to_response(provider: models.Provider) -> dict:
    return {
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
    }


def get_visible_providers(db: Session = Depends(get_db)):
    providers = db.query(models.Provider).filter(
        models.Provider.current_lat != None,
        models.Provider.current_lng != None,
    ).all()
    return [provider_to_response(provider) for provider in providers]


@router.get("", response_model=list[ProviderResponse])
def list_available_providers_v1(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return get_visible_providers(db)


@legacy_router.get("/providers", response_model=list[ProviderResponse])
def list_available_providers_legacy(db: Session = Depends(get_db)):
    return get_visible_providers(db)


def update_provider_profile_data(data: ProviderUpdate, db: Session):
    provider = db.query(models.Provider).filter(models.Provider.user_id == data.user_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    if data.current_lat is not None:
        provider.current_lat = data.current_lat
    if data.current_lng is not None:
        provider.current_lng = data.current_lng
    if data.is_available is not None:
        provider.is_available = data.is_available
    if data.charging_speed is not None:
        provider.charging_speed = data.charging_speed
    if data.connector_types is not None:
        provider.connector_types = data.connector_types
    if data.price_per_kwh is not None:
        provider.price_per_kwh = data.price_per_kwh

    db.commit()
    db.refresh(provider)
    return provider_to_response(provider)


@router.put("/profile", response_model=ProviderResponse)
def update_provider_profile_v1(
    data: ProviderUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("provider", "admin")),
):
    if current_user.role != "admin" and data.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own provider profile")
    return update_provider_profile_data(data, db)


@legacy_router.put("/provider/profile", response_model=ProviderResponse)
def update_provider_profile_legacy(data: ProviderUpdate, db: Session = Depends(get_db)):
    return update_provider_profile_data(data, db)
