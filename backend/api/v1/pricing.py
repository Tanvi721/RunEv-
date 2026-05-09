from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models
from backend.core.security import get_current_user
from backend.database import get_db
from backend.schemas.pricing import PriceEstimateRequest, PriceEstimateResponse
from backend.services.dispatch_service import find_available_provider
from backend.services.geo_service import calculate_distance, estimate_eta_minutes
from backend.services.pricing_service import estimate_service_amount, estimate_surge_multiplier

router = APIRouter(prefix="/pricing", tags=["pricing"])


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
    available_provider_count = db.query(models.Provider).filter(models.Provider.is_available == True).count()
    pending_request_count = db.query(models.ServiceRequest).filter(models.ServiceRequest.status == "pending").count()
    surge_multiplier = estimate_surge_multiplier(available_provider_count, pending_request_count)

    return {
        "provider_id": provider.id,
        "estimated_distance_km": round(distance_km, 2),
        "estimated_eta_minutes": estimate_eta_minutes(distance_km),
        "surge_multiplier": surge_multiplier,
        "estimated_price": estimate_service_amount(distance_km, provider, surge_multiplier),
    }
