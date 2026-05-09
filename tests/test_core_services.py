from backend.services.geo_service import calculate_distance, estimate_eta_minutes
from backend.services.pricing_service import estimate_service_amount, estimate_surge_multiplier


def test_calculate_distance_for_same_point_is_zero():
    assert calculate_distance(18.5204, 73.8567, 18.5204, 73.8567) == 0


def test_eta_has_two_minute_floor():
    assert estimate_eta_minutes(0) == 2


def test_pricing_uses_base_distance_and_energy_fee():
    assert estimate_service_amount(10) == 349.0


def test_surge_increases_when_demand_exceeds_supply():
    assert estimate_surge_multiplier(1, 3) == 1.5
