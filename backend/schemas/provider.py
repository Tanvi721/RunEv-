from typing import Optional
import math

from pydantic import BaseModel
from pydantic import field_validator


class ProviderResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    vehicle_number: Optional[str] = None
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    is_available: bool
    charging_speed: Optional[str] = None
    connector_types: Optional[str] = None
    price_per_kwh: Optional[float] = None
    driver_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    average_rating: Optional[float] = None
    rating_count: int = 0

    class Config:
        from_attributes = True


class ProviderUpdate(BaseModel):
    user_id: int
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    is_available: Optional[bool] = None
    charging_speed: Optional[str] = None
    connector_types: Optional[str] = None
    price_per_kwh: Optional[float] = None

    @field_validator("current_lat")
    @classmethod
    def current_lat_valid(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        if not math.isfinite(float(value)) or not -90 <= float(value) <= 90:
            raise ValueError("Latitude must be a finite number between -90 and 90.")
        return float(value)

    @field_validator("current_lng")
    @classmethod
    def current_lng_valid(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        if not math.isfinite(float(value)) or not -180 <= float(value) <= 180:
            raise ValueError("Longitude must be a finite number between -180 and 180.")
        return float(value)
