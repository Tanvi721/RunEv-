from typing import Optional
from datetime import datetime
import math

from pydantic import BaseModel, Field, model_validator
from pydantic import field_validator

from .provider import ProviderResponse
from .pricing import FareBreakdown


class RequestChargeRequest(BaseModel):
    user_id: Optional[int] = 1
    provider_id: Optional[int] = None
    pickup_lat: float
    pickup_lng: float

    @field_validator("pickup_lat")
    @classmethod
    def pickup_lat_valid(cls, value: float) -> float:
        if value is None or not math.isfinite(float(value)) or not -90 <= float(value) <= 90:
            raise ValueError("Pickup latitude must be a finite number between -90 and 90.")
        return float(value)

    @field_validator("pickup_lng")
    @classmethod
    def pickup_lng_valid(cls, value: float) -> float:
        if value is None or not math.isfinite(float(value)) or not -180 <= float(value) <= 180:
            raise ValueError("Pickup longitude must be a finite number between -180 and 180.")
        return float(value)

    @model_validator(mode="after")
    def pickup_not_default_location(self):
        if round(float(self.pickup_lat), 4) == 18.5204 and round(float(self.pickup_lng), 4) == 73.8567:
            raise ValueError("Pickup location is still the default Pune coordinate. Share live location first.")
        return self


class ServiceRequestResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    provider_id: Optional[int] = None
    pickup_lat: float
    pickup_lng: float
    status: str
    request_time: Optional[datetime] = None
    payment_method: Optional[str] = None
    charged_units_kwh: Optional[float] = None
    total_price: Optional[float] = None
    otp_code: Optional[str] = None
    otp_verified_at: Optional[datetime] = None
    provider: Optional[ProviderResponse] = None
    user: Optional[dict] = None
    estimated_distance_km: Optional[float] = None
    estimated_eta_minutes: Optional[int] = None
    fare_breakdown: Optional[FareBreakdown] = None
    notification_message: Optional[str] = None
    route_status_label: Optional[str] = None


class RequestChargeResponse(BaseModel):
    message: str
    request_id: int
    provider: ProviderResponse
    estimated_distance_km: float
    estimated_eta_minutes: int
    estimated_price: float
    fare_breakdown: FareBreakdown


class ChargeUnitsRequest(BaseModel):
    charged_units_kwh: float = Field(gt=0, le=100)
    emergency_fee: float = Field(default=0, ge=0)
    night_fee: float = Field(default=0, ge=0)


class PaymentMethodSelection(BaseModel):
    payment_method: str


class OtpVerificationRequest(BaseModel):
    otp_code: str
