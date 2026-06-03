from typing import Optional
import math

from pydantic import BaseModel, model_validator
from pydantic import field_validator


def _validate_latitude(value: float) -> float:
    if value is None or not math.isfinite(float(value)) or not -90 <= float(value) <= 90:
        raise ValueError("Latitude must be a finite number between -90 and 90.")
    return float(value)


def _validate_longitude(value: float) -> float:
    if value is None or not math.isfinite(float(value)) or not -180 <= float(value) <= 180:
        raise ValueError("Longitude must be a finite number between -180 and 180.")
    return float(value)


class ProviderLocationUpdate(BaseModel):
    provider_id: Optional[int] = None
    current_lat: float
    current_lng: float
    address: Optional[str] = None
    is_available: Optional[bool] = None

    @field_validator("current_lat")
    @classmethod
    def current_lat_valid(cls, value: float) -> float:
        return _validate_latitude(value)

    @field_validator("current_lng")
    @classmethod
    def current_lng_valid(cls, value: float) -> float:
        return _validate_longitude(value)

    @model_validator(mode="after")
    def current_location_not_stale_default(self):
        address = (self.address or "").lower()
        if (
            round(float(self.current_lat), 4) == 18.5204
            and round(float(self.current_lng), 4) == 73.8567
            and "pune" not in address
        ):
            raise ValueError("Driver location is still the default Pune coordinate. Share live location first.")
        return self


class ProviderLocationResponse(BaseModel):
    provider_id: int
    current_lat: float
    current_lng: float
    address: Optional[str] = None
    is_available: bool
