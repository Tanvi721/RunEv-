from typing import Optional

from pydantic import BaseModel


class PriceEstimateRequest(BaseModel):
    pickup_lat: float
    pickup_lng: float
    provider_id: Optional[int] = None


class PriceEstimateResponse(BaseModel):
    provider_id: int
    estimated_distance_km: float
    estimated_eta_minutes: int
    surge_multiplier: float
    estimated_price: float
