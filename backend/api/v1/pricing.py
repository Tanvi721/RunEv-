import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models
from backend.core.security import get_current_user, require_roles
from backend.database import get_db
from backend.schemas.pricing import PriceEstimateRequest, PriceEstimateResponse, PricingSettingsResponse, PricingSettingsUpdate
from backend.services.dispatch_service import find_available_provider
from backend.services.geo_service import calculate_distance, estimate_eta_minutes
from backend.services.pricing_service import calculate_fare_breakdown, get_pricing_settings, settings_payload

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/settings", response_model=PricingSettingsResponse)
def read_pricing_settings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return settings_payload(get_pricing_settings(db))


@router.put("/settings", response_model=PricingSettingsResponse)
def update_pricing_settings(
    data: PricingSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("admin")),
):
    settings = get_pricing_settings(db)
    settings.base_visit_fee = data.base_visit_fee
    settings.distance_rate_per_km = data.distance_rate_per_km
    settings.charging_rate_per_kwh = data.charging_rate_per_kwh
    settings.platform_fee = data.platform_fee
    settings.emergency_fee_limit = data.emergency_fee_limit
    settings.night_fee_limit = data.night_fee_limit
    settings.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(settings)
    return settings_payload(settings)


@router.post("/estimate", response_model=PriceEstimateResponse)
def estimate_price(
    data: PriceEstimateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    provider = find_available_provider(
        db,
        pickup_lat=data.pickup_lat,
        pickup_lng=data.pickup_lng,
        provider_id=data.provider_id,
    )
    if not provider.current_lat or not provider.current_lng:
        raise HTTPException(status_code=404, detail="Provider location is not available")

    distance_km = calculate_distance(data.pickup_lat, data.pickup_lng, provider.current_lat, provider.current_lng)
    breakdown = calculate_fare_breakdown(
        distance_km,
        energy_kwh=data.estimated_energy_kwh,
        settings=get_pricing_settings(db),
    )

    return {
        "provider_id": provider.id,
        "estimated_distance_km": breakdown["estimated_distance_km"],
        "estimated_eta_minutes": estimate_eta_minutes(distance_km),
        "estimated_price": breakdown["total_fare"],
        "fare_breakdown": breakdown,
    }
