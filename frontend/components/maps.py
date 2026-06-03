from __future__ import annotations

import math
from typing import Iterable

import folium
import streamlit as st
from folium import plugins
from streamlit_folium import st_folium

ON_SITE_STATUSES = {"arrived", "charging", "awaiting_payment", "completed"}


def _vehicle_icon(color: str = "#00e5a8") -> folium.DivIcon:
    return folium.DivIcon(
        html=f"""
        <div style="width:34px;height:34px;border-radius:13px;background:{color};display:flex;align-items:center;justify-content:center;
                    box-shadow:0 0 0 8px rgba(0,229,168,.16),0 12px 24px rgba(0,0,0,.35);font-size:18px;">⚡</div>
        """,
        class_name="runev-vehicle-marker",
    )


def _customer_icon() -> folium.DivIcon:
    return folium.DivIcon(
        html="""
        <div style="width:26px;height:26px;border-radius:999px;background:#3b82f6;border:4px solid #dbeafe;
                    box-shadow:0 0 0 10px rgba(59,130,246,.18),0 12px 24px rgba(0,0,0,.32);"></div>
        """,
        class_name="runev-customer-marker",
    )


def _tiles() -> str:
    return "OpenStreetMap"


def _valid_coordinate_pair(lat, lng) -> bool:
    try:
        lat_value = float(lat)
        lng_value = float(lng)
    except (TypeError, ValueError):
        return False
    return (
        math.isfinite(lat_value)
        and math.isfinite(lng_value)
        and -90 <= lat_value <= 90
        and -180 <= lng_value <= 180
    )


def render_user_map(user_lat: float, user_lng: float, providers: Iterable[dict], address: str, key: str = "user_map") -> None:
    if not _valid_coordinate_pair(user_lat, user_lng):
        return
    providers = list(providers or [])
    m = folium.Map(location=[user_lat, user_lng], zoom_start=13, tiles=_tiles(), control_scale=True)
    plugins.Fullscreen(position="topright").add_to(m)
    plugins.LocateControl(auto_start=False).add_to(m)

    folium.Circle([user_lat, user_lng], radius=2500, color="#3b82f6", fill=True, fill_opacity=0.08, weight=1).add_to(m)
    folium.Marker([user_lat, user_lng], popup=folium.Popup(address, max_width=280), tooltip="Pickup location", icon=_customer_icon()).add_to(m)
    bounds = [[user_lat, user_lng]]

    for provider in providers:
        lat = provider.get("current_lat")
        lng = provider.get("current_lng")
        if not _valid_coordinate_pair(lat, lng):
            continue
        available = provider.get("is_available")
        color = "#00e5a8" if available else "#64748b"
        popup = f"""
        <div style="font-family:Inter,sans-serif;min-width:190px">
            <strong>{provider.get('vehicle_number', 'Charging Van')}</strong><br>
            Driver: {provider.get('driver_name') or 'Driver'}<br>
            Status: {'Available' if available else 'Busy'}<br>
            Speed: {provider.get('charging_speed') or 'Standard'}<br>
            Connector: {provider.get('connector_types') or 'Universal'}<br>
            Rate: Rs {provider.get('price_per_kwh') or 20}/kWh
        </div>
        """
        folium.Marker([lat, lng], popup=folium.Popup(popup, max_width=280), tooltip=provider.get("vehicle_number"), icon=_vehicle_icon(color)).add_to(m)
        if provider.get("distance_km") is not None:
            plugins.AntPath([[user_lat, user_lng], [lat, lng]], color="#00e5a8" if available else "#64748b", pulse_color="#3b82f6", weight=3, opacity=0.65).add_to(m)
        bounds.append([lat, lng])

    if len(bounds) > 1:
        m.fit_bounds(bounds, padding=(30, 30))
    st_folium(m, width=None, height=520, key=key)


