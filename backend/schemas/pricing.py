from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PricingSettingsResponse(BaseModel):
    base_visit_fee: float
    distance_rate_per_km: float
    charging_rate_per_kwh: float
    platform_fee: float
    emergency_fee_limit: float
    night_fee_limit: float
    updated_at: Optional[datetime] = None


class PricingSettingsUpdate(BaseModel):
    base_visit_fee: float = Field(ge=0)
    distance_rate_per_km: float = Field(ge=0)
    charging_rate_per_kwh: float = Field(ge=0)
    platform_fee: float = Field(ge=0)
    emergency_fee_limit: float = Field(ge=0)
    night_fee_limit: float = Field(ge=0)


class FareBreakdown(BaseModel):
    base_visit_fee: float
    distance_rate_per_km: float
    charging_rate_per_kwh: float
    platform_fee: float
    estimated_distance_km: float
    charged_units_kwh: float = 0
    distance_charge: float
    charging_cost: float
    emergency_fee: float = 0
    night_fee: float = 0
    total_fare: float
    driver_earnings: float
    runev_earnings: float
    charging_revenue: float


class PriceEstimateRequest(BaseModel):
    pickup_lat: float
    pickup_lng: float
    provider_id: Optional[int] = None
    estimated_energy_kwh: float = Field(default=0, ge=0)


class PriceEstimateResponse(BaseModel):
    provider_id: int
    estimated_distance_km: float
    estimated_eta_minutes: int
    estimated_price: float
    fare_breakdown: FareBreakdown
