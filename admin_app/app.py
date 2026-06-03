from __future__ import annotations

import base64
import math
import os
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from types import SimpleNamespace

import requests
import textwrap
import streamlit as st
import streamlit.components.v1 as components
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import Base, SessionLocal, engine, ensure_auth_security_columns, ensure_pricing_columns
from backend.models import Provider, ServiceRequest, User
from backend.services.dispatch_service import ACTIVE_TRIP_STATUSES
from frontend.components.analytics import render_operations_analytics
from frontend.components.theme import (
    apply_theme_runtime,
    init_theme_state,
    persist_theme_preference,
    render_theme_selector,
    restore_theme_preferences,
)
from frontend.components.maps import render_provider_map
from frontend.components.geolocation import live_location_button, validate_coordinates
from frontend.components.ui import hero, metric_card, money, safe_text, status_badge, timeline
from frontend.styles.theme import configure_page, inject_global_styles
from frontend.utils.live import auto_refresh, push_notification, render_live_notification, toast_for_status
from utils import api_client
from backend.services.pricing_service import calculate_fare_breakdown, get_pricing_settings, request_fare_breakdown, settings_payload
from backend.core.validation import (
    normalize_email,
    normalize_indian_mobile,
    normalize_vehicle_number,
    password_strength,
    validate_full_name,
    validate_password,
    validate_file_upload,
)


def clean_html(html_str: str) -> str:
    import re
    no_comments = re.sub(r"<!--.*?-->", "", html_str, flags=re.DOTALL)
    return " ".join(no_comments.split())


def inject_driver_styles() -> None:
    styles = """
    <style>
    /* Reset Streamlit's default input wrapper background */
    .block-container:has(.runev-driver-dashboard-landing) div[data-baseweb="input"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Reset eye toggle button background */
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #cbd5e1 !important;
        width: auto !important;
        min-height: unset !important;
        padding: 0 8px !important;
        transform: none !important;
        margin: 0 !important;
    }
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] button:hover {
        color: #FFFFFF !important;
    }
    
    /* Add padding and icons to text inputs */
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] input {
        padding-left: 42px !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"]:has(input[placeholder*="email"]) input,
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"]:has(input[placeholder*="Email"]) input {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="%23475569" viewBox="0 0 16 16"><path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1H2zm13 2.383-4.758 2.855L15 11.114v-5.73zm-.03 6.862L10.27 8.138 8 9.5 5.73 8.138 1.03 12.245A1 1 0 0 0 2 13h12a1 1 0 0 0 .97-.755zM1 11.114l4.758-2.876L1 5.383v5.73z"/></svg>') !important;
        background-repeat: no-repeat !important;
        background-position: 15px center !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"]:has(input[type="password"]) input {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="%23475569" viewBox="0 0 16 16"><path d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z"/></svg>') !important;
        background-repeat: no-repeat !important;
        background-position: 15px center !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"]:has(input[placeholder*="Name"]) input,
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"]:has(input[placeholder*="name"]) input,
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"]:has(input[placeholder*="operator"]) input {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="%23475569" viewBox="0 0 16 16"><path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"/></svg>') !important;
        background-repeat: no-repeat !important;
        background-position: 15px center !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"]:has(input[placeholder*="phone"]) input,
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"]:has(input[placeholder*="Mobile"]) input {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="%23475569" viewBox="0 0 16 16"><path d="M3.654 1.328a.678.678 0 0 0-1.015-.063L1.605 2.3c-.483.484-.661 1.169-.45 1.77a17.6 17.6 0 0 0 4.168 6.608 17.6 17.6 0 0 0 6.608 4.168c.601.211 1.286.033 1.77-.45l1.034-1.034a.678.678 0 0 0-.063-1.015l-2.307-1.794a.68.68 0 0 0-.58-.122l-2.19.547a1.75 1.75 0 0 1-1.657-.459L5.482 8.062a1.75 1.75 0 0 1-.46-1.657l.548-2.19a.68.68 0 0 0-.122-.58z"/></svg>') !important;
        background-repeat: no-repeat !important;
        background-position: 15px center !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"]:has(input[placeholder*="Vehicle"]) input,
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"]:has(input[placeholder*="vehicle"]) input {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="%23475569" viewBox="0 0 16 16"><path d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2zm4 4a1 1 0 1 0 0-2 1 1 0 0 0 0 2m7-1a1 1 0 1 0 2 0 1 1 0 0 0-2 0M4 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2m7-1a1 1 0 1 0 2 0 1 1 0 0 0-2 0M9 7a1 1 0 1 0 0-2 1 1 0 0 0 0 2m0 3a1 1 0 1 0 0-2 1 1 0 0 0 0 2M7 8a1 1 0 1 0 0-2 1 1 0 0 0 0 2"/></svg>') !important;
        background-repeat: no-repeat !important;
        background-position: 15px center !important;
    }
    
    /* Hide input labels */
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] label,
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] [data-testid="stWidgetLabel"] {
        display: none !important;
    }
    
    /* Style tabs typography and color */
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [role="tablist"] button p,
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [role="tablist"] button span,
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [role="tablist"] button {
        color: #cbd5e1 !important;
    }
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [role="tablist"] button[aria-selected="true"] p,
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [role="tablist"] button[aria-selected="true"] span,
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [role="tablist"] button[aria-selected="true"] {
        color: #14e6b0 !important;
    }
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [role="tablist"] button:hover p,
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [role="tablist"] button:hover span,
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [role="tablist"] button:hover {
        color: #ffffff !important;
    }
    </style>
    """
    st.markdown(styles, unsafe_allow_html=True)


configure_page("RunEV - Driver Console", "🚐")
inject_global_styles()
inject_driver_styles()
init_theme_state()
apply_theme_runtime()

VISIBLE_ACTIVE_TRIP_STATUSES = tuple(status for status in ACTIVE_TRIP_STATUSES if status != "pending")
DEFAULT_PROVIDER_LOCATION = (18.5204, 73.8567)
RUNEV_DRIVER_SESSION_STORAGE_KEY = "runev.driver.jwt"
LOCAL_TIMEZONE = ZoneInfo("Asia/Kolkata")


def is_default_provider_location(latitude: float | None, longitude: float | None) -> bool:
    if latitude is None or longitude is None:
        return True
    try:
        return (
            round(float(latitude), 4) == DEFAULT_PROVIDER_LOCATION[0]
            and round(float(longitude), 4) == DEFAULT_PROVIDER_LOCATION[1]
        )
    except (TypeError, ValueError):
        return True


def address_matches_default_location(address: str | None) -> bool:
    return "pune" in str(address or "").lower()


@st.cache_resource
def ensure_database_schema() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_auth_security_columns()
    ensure_pricing_columns()


def init_state() -> None:
    defaults = {
        "user": None,
        "jwt_token": None,
        "show_add_provider_form": False,
        "provider_lat": 18.5204,
        "provider_lng": 73.8567,
        "provider_address": "Detecting van live location",
        "selected_driver_map_request_id": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def object_from_dict(data):
    if isinstance(data, dict):
        return SimpleNamespace(**{key: object_from_dict(value) for key, value in data.items()})
    if isinstance(data, list):
        return [object_from_dict(value) for value in data]
    return data


def reverse_geocode(lat: float, lng: float, fallback: str = "Live location captured") -> str:
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"format": "jsonv2", "lat": lat, "lon": lng},
            headers={"User-Agent": "RunEV local development app"},
            timeout=5,
        )
        if response.status_code == 200:
            return response.json().get("display_name") or fallback
    except requests.RequestException:
        pass
    return fallback


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return radius * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def estimate_eta_minutes(distance_km: float | None) -> int:
    return max(2, round(((distance_km or 0) / 25.0) * 60))