def render_trip_map(
    pickup_lat: float,
    pickup_lng: float,
    provider: dict | object | None,
    key: str = "trip_map",
    trip_status: str | None = None,
) -> None:
    if not _valid_coordinate_pair(pickup_lat, pickup_lng):
        return
    m = folium.Map(location=[pickup_lat, pickup_lng], zoom_start=14, tiles=_tiles(), control_scale=True)
    folium.Marker([pickup_lat, pickup_lng], tooltip="Customer pickup", icon=_customer_icon()).add_to(m)
    folium.Circle([pickup_lat, pickup_lng], radius=900, color="#3b82f6", fill=True, fill_opacity=0.08, weight=1).add_to(m)
    bounds = [[pickup_lat, pickup_lng]]

    if provider:
        getter = provider.get if isinstance(provider, dict) else lambda name, default=None: getattr(provider, name, default)
        lat = getter("current_lat")
        lng = getter("current_lng")
        if _valid_coordinate_pair(lat, lng):
            vehicle = getter("vehicle_number", "Charging Van")
            is_on_site = trip_status in ON_SITE_STATUSES
            marker_lat = pickup_lat if is_on_site else lat
            marker_lng = pickup_lng if is_on_site else lng
            tooltip = f"{vehicle} at pickup" if is_on_site else vehicle
            folium.Marker([marker_lat, marker_lng], popup=vehicle, tooltip=tooltip, icon=_vehicle_icon()).add_to(m)
            if not is_on_site:
                plugins.AntPath([[pickup_lat, pickup_lng], [lat, lng]], color="#00e5a8", pulse_color="#3b82f6", weight=5, delay=700).add_to(m)
                bounds.append([lat, lng])

    if len(bounds) > 1:
        m.fit_bounds(bounds, padding=(30, 30))
    st_folium(m, width=None, height=460, key=key)


def render_provider_map(provider, requests_list=None, key: str = "provider_map") -> None:
    provider_lat = getattr(provider, "current_lat", None)
    provider_lng = getattr(provider, "current_lng", None)
    provider_address = getattr(provider, "address", "") or ""
    if (
        _valid_coordinate_pair(provider_lat, provider_lng)
        and round(float(provider_lat), 4) == 18.5204
        and round(float(provider_lng), 4) == 73.8567
        and "pune" not in str(provider_address).lower()
    ):
        st.warning("Share Driver Live Location to show the van on the map.")
        return
    lat = float(provider_lat) if _valid_coordinate_pair(provider_lat, provider_lng) else 18.5204
    lng = float(provider_lng) if _valid_coordinate_pair(provider_lat, provider_lng) else 73.8567
    m = folium.Map(location=[lat, lng], zoom_start=13, tiles=_tiles(), control_scale=True)
    plugins.Fullscreen(position="topright").add_to(m)
    folium.Marker([lat, lng], popup=getattr(provider, "address", "") or "Charging van", tooltip="Charging van", icon=_vehicle_icon()).add_to(m)
    folium.Circle([lat, lng], radius=3500, color="#00e5a8", fill=True, fill_opacity=0.06, weight=1).add_to(m)
    bounds = [[lat, lng]]

    for req in requests_list or []:
        pickup_lat = getattr(req, "pickup_lat", None)
        pickup_lng = getattr(req, "pickup_lng", None)
        if not _valid_coordinate_pair(pickup_lat, pickup_lng):
            continue
        status = getattr(req, "status", "pending")
        is_on_site = status in ON_SITE_STATUSES
        folium.Marker([pickup_lat, pickup_lng], tooltip=f"Customer: {status}", icon=_customer_icon()).add_to(m)
        if is_on_site:
            folium.Marker([pickup_lat, pickup_lng], tooltip="Charging van at customer", icon=_vehicle_icon()).add_to(m)
        else:
            plugins.AntPath([[lat, lng], [pickup_lat, pickup_lng]], color="#00e5a8", pulse_color="#3b82f6", weight=4, delay=650).add_to(m)
        bounds.append([pickup_lat, pickup_lng])

    if len(bounds) > 1:
        m.fit_bounds(bounds, padding=(30, 30))
    st_folium(m, width=None, height=460, key=key)
