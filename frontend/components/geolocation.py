from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

try:
    from streamlit_geolocation import streamlit_geolocation
except ImportError:  # pragma: no cover - optional runtime component
    streamlit_geolocation = None

_COMPONENT_PATH = Path(__file__).parent / "geolocation_component"
_location_component = components.declare_component("runev_live_geolocation", path=str(_COMPONENT_PATH))


def _query_value(name: str) -> str | None:
    value = st.query_params.get(name)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def validate_coordinates(latitude: Any, longitude: Any, accuracy: Any | None = None) -> tuple[float, float, float]:
    try:
        lat = float(latitude)
        lng = float(longitude)
        acc = float(accuracy) if accuracy not in (None, "") else 0.0
    except (TypeError, ValueError):
        raise ValueError("Location response did not include valid numeric latitude, longitude, and accuracy.")

    if not (math.isfinite(lat) and -90 <= lat <= 90):
        raise ValueError("Location response included an invalid latitude.")
    if not (math.isfinite(lng) and -180 <= lng <= 180):
        raise ValueError("Location response included an invalid longitude.")
    if not (math.isfinite(acc) and acc >= 0):
        raise ValueError("Location response included an invalid accuracy value.")
    return lat, lng, acc


def live_location_button(label: str = "Use My Live Location", key: str | None = None) -> dict[str, Any] | None:
    component_key = key or "runev_location"
    result: dict[str, Any] | None = None

    component_failed = False
    try:
        component_location = _location_component(label=label, key=f"{component_key}_component", default=None)
    except Exception:
        component_failed = True
        component_location = None

    if isinstance(component_location, dict):
        if component_location.get("error"):
            return {"error": str(component_location["error"]), "timestamp": str(component_location.get("timestamp") or time.time())}
        latitude = component_location.get("latitude")
        longitude = component_location.get("longitude")
        if latitude is not None and longitude is not None:
            try:
                lat, lng, accuracy = validate_coordinates(latitude, longitude, component_location.get("accuracy"))
                return {
                    "latitude": lat,
                    "longitude": lng,
                    "accuracy": accuracy,
                    "timestamp": str(component_location.get("timestamp") or time.time()),
                }
            except ValueError as exc:
                return {"error": str(exc), "timestamp": str(component_location.get("timestamp") or time.time())}

    if component_location is None and not component_failed:
        return None

    if streamlit_geolocation is not None:
        native_location = streamlit_geolocation()
        if isinstance(native_location, dict):
            latitude = native_location.get("latitude")
            longitude = native_location.get("longitude")
            if latitude is not None and longitude is not None:
                try:
                    lat, lng, accuracy = validate_coordinates(latitude, longitude, native_location.get("accuracy"))
                    return {
                        "latitude": lat,
                        "longitude": lng,
                        "accuracy": accuracy,
                        "timestamp": str(time.time()),
                    }
                except ValueError as exc:
                    result = {"error": str(exc), "timestamp": str(time.time())}

    if _query_value("runev_geo_key") == component_key:
        error = _query_value("runev_geo_error")
        if error:
            result = {"error": error, "timestamp": _query_value("runev_geo_ts") or str(time.time())}
        else:
            latitude = _query_value("runev_geo_lat")
            longitude = _query_value("runev_geo_lng")
            if latitude is not None and longitude is not None:
                address = _query_value("runev_geo_address")
                try:
                    lat, lng, accuracy = validate_coordinates(latitude, longitude, _query_value("runev_geo_accuracy"))
                    result = {
                        "latitude": lat,
                        "longitude": lng,
                        "accuracy": accuracy,
                        "address": address,
                        "timestamp": _query_value("runev_geo_ts") or str(time.time()),
                    }
                except ValueError as exc:
                    result = {"error": str(exc), "timestamp": _query_value("runev_geo_ts") or str(time.time())}

    components.html(
        f"""
        <button id="runev-location-button" type="button">{label}</button>
        <script>
            const button = document.getElementById("runev-location-button");
            const key = {json.dumps(component_key)};
            const geolocationOptions = {{ enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }};

            function explainGeoError(error) {{
                if (!error) {{
                    return "Could not fetch location. Check browser location permission and device location services.";
                }}
                if (error.code === 1) {{
                    return "Location permission was denied or blocked. Allow location access for this site in browser settings, then try again.";
                }}
                if (error.code === 2) {{
                    return "Your device could not determine GPS location. Turn on device location services and try again.";
                }}
                if (error.code === 3) {{
                    return "Location request timed out. Turn on GPS/location services and try again.";
                }}
                return error.message || "Could not fetch location.";
            }}

            function invalidCoordinateMessage(coords) {{
                const latitude = Number(coords && coords.latitude);
                const longitude = Number(coords && coords.longitude);
                const accuracy = Number(coords && coords.accuracy);
                if (!Number.isFinite(latitude) || latitude < -90 || latitude > 90) {{
                    return "Location response included an invalid latitude.";
                }}
                if (!Number.isFinite(longitude) || longitude < -180 || longitude > 180) {{
                    return "Location response included an invalid longitude.";
                }}
                if (!Number.isFinite(accuracy) || accuracy < 0) {{
                    return "Location response included an invalid accuracy value.";
                }}
                return "";
            }}

            button.addEventListener("click", () => {{
                let geolocation = null;
                try {{
                    geolocation = window.parent.navigator && window.parent.navigator.geolocation;
                }} catch (_) {{}}
                geolocation = geolocation || navigator.geolocation;
                if (!geolocation) {{
                    writeLocationParams({{runev_geo_error: "Location is not supported in this browser."}});
                    return;
                }}
                button.disabled = true;
                const originalLabel = button.textContent;
                button.textContent = "Requesting permission...";
                let finished = false;
                const finish = (values) => {{
                    if (finished) {{
                        return;
                    }}
                    finished = true;
                    window.clearTimeout(stuckTimer);
                    writeLocationParams(values);
                }};
                if (navigator.permissions && navigator.permissions.query) {{
                    navigator.permissions.query({{ name: "geolocation" }}).then((status) => {{
                        if (!finished) {{
                            button.textContent = status.state === "prompt" ? "Waiting for permission..." : "Getting location...";
                        }}
                    }}).catch(() => {{
                        if (!finished) {{
                            button.textContent = "Getting location...";
                        }}
                    }});
                }} else {{
                    button.textContent = "Getting location...";
                }}
                const stuckTimer = window.setTimeout(() => {{
                    finish({{runev_geo_error: "Location took too long. Check browser permission and device location services, then try again."}});
                }}, 17000);
                geolocation.getCurrentPosition(
                    (position) => {{
                        const validationError = invalidCoordinateMessage(position.coords);
                        if (validationError) {{
                            finish({{runev_geo_error: validationError}});
                            return;
                        }}
                        finish({{
                            runev_geo_lat: position.coords.latitude,
                            runev_geo_lng: position.coords.longitude,
                            runev_geo_accuracy: position.coords.accuracy
                        }});
                    }},
                    (error) => {{
                        finish({{runev_geo_error: explainGeoError(error)}});
                    }},
                    geolocationOptions
                );
            }});

            function writeLocationParams(values) {{
                try {{
                    const url = new URL(window.parent.location.href);
                    ["runev_geo_error", "runev_geo_lat", "runev_geo_lng", "runev_geo_accuracy", "runev_geo_address"].forEach((name) => {{
                        url.searchParams.delete(name);
                    }});
                    url.searchParams.set("runev_geo_key", key);
                    url.searchParams.set("runev_geo_ts", Date.now().toString());
                    Object.entries(values).forEach(([name, value]) => {{
                        url.searchParams.set(name, value);
                    }});
                    window.parent.location.replace(url.toString());
                }} catch (error) {{
                    button.disabled = false;
                    button.textContent = "Use My Live Location";
                }}
            }}
        </script>
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                background: transparent;
                overflow: hidden;
            }}
            #runev-location-button {{
                width: auto;
                min-width: 180px;
                min-height: 42px;
                border: 1px solid rgba(20, 230, 176, 0.45);
                border-radius: 10px;
                background: rgba(20, 230, 176, 0.14);
                color: #f8fafc;
                cursor: pointer;
                font: 750 14px/1.2 Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}
            #runev-location-button:disabled {{
                cursor: wait;
                opacity: 0.72;
            }}
        </style>
        """,
        height=48,
    )
    return result
