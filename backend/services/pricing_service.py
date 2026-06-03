from __future__ import annotations

import datetime

from sqlalchemy.orm import Session

from backend import models

DEFAULT_BASE_VISIT_FEE = 99.0
DEFAULT_DISTANCE_RATE_PER_KM = 12.0
DEFAULT_CHARGING_RATE_PER_KWH = 20.0
DEFAULT_PLATFORM_FEE = 20.0


def get_pricing_settings(db: Session) -> models.PricingSetting:
    settings = db.query(models.PricingSetting).filter(models.PricingSetting.id == 1).first()
    if settings:
        return settings

    settings = models.PricingSetting(
        id=1,
        base_visit_fee=DEFAULT_BASE_VISIT_FEE,
        distance_rate_per_km=DEFAULT_DISTANCE_RATE_PER_KM,
        charging_rate_per_kwh=DEFAULT_CHARGING_RATE_PER_KWH,
        platform_fee=DEFAULT_PLATFORM_FEE,
        emergency_fee_limit=0.0,
        night_fee_limit=0.0,
        updated_at=datetime.datetime.utcnow(),
    )
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def settings_payload(settings: models.PricingSetting) -> dict:
    return {
        "base_visit_fee": float(settings.base_visit_fee),
        "distance_rate_per_km": float(settings.distance_rate_per_km),
        "charging_rate_per_kwh": float(settings.charging_rate_per_kwh),
        "platform_fee": float(settings.platform_fee),
        "emergency_fee_limit": float(settings.emergency_fee_limit or 0),
        "night_fee_limit": float(settings.night_fee_limit or 0),
        "updated_at": settings.updated_at,
    }


def calculate_fare_breakdown(
    distance_km: float,
    energy_kwh: float = 0.0,
    emergency_fee: float = 0.0,
    night_fee: float = 0.0,
    settings: models.PricingSetting | None = None,
) -> dict:
    base_visit_fee = float(settings.base_visit_fee if settings else DEFAULT_BASE_VISIT_FEE)
    distance_rate = float(settings.distance_rate_per_km if settings else DEFAULT_DISTANCE_RATE_PER_KM)
    charging_rate = float(settings.charging_rate_per_kwh if settings else DEFAULT_CHARGING_RATE_PER_KWH)
    platform_fee = float(settings.platform_fee if settings else DEFAULT_PLATFORM_FEE)
    emergency_limit = float(settings.emergency_fee_limit if settings else 0)
    night_limit = float(settings.night_fee_limit if settings else 0)

    emergency_fee = min(max(float(emergency_fee or 0), 0), emergency_limit)
    night_fee = min(max(float(night_fee or 0), 0), night_limit)
    distance_km = max(float(distance_km or 0), 0)
    energy_kwh = max(float(energy_kwh or 0), 0)

    distance_charge = round(distance_km * distance_rate, 2)
    charging_cost = round(energy_kwh * charging_rate, 2)
    total_fare = round(base_visit_fee + distance_charge + charging_cost + platform_fee + emergency_fee + night_fee, 2)
    driver_earnings = round(distance_charge + emergency_fee + night_fee, 2)
    runev_earnings = round(base_visit_fee + platform_fee, 2)

    return {
        "base_visit_fee": round(base_visit_fee, 2),
        "distance_rate_per_km": round(distance_rate, 2),
        "charging_rate_per_kwh": round(charging_rate, 2),
        "platform_fee": round(platform_fee, 2),
        "estimated_distance_km": round(distance_km, 2),
        "charged_units_kwh": round(energy_kwh, 2),
        "distance_charge": distance_charge,
        "charging_cost": charging_cost,
        "emergency_fee": round(emergency_fee, 2),
        "night_fee": round(night_fee, 2),
        "total_fare": total_fare,
        "driver_earnings": driver_earnings,
        "runev_earnings": runev_earnings,
        "charging_revenue": charging_cost,
    }


def apply_fare_breakdown(service_request: models.ServiceRequest, breakdown: dict) -> None:
    service_request.estimated_distance_km = breakdown["estimated_distance_km"]
    service_request.base_visit_fee = breakdown["base_visit_fee"]
    service_request.distance_rate_per_km = breakdown["distance_rate_per_km"]
    service_request.charging_rate_per_kwh = breakdown["charging_rate_per_kwh"]
    service_request.platform_fee = breakdown["platform_fee"]
    service_request.distance_charge = breakdown["distance_charge"]
    service_request.charging_cost = breakdown["charging_cost"]
    service_request.emergency_fee = breakdown["emergency_fee"]
    service_request.night_fee = breakdown["night_fee"]
    service_request.driver_earnings = breakdown["driver_earnings"]
    service_request.runev_earnings = breakdown["runev_earnings"]
    service_request.charging_revenue = breakdown["charging_revenue"]
    service_request.total_price = breakdown["total_fare"]


def request_fare_breakdown(service_request: models.ServiceRequest) -> dict:
    return {
        "base_visit_fee": float(service_request.base_visit_fee or 0),
        "distance_rate_per_km": float(service_request.distance_rate_per_km or 0),
        "charging_rate_per_kwh": float(service_request.charging_rate_per_kwh or 0),
        "platform_fee": float(service_request.platform_fee or 0),
        "estimated_distance_km": float(service_request.estimated_distance_km or 0),
        "charged_units_kwh": float(service_request.charged_units_kwh or 0),
        "distance_charge": float(service_request.distance_charge or 0),
        "charging_cost": float(service_request.charging_cost or 0),
        "emergency_fee": float(service_request.emergency_fee or 0),
        "night_fee": float(service_request.night_fee or 0),
        "total_fare": float(service_request.total_price or 0),
        "driver_earnings": float(service_request.driver_earnings or 0),
        "runev_earnings": float(service_request.runev_earnings or 0),
        "charging_revenue": float(service_request.charging_revenue or 0),
    }
