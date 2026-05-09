from typing import Optional

from pydantic import BaseModel


class ProviderLocationUpdate(BaseModel):
    provider_id: Optional[int] = None
    current_lat: float
    current_lng: float
    address: Optional[str] = None
    is_available: Optional[bool] = None


class ProviderLocationResponse(BaseModel):
    provider_id: int
    current_lat: float
    current_lng: float
    address: Optional[str] = None
    is_available: bool
