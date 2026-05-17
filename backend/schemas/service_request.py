from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from .provider import ProviderResponse


class RequestChargeRequest(BaseModel):
    user_id: Optional[int] = 1
    provider_id: Optional[int] = None
    pickup_lat: float
    pickup_lng: float


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
    notification_message: Optional[str] = None
    route_status_label: Optional[str] = None


class RequestChargeResponse(BaseModel):
    message: str
    request_id: int
    provider: ProviderResponse
    estimated_distance_km: float
    estimated_eta_minutes: int
    estimated_price: float


class ChargeUnitsRequest(BaseModel):
    charged_units_kwh: float


class PaymentMethodSelection(BaseModel):
    payment_method: str


class OtpVerificationRequest(BaseModel):
    otp_code: str