def object_time(row) -> datetime:
    value = getattr(row, "request_time", None)
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.utcnow()
    return datetime.utcnow()


def format_local_time(value: datetime | str | None) -> str:
    if not value:
        return "Recent"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(LOCAL_TIMEZONE).strftime("%d %b, %I:%M %p")
    except ValueError:
        return str(value)


def load_pending_requests_from_api() -> list:
    try:
        rows = api_client.request_json("GET", "/api/v1/requests/provider", token=st.session_state.get("jwt_token")) or []
    except api_client.ApiError as exc:
        st.error(str(exc))
        return []

    requests_list = []
    for row in rows:
        row["request_time"] = object_time(object_from_dict(row))
        requests_list.append(object_from_dict(row))
    return requests_list


def update_request_status(request_id: int, action: str) -> None:
    try:
        api_client.request_json("POST", f"/api/v1/requests/charge/{request_id}/{action}", token=st.session_state.get("jwt_token"))
        action_labels = {
            "accept": "Trip accepted",
            "reject": "Trip declined",
            "arrived": "Driver marked reached",
            "start-charging": "Charging started",
        }
        push_notification(action_labels.get(action, "Trip updated"), "success")
        st.rerun()
    except api_client.ApiError as exc:
        st.error(str(exc))


def start_charging_with_otp(request_id: int, otp_code: str) -> None:
    try:
        api_client.request_json(
            "POST",
            f"/api/v1/requests/charge/{request_id}/start-charging",
            token=st.session_state.get("jwt_token"),
            json={"otp_code": otp_code.strip()},
        )
        push_notification("OTP verified. Charging started", "success")
        st.rerun()
    except api_client.ApiError as exc:
        st.error(str(exc))


def submit_charged_units(request_id: int, charged_units_kwh: float, emergency_fee: float = 0.0, night_fee: float = 0.0) -> None:
    try:
        api_client.request_json(
            "POST",
            f"/api/v1/requests/charge/{request_id}/units",
            token=st.session_state.get("jwt_token"),
            json={
                "charged_units_kwh": charged_units_kwh,
                "emergency_fee": emergency_fee,
                "night_fee": night_fee,
            },
        )
        push_notification("Charging complete. Bill sent to customer", "success")
        st.rerun()
    except api_client.ApiError as exc:
        st.error(str(exc))


def route_distance_and_eta(provider: Provider | None, request: ServiceRequest | SimpleNamespace) -> tuple[float | None, int | None]:
    if not provider or provider.current_lat is None or provider.current_lng is None:
        return None, None
    distance = calculate_distance(request.pickup_lat, request.pickup_lng, provider.current_lat, provider.current_lng)
    return distance, estimate_eta_minutes(distance)


def estimate_service_amount(request: ServiceRequest | SimpleNamespace, provider: Provider | None) -> float:
    total = getattr(request, "total_price", None)
    if total:
        return float(total)
    distance, _ = route_distance_and_eta(provider, request)
    return calculate_fare_breakdown(float(distance or 0))["total_fare"]


def provider_rating_stats(provider: Provider | SimpleNamespace | None) -> tuple[float | None, int]:
    if not provider:
        return None, 0
    ratings = getattr(provider, "ratings", None) or []
    count = len(ratings)
    if count == 0:
        return None, 0
    average = sum(float(rating.score) for rating in ratings) / count
    return average, count


def provider_rating_label(provider: Provider | SimpleNamespace | None) -> str:
    average, count = provider_rating_stats(provider)
    if average is None:
        return "No ratings yet"
    return f"{average:.1f}/5 from {count} rating{'s' if count != 1 else ''}"


