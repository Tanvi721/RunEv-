from backend import models

BASE_SERVICE_FEE = 149.0
PER_KM_FEE = 18.0
DEFAULT_ENERGY_FEE = 20.0


def estimate_service_amount(distance_km: float, provider: models.Provider | None = None, surge_multiplier: float = 1.0) -> float:
    energy_fee = DEFAULT_ENERGY_FEE
    if provider and provider.price_per_kwh:
        energy_fee = float(provider.price_per_kwh)

    subtotal = BASE_SERVICE_FEE + (distance_km * PER_KM_FEE) + energy_fee
    return round(subtotal * max(surge_multiplier, 1.0), 2)


def estimate_surge_multiplier(available_provider_count: int, pending_request_count: int) -> float:
    if available_provider_count <= 0 and pending_request_count > 0:
        return 1.5
    if available_provider_count <= 0:
        return 1.0

    demand_ratio = pending_request_count / available_provider_count
    if demand_ratio >= 3:
        return 1.5
    if demand_ratio >= 2:
        return 1.25
    return 1.0
