from typing import Optional

from pydantic import BaseModel


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