def render_provider_rating_card(provider: Provider | SimpleNamespace | None) -> None:
    average, count = provider_rating_stats(provider)
    score = average or 0
    filled_stars = int(round(score))
    empty_stars = max(0, 5 - filled_stars)
    stars = "".join('<span class="filled">&#9733;</span>' for _ in range(filled_stars))
    stars += "".join('<span>&#9733;</span>' for _ in range(empty_stars))
    score_text = "New" if average is None else f"{average:.1f}"
    review_text = "No ratings yet" if count == 0 else f"{count} verified rating{'s' if count != 1 else ''}"
    signal = "New van" if average is None else "Excellent" if average >= 4.5 else "Trusted" if average >= 4 else "Rated"
    percent = min(100, max(0, (score / 5) * 100))
    st.markdown(
        textwrap.dedent(f"""
        <div class="runev-rating-card">
            <div class="runev-rating-head">
                <span>Van Rating</span>
                <b>{safe_text(signal)}</b>
            </div>
            <div class="runev-rating-body">
                <strong>{safe_text(score_text)}</strong>
                <div>
                    <div class="runev-stars">{stars}</div>
                    <p>{safe_text(review_text)}</p>
                </div>
            </div>
            <div class="runev-rating-track"><span style="width:{percent:.0f}%"></span></div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def ensure_provider_role(db, provider: Provider | None) -> None:
    if not provider or st.session_state.user.get("role") in ("provider", "admin"):
        return
    user = db.query(User).filter(User.id == st.session_state.user["id"]).first()
    if user and user.role != "provider":
        user.role = "provider"
        db.commit()
    st.session_state.user["role"] = "provider"


def complete_login(token: str) -> None:
    user = api_client.me(token)
    st.session_state.user = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "phone": user.get("phone"),
    }
    st.session_state.jwt_token = token
    persist_driver_session(token)
    st.session_state.show_add_provider_form = user["role"] == "provider"
    restore_theme_preferences(token)
    st.rerun()


def persist_driver_session(token: str | None = None) -> None:
    token = token or st.session_state.get("jwt_token")
    if not token:
        return
    components.html(
        f"""
        <script>
        try {{ window.parent.localStorage.setItem({RUNEV_DRIVER_SESSION_STORAGE_KEY!r}, {str(token)!r}); }} catch (_) {{}}
        </script>
        """,
        height=0,
        width=0,
    )


def recover_driver_session() -> None:
    query_token = st.query_params.get("runev_driver_token")
    if isinstance(query_token, list):
        query_token = query_token[0]
    if query_token:
        try:
            st.query_params.clear()
            complete_login(str(query_token))
        except api_client.ApiError:
            clear_driver_session()
        return
    components.html(
        f"""
        <script>
        (() => {{
            const url = new URL(window.parent.location.href);
            if (url.searchParams.has("runev_driver_token")) return;
            let token = "";
            try {{ token = window.parent.localStorage.getItem({RUNEV_DRIVER_SESSION_STORAGE_KEY!r}) || ""; }} catch (_) {{}}
            if (token) {{
                url.searchParams.set("runev_driver_token", token);
                window.parent.location.replace(url.toString());
            }}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def clear_driver_session() -> None:
    st.session_state.user = None
    st.session_state.jwt_token = None
    components.html(
        f"""
        <script>
        try {{ window.parent.localStorage.removeItem({RUNEV_DRIVER_SESSION_STORAGE_KEY!r}); }} catch (_) {{}}
        </script>
        """,
        height=0,
        width=0,
    )


def render_driver_auth_header(mode: str) -> None:
    copy = {
        "login": ("Fleet access", "Sign in to Driver Console", "Use your registered fleet email and password."),
        "register": ("New operator", "Register Fleet", "Create a fleet account and add your first charging van."),
        "forgot": ("Account recovery", "Forgot Password", "Request help recovering access to your fleet account."),
    }
    eyebrow, title, subtitle = copy.get(mode, copy["login"])
    st.markdown(
        textwrap.dedent(f"""
        <div class="runev-driver-auth-copy">
            <span>{safe_text(eyebrow)}</span>
            <h2>{safe_text(title)}</h2>
            <p>{safe_text(subtitle)}</p>
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_driver_login_form() -> None:
    with st.form("driver_password_login_form"):
        email = st.text_input("Email Address", key="driver_login_email", placeholder="operator@runev.com")
        password = st.text_input("Password", key="driver_login_password", type="password", placeholder="Enter your password")
        if st.form_submit_button("Launch Fleet Console", use_container_width=True):
            try:
                normalized_email = normalize_email(email)
                if not password:
                    raise ValueError("Enter your password.")
                token_data = api_client.login(normalized_email, password)
                complete_login(token_data["access_token"])
            except (ValueError, api_client.ApiError) as exc:
                st.error(str(exc))

    if st.button("Forgot Password", use_container_width=True, type="secondary"):
        st.session_state.driver_auth_mode = "forgot"
        st.rerun()

    st.markdown(
        textwrap.dedent("""
        <div style="text-align: center; margin-top: 14px; font-size: 14px; color: #cbd5e1;">
            Need fleet access? Select the <span style="color: #00E5B3; font-weight: 600;">Registration</span> tab.
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_driver_register_form() -> None:
    with st.form("driver_signup_form"):
        username = st.text_input("Driver Name", key="driver_register_name", placeholder="Enter operator name")
        email = st.text_input("Email Address", key="driver_register_email", placeholder="Enter email ID")
        phone = st.text_input("Mobile Number", key="driver_register_phone", placeholder="Enter mobile number")
        password = st.text_input("Password", key="driver_register_password", type="password", placeholder="Minimum 8 characters")
        confirm_password = st.text_input("Confirm Password", key="driver_register_confirm", type="password", placeholder="Confirm password")
        vehicle_number = st.text_input("Vehicle Number", key="driver_register_vehicle", placeholder="Enter vehicle number")
        if password:
            st.caption(f"Password strength: {password_strength(password)}")
        if st.form_submit_button("Create Fleet Account", use_container_width=True):
            try:
                normalized_name = validate_full_name(username, "Driver name")
                normalized_email = normalize_email(email)
                normalized_phone = normalize_indian_mobile(phone)
                normalized_vehicle = normalize_vehicle_number(vehicle_number)
                validate_password(password)
                if password != confirm_password:
                    raise ValueError("Confirm password must match password.")
                api_client.register(
                    normalized_name,
                    normalized_email,
                    password,
                    role="provider",
                    vehicle_number=normalized_vehicle,
                    phone=normalized_phone,
                    confirm_password=confirm_password,
                )
                st.session_state.driver_auth_mode = "login"
                st.success("Fleet account created. Sign in with your email and password.")
            except (ValueError, api_client.ApiError) as exc:
                st.error(str(exc))
    if st.button("Back to Sign In", use_container_width=True):
        st.session_state.driver_auth_mode = "login"
        st.rerun()

    st.markdown(
        textwrap.dedent("""
        <div style="text-align: center; margin-top: 14px; font-size: 14px; color: #cbd5e1;">
            Already have an account? Select the <span style="color: #00E5B3; font-weight: 600;">Login</span> tab.
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_driver_forgot_password() -> None:
    with st.form("driver_forgot_password_form"):
        email = st.text_input("Email Address", key="driver_forgot_email", placeholder="operator@runev.com")
        new_password = st.text_input("New Password", key="driver_reset_password", type="password", placeholder="Minimum 8 characters")
        confirm_password = st.text_input("Confirm Password", key="driver_reset_confirm", type="password", placeholder="Re-enter password")
        if new_password:
            st.caption(f"Password strength: {password_strength(new_password)}")
        if st.form_submit_button("Request Reset", use_container_width=True):
            try:
                normalized_email = normalize_email(email)
                validate_password(new_password)
                if new_password != confirm_password:
                    raise ValueError("Passwords do not match.")
                result = api_client.reset_password(normalized_email, new_password)
                st.success(result.get("message", "Password reset link sent."))
                st.session_state.driver_auth_mode = "login"
            except (ValueError, api_client.ApiError) as exc:
                st.error(str(exc))
    if st.button("Back to Sign In", use_container_width=True, key="driver_forgot_back"):
        st.session_state.driver_auth_mode = "login"
        st.rerun()


def save_provider_location_to_db(
    db,
    provider: Provider,
    latitude: float,
    longitude: float,
    address: str,
) -> None:
    provider.current_lat = latitude
    provider.current_lng = longitude
    provider.address = address
    db.commit()
    db.refresh(provider)


def repair_default_provider_location(db, provider: Provider | None) -> None:
    if not provider or not is_default_provider_location(provider.current_lat, provider.current_lng):
        return
    if address_matches_default_location(provider.address):
        return
    address = (provider.address or "").strip()
    if not address:
        return
    nearby_match = (
        db.query(Provider)
        .filter(
            Provider.id != provider.id,
            Provider.address == address,
            Provider.current_lat.isnot(None),
            Provider.current_lng.isnot(None),
        )
        .first()
    )
    if not nearby_match or is_default_provider_location(nearby_match.current_lat, nearby_match.current_lng):
        return
    provider.current_lat = nearby_match.current_lat
    provider.current_lng = nearby_match.current_lng
    db.commit()
    db.refresh(provider)


def capture_provider_location(provider: Provider | None = None, key_suffix: str = "default", db=None) -> str:
    if db is not None and provider is not None:
        repair_default_provider_location(db, provider)
    if provider and provider.current_lat is not None and provider.current_lng is not None:
        try:
            st.session_state.provider_lat, st.session_state.provider_lng, _ = validate_coordinates(
                provider.current_lat,
                provider.current_lng,
            )
        except ValueError:
            pass
    if provider and provider.address:
        st.session_state.provider_address = provider.address

    address_key = f"provider_address_{key_suffix}"
    if address_key not in st.session_state:
        st.session_state[address_key] = provider.address if provider and provider.address else st.session_state.provider_address

    address = st.session_state.get(address_key, st.session_state.provider_address)
    st.session_state.provider_address = st.text_input("Van live address", key=address_key)

    capture_key = f"capture_provider_location_{key_suffix}"
    location = live_location_button("Share Driver Live Location", key=capture_key)
    if location:
        if location.get("error"):
            st.warning(str(location["error"]))
        else:
            try:
                latitude, longitude, accuracy = validate_coordinates(
                    location.get("latitude"),
                    location.get("longitude"),
                    location.get("accuracy"),
                )
            except ValueError as exc:
                st.warning(str(exc))
            else:
                location_key = f"{capture_key}:{latitude}:{longitude}:{accuracy}:{location.get('timestamp')}"
                if st.session_state.get(f"{capture_key}_last_location_key") != location_key:
                    st.session_state[f"{capture_key}_last_location_key"] = location_key
                    st.session_state.provider_lat = latitude
                    st.session_state.provider_lng = longitude
                    fallback_address = f"Live van location: {latitude:.6f}, {longitude:.6f}"
                    st.session_state.provider_address = reverse_geocode(latitude, longitude, fallback_address)
                    st.session_state.provider_location_accuracy = accuracy
                    if provider:
                        if db is not None:
                            try:
                                save_provider_location_to_db(
                                    db,
                                    provider,
                                    latitude,
                                    longitude,
                                    st.session_state.provider_address,
                                )
                            except SQLAlchemyError as exc:
                                db.rollback()
                                st.warning(f"Location was captured but could not be saved locally: {exc}")
                        try:
                            api_client.request_json(
                                "PUT",
                                "/api/v1/tracking/provider/location",
                                token=st.session_state.get("jwt_token"),
                                json={
                                    "provider_id": provider.id,
                                    "current_lat": latitude,
                                    "current_lng": longitude,
                                    "address": st.session_state.provider_address,
                                },
                            )
                            push_notification("Live van location updated", "success")
                            st.rerun()
                        except api_client.ApiError as exc:
                            if db is None:
                                st.warning(f"Location was captured but could not be saved: {exc}")
                            else:
                                push_notification("Live van location updated", "success")
                                st.rerun()
                    else:
                        push_notification("Live van location updated", "success")
                        st.rerun()

    if st.session_state.get("provider_location_accuracy"):
        st.caption(
            f"Captured coordinates: {st.session_state.provider_lat:.6f}, "
            f"{st.session_state.provider_lng:.6f}"
            f" (accuracy {float(st.session_state.provider_location_accuracy):.0f} m)"
        )
    elif provider and provider.current_lat is not None and provider.current_lng is not None:
        st.caption(
            f"Saved van coordinates: {float(provider.current_lat):.6f}, "
            f"{float(provider.current_lng):.6f}"
        )
    return st.session_state.provider_address


def render_login() -> None:
    recover_driver_session()
    st.session_state.setdefault("driver_auth_mode", "login")
    st.markdown('<div class="runev-driver-dashboard-landing"></div>', unsafe_allow_html=True)
    
    landing_css = """
    <style>
    .stApp:has(.runev-driver-dashboard-landing),
    body:has(.runev-driver-dashboard-landing) {
        background:
            radial-gradient(circle at 12% 12%, rgba(0, 229, 168, 0.14), transparent 28rem),
            linear-gradient(135deg, #0b1220 0%, #111827 52%, #172033 100%) !important;
        color: #f8fafc !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) [data-testid="column"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        gap: 0.5rem !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) {
        max-width: 100% !important;
        height: auto !important;
        min-height: 100vh !important;
        max-height: none !important;
        overflow-y: auto !important;
        padding: 1rem 1.5rem !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        gap: 0.5rem !important;
        box-sizing: border-box !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) [data-testid="stHorizontalBlock"] {
        width: 100% !important;
        max-width: 100% !important;
        margin: 14px 0 0 0 !important;
        padding: 0 !important;
    }

    .runev-fleet-hero-banner {
        width: 100% !important;
        background: linear-gradient(90deg, rgba(8, 20, 31, 0.95), rgba(15, 23, 42, 0.95)) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 0.35rem 1rem !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        box-sizing: border-box !important;
        margin-bottom: 12px !important;
    }
    .runev-fleet-hero-banner .banner-logo {
        font-size: 15px !important;
        font-weight: 800 !important;
        color: #14e6b0 !important;
        letter-spacing: 0.5px !important;
    }
    .runev-fleet-hero-banner .banner-divider {
        color: rgba(255, 255, 255, 0.2) !important;
        margin: 0 8px !important;
    }
    .runev-fleet-hero-banner .banner-subtitle {
        font-size: 11px !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
    }
    .runev-fleet-hero-banner .banner-status {
        font-size: 12px !important;
        color: #94a3b8 !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.4rem !important;
    }
    .runev-fleet-hero-banner .status-dot {
        width: 6px !important;
        height: 6px !important;
        background-color: #10b981 !important;
        border-radius: 50% !important;
        box-shadow: 0 0 8px #10b981 !important;
    }

    .runev-fleet-label {
        font-size: 10px !important;
        font-weight: 700 !important;
        color: #14e6b0 !important;
        letter-spacing: 1.5px !important;
        margin-top: 10px !important;
        margin-bottom: 0.1rem !important;
    }
    h1.runev-fleet-main-heading {
        font-size: 28px !important;
        font-weight: 900 !important;
        line-height: 1.1 !important;
        color: #FFFFFF !important;
        margin: 0 0 2px 0 !important;
        letter-spacing: -0.5px !important;
        background: none !important;
        -webkit-background-clip: unset !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    p.runev-fleet-subheading {
        font-size: 13.5px !important;
        color: #E2E8F0 !important;
        line-height: 1.4 !important;
        margin-bottom: 0.8rem !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .stTabs {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 0.75rem 1.25rem !important;
        width: 100% !important;
        max-width: 520px !important;
        box-sizing: border-box !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.25rem !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(20px) !important;
        max-height: none !important;
        overflow: visible !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [data-testid="stTabBar"] {
        margin-bottom: 0.4rem !important;
        gap: 0.5rem !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [data-testid="stTabBar"] button {
        padding: 4px 8px !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) [data-testid="stForm"] {
        padding: 0 !important;
        background: transparent !important;
        border: none !important;
        gap: 0 !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) [data-testid="stForm"] [data-testid="element-container"] {
        margin-bottom: 6px !important;
        margin-top: 0 !important;
    }

    /* Fixed input visibility and height (48px) */
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] div[data-baseweb="input"],
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background-color: #1A2238 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        height: 48px !important;
        transition: all 0.2s !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] div[data-baseweb="input"]:hover,
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] div[data-baseweb="base-input"]:hover {
        border-color: rgba(255, 255, 255, 0.22) !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within {
        border-color: #00E5B3 !important;
        box-shadow: 0 0 10px rgba(0, 229, 179, 0.3) !important;
        background-color: #1A2238 !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 14px !important;
        height: 48px !important;
        padding: 4px 10px 4px 42px !important;
        line-height: 48px !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stTextInput"] input::placeholder {
        color: rgba(255, 255, 255, 0.65) !important;
        -webkit-text-fill-color: rgba(255, 255, 255, 0.65) !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .stButton > button,
    .block-container:has(.runev-driver-dashboard-landing) .stFormSubmitButton > button {
        height: 44px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        padding: 4px 12px !important;
        margin-top: 0.2rem !important;
        background: linear-gradient(90deg, #00E5A8 0%, #3B82F6 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0, 229, 168, 0.2) !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) .stButton > button:hover,
    .block-container:has(.runev-driver-dashboard-landing) .stFormSubmitButton > button:hover {
        background: linear-gradient(90deg, #00c48f 0%, #2563eb 100%) !important;
        box-shadow: 0 6px 20px rgba(0, 229, 168, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Footer Thin Strip Style */
    .runev-fleet-footer {
        width: 100% !important;
        background: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 0.5rem 1.5rem !important;
        margin-top: 0.5rem !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-sizing: border-box !important;
        border-radius: 8px !important;
    }
    .runev-fleet-footer .footer-content {
        display: flex !important;
        align-items: center !important;
        gap: 1.5rem !important;
    }
    .runev-fleet-footer .footer-label {
        font-size: 11px !important;
        font-weight: 700 !important;
        color: #94a3b8 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    .runev-fleet-footer .footer-item {
        font-size: 13px !important;
        color: #cbd5e1 !important;
    }
    .runev-fleet-footer .footer-num {
        color: #14e6b0 !important;
        font-weight: 700 !important;
    }
    .runev-fleet-footer .footer-divider {
        color: rgba(255, 255, 255, 0.15) !important;
    }
    
    .right-panel-header {
        display: flex !important;
        flex-direction: column !important;
        gap: 4px !important;
        margin-bottom: 12px !important;
        margin-top: 36px !important;
    }
    .preview-eyebrow {
        font-size: 11px !important;
        font-weight: 700 !important;
        color: #14e6b0 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        line-height: 1.2 !important;
    }

    /* Style for static EV Fleet Image */
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stImage"] {
        max-height: 250px !important;
        height: 250px !important;
        width: 100% !important;
        max-width: 100% !important;
        overflow: hidden !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
        margin-bottom: 0.5rem !important;
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        padding: 2px !important;
        box-sizing: border-box !important;
    }
    .block-container:has(.runev-driver-dashboard-landing) div[data-testid="stImage"] img {
        max-height: 246px !important;
        height: 246px !important;
        width: 100% !important;
        object-fit: cover !important;
        border-radius: 14px !important;
    }

    /* 2x2 Metric Grid & Metric Cards like User App */
    .fleet-metrics-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 10px !important;
        width: 100% !important;
        margin-top: 0.5rem !important;
    }
    .fleet-metric-card {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 10px 12px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        height: 82px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        box-sizing: border-box !important;
        transition: all 0.3s !important;
    }
    .fleet-metric-card:hover {
        border-color: rgba(20, 230, 176, 0.35) !important;
        box-shadow: 0 8px 20px rgba(20, 230, 176, 0.08) !important;
        transform: translateY(-1px) !important;
    }
    .metric-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 4px !important;
    }
    .metric-header span, .fleet-metric-card .metric-header span {
        color: #94a3b8 !important;
        font-weight: 700 !important;
    }
    div.stMarkdown p.runev-fleet-subheading,
    .runev-fleet-subheading {
        color: #cbd5e1 !important;
    }
    .metric-icon {
        font-size: 14px !important;
    }
    .metric-value {
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        line-height: 1.1 !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }
    .metric-value.text-green {
        color: #14e6b0 !important;
    }
    .metric-value.text-blue {
        color: #3b82f6 !important;
    }
    .metric-value.text-purple {
        color: #a855f7 !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) .stTabs [role="tablist"] button p {
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) [data-testid="element-container"] {
        margin-bottom: 0.25rem !important;
    }

    /* Text contrast & visibility overrides for light/dark themes */
    .block-container:has(.runev-driver-dashboard-landing) [data-testid="stMarkdownContainer"] p,
    .block-container:has(.runev-driver-dashboard-landing) [data-testid="stMarkdownContainer"] span,
    .block-container:has(.runev-driver-dashboard-landing) [data-testid="stMarkdownContainer"] h1,
    .block-container:has(.runev-driver-dashboard-landing) [data-testid="stMarkdownContainer"] h2,
    .block-container:has(.runev-driver-dashboard-landing) [data-testid="stMarkdownContainer"] h3,
    .block-container:has(.runev-driver-dashboard-landing) [data-testid="stMarkdownContainer"] h4,
    .block-container:has(.runev-driver-dashboard-landing) [data-testid="stMarkdownContainer"] label,
    .block-container:has(.runev-driver-dashboard-landing) p,
    .block-container:has(.runev-driver-dashboard-landing) span,
    .block-container:has(.runev-driver-dashboard-landing) label {
        color: #FFFFFF !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .runev-fleet-subheading {
        color: #cbd5e1 !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .preview-eyebrow {
        color: #14e6b0 !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .metric-header span {
        color: #94a3b8 !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .metric-value {
        color: #FFFFFF !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .metric-value.text-green {
        color: #14e6b0 !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .metric-value.text-blue {
        color: #3b82f6 !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .metric-value.text-purple {
        color: #a855f7 !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .runev-fleet-hero-banner .banner-logo {
        color: #14e6b0 !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .runev-fleet-hero-banner .banner-subtitle {
        color: #94a3b8 !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .runev-fleet-hero-banner .banner-status {
        color: #94a3b8 !important;
    }
    
    .block-container:has(.runev-driver-dashboard-landing) .runev-fleet-label {
        color: #00E5B3 !important;
    }

    .block-container:has(.runev-driver-dashboard-landing) .stCaptionContainer,
    .block-container:has(.runev-driver-dashboard-landing) .stCaptionContainer * {
        color: #94A3B8 !important;
    }
    </style>
    """
    st.markdown(landing_css, unsafe_allow_html=True)

    st.markdown(clean_html("""
    <div class="runev-fleet-hero-banner">
        <div class="banner-content">
            <span class="banner-logo">⚡ RunEV Dispatch</span>
            <span class="banner-divider">|</span>
            <span class="banner-subtitle">OPERATIONS COMMAND CENTRE</span>
        </div>
        <div class="banner-status">
            <span class="status-dot"></span> Live Network Active
        </div>
    </div>
    """), unsafe_allow_html=True)
    
    col_left, col_right = st.columns([0.58, 0.42], gap="medium")
    
    with col_left:
        st.markdown(clean_html("""
        <div class="runev-fleet-label">ON-DEMAND DISPATCH PLATFORM</div>
        <h1 class="runev-fleet-main-heading">RunEV Dispatch</h1>
        <p class="runev-fleet-subheading">Manage charging operations, drivers and fleet performance.</p>
        """), unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["Login", "Registration"])
        with tab_login:
            if st.session_state.get("driver_auth_mode") == "forgot":
                render_driver_forgot_password()
            else:
                render_driver_login_form()
        with tab_register:
            render_driver_register_form()
            
    with col_right:
        st.markdown(clean_html("""
        <div class="right-panel-header">
            <div class="preview-eyebrow">LIVE FLEET DASHBOARD</div>
        </div>
        """), unsafe_allow_html=True)
        
        # Render static illustration image
        st.image("admin_app/fleet_visual.png", use_column_width=True)
        
        st.markdown(clean_html("""
        <div class="fleet-metrics-grid">
            <div class="fleet-metric-card">
                <div class="metric-header">
                    <span>Today's Revenue</span>
                    <span class="metric-icon">💰</span>
                </div>
                <div class="metric-value text-green">₹2,45,680</div>
            </div>
            <div class="fleet-metric-card">
                <div class="metric-header">
                    <span>Active Drivers</span>
                    <span class="metric-icon">👥</span>
                </div>
                <div class="metric-value text-blue">128</div>
            </div>
            <div class="fleet-metric-card">
                <div class="metric-header">
                    <span>Live Requests</span>
                    <span class="metric-icon">⚡</span>
                </div>
                <div class="metric-value text-purple">32</div>
            </div>
            <div class="fleet-metric-card">
                <div class="metric-header">
                    <span>Fleet SLA</span>
                    <span class="metric-icon">📈</span>
                </div>
                <div class="metric-value text-green">99.8%</div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    # Render thin footer strip at the bottom of the page
    st.markdown(clean_html("""
    <div class="runev-fleet-footer">
        <div class="footer-content">
            <span class="footer-label">FLEET STATS:</span>
            <span class="footer-item"><span class="footer-num">24</span> Vans</span>
            <span class="footer-divider">|</span>
            <span class="footer-item"><span class="footer-num">128</span> Sessions</span>
            <span class="footer-divider">|</span>
            <span class="footer-item"><span class="footer-num">99.8%</span> SLA</span>
        </div>
    </div>
    """), unsafe_allow_html=True)




def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            textwrap.dedent("""
            <div class="runev-sidebar-brand">
                <div class="runev-sidebar-logo">RunEV Fleet</div>
                <p class="runev-sidebar-subtitle">Driver & operations console</p>
            </div>
            """),
            unsafe_allow_html=True,
        )
        st.caption(st.session_state.user.get("email"))
        choices = ["Dashboard", "Live Trips", "Drivers", "Analytics", "Earnings", "Payments", "Settings"]
        icon_map = {
            "Dashboard": "🏠",
            "Live Trips": "🛰️",
            "Drivers": "🚐",
            "Analytics": "📈",
            "Earnings": "💰",
            "Payments": "💳",
            "Settings": "⚙️",
        }
        labels = [f"{icon_map[item]}  {item}" for item in choices]
        nav_label = st.radio("Navigation", labels, label_visibility="collapsed")
        nav = choices[labels.index(nav_label)]
        st.divider()
        auto_refresh(10, enabled=nav in {"Dashboard", "Live Trips"})
        if st.button("Refresh", use_container_width=True):
            st.rerun()
        if st.button("Logout", use_container_width=True):
            clear_driver_session()
            st.session_state.show_add_provider_form = False
            st.rerun()
    return nav


def get_context():
    db = SessionLocal()
    if st.session_state.user.get("role") == "admin":
        providers = db.query(Provider).order_by(Provider.id).all()
    else:
        providers = db.query(Provider).filter(Provider.user_id == st.session_state.user["id"]).order_by(Provider.id).all()
    provider = providers[0] if providers else None
    providers_by_id = {item.id: item for item in providers}
    ensure_provider_role(db, provider)
    return db, providers, provider, providers_by_id


def get_active_requests(db, providers_by_id: dict[int, Provider]) -> list[ServiceRequest]:
    if not providers_by_id:
        return []
    return (
        db.query(ServiceRequest)
        .filter(ServiceRequest.provider_id.in_(list(providers_by_id.keys())), ServiceRequest.status.in_(VISIBLE_ACTIVE_TRIP_STATUSES))
        .order_by(ServiceRequest.request_time.desc())
        .all()
    )


def get_all_requests(db, providers_by_id: dict[int, Provider]) -> list[ServiceRequest]:
    if not providers_by_id:
        return []
    return db.query(ServiceRequest).filter(ServiceRequest.provider_id.in_(list(providers_by_id.keys()))).order_by(ServiceRequest.request_time.desc()).all()


def render_kpis(providers: list[Provider], pending: list, active: list, all_requests: list, providers_by_id: dict[int, Provider]) -> None:
    completed = [req for req in all_requests if req.status == "completed"]
    pending_payments = [req for req in all_requests if req.status == "awaiting_payment"]
    total_earnings = sum(estimate_service_amount(req, providers_by_id.get(req.provider_id)) for req in completed)
    cols = st.columns(5)
    for col, args in zip(
        cols,
        [
            ("Active Trips", len(active), "🛰️", "route tracked"),
            ("Total Revenue", money(total_earnings), "💰", "completed"),
            ("Available Drivers", sum(1 for p in providers if p.is_available), "🚐", f"{len(providers)} vans"),
            ("Charging Sessions", len(all_requests), "⚡", "all time"),
            ("Pending Payments", len(pending_payments), "🧾", f"{len(pending)} new requests"),
        ],
    ):
        with col:
            metric_card(*args)


def render_request_card(req, user: User | None, provider: Provider | None, pricing_settings=None) -> None:
    distance, eta = route_distance_and_eta(provider, req)
    user_phone = getattr(user, "phone", None) or getattr(getattr(req, "user", None), "phone", None)
    with st.container(border=True):
        col_a, col_b, col_c = st.columns([1.5, 1.1, 0.9])
        with col_a:
            status = getattr(req, "status", "pending")
            label = "In Route" if status in {"accepted", "en_route"} else None
            st.markdown(f"**{user.username if user else 'Customer'}** {status_badge(status, label)}", unsafe_allow_html=True)
            if user_phone:
                st.caption(f"Customer mobile: {user_phone}")
            if provider:
                st.caption(f"Van {provider.vehicle_number}")
                st.caption(f"Rating: {provider_rating_label(provider)}")
            if is_default_provider_location(req.pickup_lat, req.pickup_lng):
                pickup_address = "Old default pickup. Ask the customer to share live pickup again."
            else:
                pickup_address = reverse_geocode(
                    req.pickup_lat,
                    req.pickup_lng,
                    "Pickup address unavailable. Ask the customer to share live pickup again.",
                )
            st.text_input("Pickup address", value=pickup_address, key=f"pickup_address_{req.id}", disabled=True)
            timeline(getattr(req, "status", "pending"))
        with col_b:
            st.metric("ETA", f"{eta} min" if eta is not None else "Location needed")
            if distance is not None:
                st.caption(f"{distance:.2f} km away")
            st.caption(f"Payment: {getattr(req, 'payment_method', 'CASH')}")
        with col_c:
            if st.button("Open Map", key=f"map_{req.id}", use_container_width=True):
                st.session_state.selected_driver_map_request_id = req.id
            if getattr(req, "status", "pending") == "pending":
                accept, decline = st.columns(2)
                if accept.button("Accept", key=f"accept_{req.id}", use_container_width=True):
                    update_request_status(req.id, "accept")
                if decline.button("Decline", key=f"decline_{req.id}", use_container_width=True):
                    update_request_status(req.id, "reject")
            elif getattr(req, "status", "") == "awaiting_payment":
                st.metric("Final bill", money(getattr(req, "total_price", 0)))
                breakdown = request_fare_breakdown(req)
                st.caption(
                    f"Driver {money(breakdown['driver_earnings'])} / "
                    f"RunEV {money(breakdown['runev_earnings'])} / "
                    f"Charging {money(breakdown['charging_revenue'])}"
                )
                st.info("Waiting for payment choice.")
            else:
                amount = estimate_service_amount(req, provider)
                st.metric("Estimated fare", money(amount))
                status = getattr(req, "status", "")
                if status in {"accepted", "en_route"}:
                    if st.button("Mark Reached", key=f"arrived_{req.id}", use_container_width=True):
                        update_request_status(req.id, "arrived")
                elif status == "arrived":
                    st.info("Ask the customer for the trip OTP before charging.")
                    otp_code = st.text_input("Customer OTP", max_chars=6, key=f"otp_{req.id}")
                    if st.button("Verify OTP & start", key=f"start_charging_{req.id}", use_container_width=True, disabled=len(otp_code.strip()) != 6):
                        start_charging_with_otp(req.id, otp_code)
                elif status == "charging":
                    st.success("Charging in progress.")
                    units = st.number_input("Units gained (kWh)", min_value=0.0, step=0.5, format="%.2f", key=f"units_{req.id}")
                    emergency_limit = float(getattr(pricing_settings, "emergency_fee_limit", 0) or 0)
                    night_limit = float(getattr(pricing_settings, "night_fee_limit", 0) or 0)
                    emergency_fee = st.number_input("Emergency fee", min_value=0.0, max_value=emergency_limit, step=10.0, format="%.2f", key=f"emergency_fee_{req.id}")
                    night_fee = st.number_input("Night fee", min_value=0.0, max_value=night_limit, step=10.0, format="%.2f", key=f"night_fee_{req.id}")
                    charging_rate = float(getattr(pricing_settings, "charging_rate_per_kwh", 20) or 20)
                    st.caption(f"Charging rate: Rs {charging_rate:.2f}/kWh. Base, distance, charging, and platform rates are admin controlled.")
                    if st.button("Complete charging", key=f"bill_{req.id}", use_container_width=True, disabled=units <= 0):
                        submit_charged_units(req.id, units, emergency_fee, night_fee)


def render_dashboard() -> None:
    db, providers, provider, providers_by_id = get_context()
    try:
        pricing_settings = get_pricing_settings(db)
        pending = load_pending_requests_from_api()
        active = get_active_requests(db, providers_by_id)
        all_requests = get_all_requests(db, providers_by_id)
        hero("Fleet dashboard", f"Welcome, {st.session_state.user['username']}", "Live charging requests, dispatch queue, driver availability, and revenue pulse.")
        render_kpis(providers, pending, active, all_requests, providers_by_id)

        if not provider:
            st.warning("You do not have a charging van profile yet.")
            if st.button("Add Charging Van", use_container_width=True):
                st.session_state.show_add_provider_form = True
            if st.session_state.show_add_provider_form:
                render_provider_form(db)
            return

        with st.container(border=True):
            st.markdown("#### Driver live location")
            capture_provider_location(provider, "dashboard_quick", db=db)

        st.markdown("### Live Requests")
        if not pending:
            st.info("No users currently requesting a charge in your area.")
        for req in pending:
            request_provider = providers_by_id.get(req.provider_id, provider)
            user = db.query(User).filter(User.id == req.user_id).first()
            toast_for_status(getattr(req, "status", "pending"), f"provider_request_{req.id}")
            render_request_card(req, user, request_provider, pricing_settings)

        st.markdown("### Active Trips")
        if not active:
            st.info("No active trips yet.")
        for req in active:
            request_provider = providers_by_id.get(req.provider_id, provider)
            user = db.query(User).filter(User.id == req.user_id).first()
            render_request_card(req, user, request_provider, pricing_settings)

        st.markdown("### Live Route Map")
        map_requests = list(pending) + active
        selected_request = next(
            (req for req in map_requests if req.id == st.session_state.get("selected_driver_map_request_id")),
            None,
        )
        if selected_request:
            selected_provider = providers_by_id.get(selected_request.provider_id, provider)
            selected_user = db.query(User).filter(User.id == selected_request.user_id).first()
            st.caption(
                f"Showing route for request #{selected_request.id}"
                f" · {selected_user.username if selected_user else 'Customer'}"
                f" · {selected_provider.vehicle_number if selected_provider else 'Charging Van'}"
            )
            render_provider_map(selected_provider, [selected_request], key=f"fleet_selected_map_{selected_request.id}")
        else:
            st.caption("Tap Open Map on any request to focus its route.")
            render_provider_map(provider, map_requests, key="fleet_dashboard_map")
    finally:
        db.close()


def render_live_trips() -> None:
    db, providers, provider, providers_by_id = get_context()
    try:
        pricing_settings = get_pricing_settings(db)
        active = get_active_requests(db, providers_by_id)
        hero("Live trips", "Current routes only", "Only vans that are in route, reached, charging, or waiting for payment appear here.")

        if not provider:
            st.warning("You do not have a charging van profile yet.")
            return

        with st.container(border=True):
            st.markdown("#### Driver live location")
            capture_provider_location(provider, "live_trips_quick", db=db)

        st.markdown("### Current Trips")
        if not active:
            st.info("No current trips right now.")
        for req in active:
            request_provider = providers_by_id.get(req.provider_id, provider)
            user = db.query(User).filter(User.id == req.user_id).first()
            render_request_card(req, user, request_provider, pricing_settings)

        st.markdown("### Current Route Map")
        selected_request = next(
            (req for req in active if req.id == st.session_state.get("selected_driver_map_request_id")),
            None,
        )
        render_provider_map(
            providers_by_id.get(selected_request.provider_id, provider) if selected_request else provider,
            [selected_request] if selected_request else active,
            key=f"fleet_live_map_{selected_request.id}" if selected_request else "fleet_live_map",
        )
    finally:
        db.close()


def render_provider_form(db, existing: Provider | None = None) -> None:
    suffix = f"provider_{existing.id}" if existing else "provider_new"
    st.markdown("#### Van Live Location")
    address = capture_provider_location(existing, suffix, db=db)
    provider_user = existing.user if existing and existing.user else db.query(User).filter(User.id == st.session_state.user["id"]).first()
    with st.form(f"provider_form_{existing.id if existing else 'new'}"):
        driver_name = st.text_input("Driver Name", value=(existing.driver_name if existing else "") or "", key=f"driver_name_{suffix}")
        driver_mobile = st.text_input("Driver Mobile Number", value=(provider_user.phone if provider_user else "") or "", key=f"driver_mobile_{suffix}")
        vehicle_number = st.text_input("Vehicle Number", value=(existing.vehicle_number if existing else "") or "", key=f"vehicle_number_{suffix}")
        speed_options = ["AC 22kW", "DC 50kW", "DC 150kW"]
        default_speed = speed_options.index(existing.charging_speed) if existing and existing.charging_speed in speed_options else 0
        charging_speed = st.selectbox("Charging Speed", speed_options, index=default_speed, key=f"charging_speed_{suffix}")
        connector_types = st.text_input("Connector Types", value=(existing.connector_types if existing else "CCS2") or "CCS2", key=f"connector_types_{suffix}")
        price_per_kwh = st.number_input("Price per kWh (Rs)", value=float((existing.price_per_kwh if existing else 20.0) or 20.0), step=1.0, key=f"price_per_kwh_{suffix}")
        is_available = st.checkbox("Available for charging", value=bool(existing.is_available) if existing else True, key=f"is_available_{suffix}")
        uploaded_photo = st.file_uploader("Vehicle/Driver Image", type=["jpg", "jpeg", "png"], key=f"photo_{suffix}")
        if st.form_submit_button("Save Charging Van", use_container_width=True):
            try:
                driver_name = validate_full_name(driver_name, "Driver name")
                driver_mobile = normalize_indian_mobile(driver_mobile)
                vehicle_number = normalize_vehicle_number(vehicle_number)
                provider_lat, provider_lng, _ = validate_coordinates(
                    st.session_state.provider_lat,
                    st.session_state.provider_lng,
                )
                if price_per_kwh <= 0:
                    raise ValueError("Price per kWh must be greater than zero.")
                if uploaded_photo:
                    validate_file_upload(uploaded_photo.name, uploaded_photo.size)
            except ValueError as exc:
                st.error(str(exc))
                return
            if is_default_provider_location(provider_lat, provider_lng) and not address_matches_default_location(address):
                st.error("This van still has the default Pune coordinates. Click Share Driver Live Location before saving.")
                return
            provider = db.query(Provider).filter(Provider.id == existing.id).first() if existing else None
            provider = provider or Provider(user_id=st.session_state.user["id"])
            provider.vehicle_number = vehicle_number
            provider.charging_speed = charging_speed
            provider.connector_types = connector_types
            provider.price_per_kwh = price_per_kwh
            provider.current_lat = provider_lat
            provider.current_lng = provider_lng
            provider.is_available = is_available
            provider.driver_name = driver_name
            provider.address = address
            if provider_user:
                provider_user.phone = driver_mobile.strip() or None
            if uploaded_photo:
                photo_data = uploaded_photo.read()
                photo_b64 = base64.b64encode(photo_data).decode()
                photo_value = f"data:image/{uploaded_photo.type.split('/')[-1]};base64,{photo_b64}"
                if len(photo_value) <= 512:
                    provider.profile_photo = photo_value
                else:
                    st.warning("Driver details saved without the image because the uploaded file is too large for the current database column.")
            if provider.id is None:
                db.add(provider)
            try:
                db.commit()
                db.refresh(provider)
                if provider_user:
                    db.refresh(provider_user)
                    st.session_state.user["phone"] = provider_user.phone
                ensure_provider_role(db, provider)
                st.success("Charging van saved.")
                st.rerun()
            except SQLAlchemyError as exc:
                db.rollback()
                st.error(f"Charging van could not be saved: {exc}")


def render_drivers() -> None:
    db, providers, provider, providers_by_id = get_context()
    try:
        hero("Drivers", "Fleet profiles and availability", "Manage van details, driver image, connector types, rates, and online state.")
        if not providers:
            st.warning("Provider profile not found.")
            render_provider_form(db)
            return
        for item in providers:
            with st.container(border=True):
                col_photo, col_details = st.columns([0.8, 2])
                with col_photo:
                    if item.profile_photo:
                        st.image(item.profile_photo, width=180)
                    else:
                        st.markdown("<div class='runev-card' style='font-size:3rem;text-align:center'>🚐</div>", unsafe_allow_html=True)
                with col_details:
                    st.markdown(f"### {item.driver_name or st.session_state.user['username']} {status_badge('online' if item.is_available else 'offline', 'Online' if item.is_available else 'Offline')}", unsafe_allow_html=True)
                    st.caption(item.vehicle_number or "Vehicle number not added")
                    a, b, c = st.columns(3)
                    a.metric("Charging", item.charging_speed or "Standard")
                    b.metric("Connector", item.connector_types or "Universal")
                    c.metric("Rate", f"Rs {float(item.price_per_kwh or 20):.0f}/kWh")
                    render_provider_rating_card(item)
                    st.caption(item.address or st.session_state.provider_address)
                with st.expander("Update this van"):
                    render_provider_form(db, item)
        with st.expander("Add another charging van"):
            render_provider_form(db)
    finally:
        db.close()


def render_analytics() -> None:
    db, providers, provider, providers_by_id = get_context()
    try:
        all_requests = get_all_requests(db, providers_by_id)
        hero("Analytics", "Fleet intelligence", "Revenue, trips, driver activity, charging trends, heatmaps, peak hours, and future forecasting hooks.")
        render_operations_analytics(all_requests, providers)
        st.markdown("#### Advanced Modules")
        cols = st.columns(4)
        for col, args in zip(
            cols,
            [("AI ETA Prediction", "Model hook ready", "🧠", "traffic + driver data"), ("Smart Dispatch", "Rule engine ready", "🛰️", "nearest/fastest"), ("Battery Intelligence", "SOC placeholder", "🔋", "vehicle telemetry"), ("Demand Forecasting", "Trend-ready", "📈", "heatmap inputs")],
        ):
            with col:
                metric_card(*args)
    finally:
        db.close()


def render_earnings() -> None:
    db, providers, provider, providers_by_id = get_context()
    try:
        all_requests = get_all_requests(db, providers_by_id)
        completed = [req for req in all_requests if req.status == "completed"]
        active = [req for req in all_requests if req.status in ["accepted", "arrived", "charging"]]
        cancelled = [req for req in all_requests if req.status == "cancelled"]
        total = sum(estimate_service_amount(req, providers_by_id.get(req.provider_id)) for req in completed)
        pipeline = sum(estimate_service_amount(req, providers_by_id.get(req.provider_id)) for req in active)
        hero("Earnings", "Revenue and trips", "Completed payments, active value, cancellations, and invoices.")
        cols = st.columns(4)
        for col, args in zip(cols, [("Completed", len(completed), "✅", "paid trips"), ("Earnings", money(total), "💰", "settled"), ("Active Value", money(pipeline), "🧾", "in progress"), ("Rejected", len(cancelled), "↩️", "cancelled")]):
            with col:
                metric_card(*args)
        render_trip_history(db, all_requests, providers_by_id)
    finally:
        db.close()


def render_trip_history(db, requests_list: list[ServiceRequest], providers_by_id: dict[int, Provider]) -> None:
    st.markdown("### Trips")
    if not requests_list:
        st.info("No trip history yet.")
        return
    for req in requests_list:
        user = db.query(User).filter(User.id == req.user_id).first()
        provider = providers_by_id.get(req.provider_id)
        with st.container(border=True):
            a, b, c = st.columns([1.4, 1, 0.8])
            a.markdown(f"**{user.username if user else 'Customer'}**")
            a.caption(f"Van: {provider.vehicle_number if provider else 'Charging Van'}")
            a.caption(f"Rating: {provider_rating_label(provider)}")
            b.markdown(status_badge(req.status), unsafe_allow_html=True)
            b.caption(format_local_time(req.request_time))
            c.metric("Amount", money(estimate_service_amount(req, provider)))


def render_payments() -> None:
    db, providers, provider, providers_by_id = get_context()
    try:
        all_requests = get_all_requests(db, providers_by_id)
        awaiting = [req for req in all_requests if req.status == "awaiting_payment"]
        paid = [req for req in all_requests if req.status == "completed"]
        hero("Payments", "Billing operations", "Invoice preview, confirmation states, and Razorpay-ready integration surface.")
        cols = st.columns(3)
        cols[0].metric("Awaiting Payment", len(awaiting))
        cols[1].metric("Paid Trips", len(paid))
        cols[2].metric("Collected", money(sum(float(req.total_price or 0) for req in paid)))
        render_trip_history(db, awaiting + paid, providers_by_id)
    finally:
        db.close()


def render_settings() -> None:
    hero("Settings", "Console preferences", "Theme, density, and fleet console appearance.")
    if st.session_state.user.get("role") == "admin":
        db = SessionLocal()
        try:
            pricing = get_pricing_settings(db)
            st.markdown("#### Pricing")
            with st.form("admin_pricing_settings_form"):
                base_visit_fee = st.number_input("Base Visit Fee", min_value=0.0, value=float(pricing.base_visit_fee), step=1.0, format="%.2f")
                distance_rate = st.number_input("Distance Rate per km", min_value=0.0, value=float(pricing.distance_rate_per_km), step=1.0, format="%.2f")
                charging_rate = st.number_input("Charging Rate per kWh", min_value=0.0, value=float(pricing.charging_rate_per_kwh), step=1.0, format="%.2f")
                platform_fee = st.number_input("Platform Fee", min_value=0.0, value=float(pricing.platform_fee), step=1.0, format="%.2f")
                emergency_limit = st.number_input("Emergency Fee Limit", min_value=0.0, value=float(pricing.emergency_fee_limit or 0), step=10.0, format="%.2f")
                night_limit = st.number_input("Night Fee Limit", min_value=0.0, value=float(pricing.night_fee_limit or 0), step=10.0, format="%.2f")
                if st.form_submit_button("Save Pricing", use_container_width=True):
                    pricing.base_visit_fee = base_visit_fee
                    pricing.distance_rate_per_km = distance_rate
                    pricing.charging_rate_per_kwh = charging_rate
                    pricing.platform_fee = platform_fee
                    pricing.emergency_fee_limit = emergency_limit
                    pricing.night_fee_limit = night_limit
                    db.commit()
                    st.success("Pricing updated.")
                    st.rerun()
        finally:
            db.close()
        st.divider()
    st.markdown("#### Theme")
    mode = render_theme_selector("driver_theme_selector")
    persist_theme_preference(st.session_state.get("jwt_token"), mode)
    st.markdown("#### Admin appearance controls")
    st.color_picker("Brand color", value="#14e6b0", key="driver_brand_color")
    st.color_picker("Accent color", value="#6366f1", key="driver_accent_color")
    st.select_slider("Dashboard density", options=["Comfortable", "Balanced", "Compact"], value="Balanced", key="driver_density")
    st.selectbox("Card appearance", ["Subtle", "Elevated", "Outlined"], key="driver_card_style")
    st.caption("Theme preferences are saved to your account and mirrored to browser local storage for this console session.")


def main() -> None:
    try:
        ensure_database_schema()
    except SQLAlchemyError as exc:
        print(f"Database setup failed: {exc}")
        st.error("Database setup failed. Please check the configured DATABASE_URL and redeploy.")
        st.stop()

    init_state()
    render_live_notification()
    if st.session_state.user is None:
        render_login()
        return

    nav = render_sidebar()
    if nav == "Dashboard":
        render_dashboard()
    elif nav == "Live Trips":
        render_live_trips()
    elif nav == "Drivers":
        render_drivers()
    elif nav == "Analytics":
        render_analytics()
    elif nav == "Earnings":
        render_earnings()
    elif nav == "Payments":
        render_payments()
    else:
        render_settings()


main()
