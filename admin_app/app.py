from __future__ import annotations

import base64
import math
import os
import sys
from datetime import datetime
from types import SimpleNamespace

import requests
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import Base, SessionLocal, engine
from backend.models import Provider, ServiceRequest, User
from backend.services.dispatch_service import ACTIVE_TRIP_STATUSES
from frontend.components.analytics import render_operations_analytics
from frontend.components.geolocation import live_location_button
from frontend.components.maps import render_provider_map
from frontend.components.ui import hero, metric_card, money, safe_text, status_badge, timeline
from frontend.styles.theme import configure_page, inject_global_styles
from frontend.utils.live import auto_refresh, push_notification, render_live_notification, toast_for_status
from utils import api_client


configure_page("RunEV - Driver Console", "🚐")
inject_global_styles()

VISIBLE_ACTIVE_TRIP_STATUSES = tuple(status for status in ACTIVE_TRIP_STATUSES if status != "pending")


@st.cache_resource
def ensure_database_schema() -> None:
    Base.metadata.create_all(bind=engine)


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
            timeout=4,
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


def submit_charged_units(request_id: int, charged_units_kwh: float) -> None:
    try:
        api_client.request_json(
            "POST",
            f"/api/v1/requests/charge/{request_id}/units",
            token=st.session_state.get("jwt_token"),
            json={"charged_units_kwh": charged_units_kwh},
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
    rate = float(getattr(provider, "price_per_kwh", None) or 20)
    distance, _ = route_distance_and_eta(provider, request)
    return round(149 + float(distance or 0) * 18 + rate, 2)


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
        f"""
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
        """,
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


def capture_provider_location(provider: Provider | None = None, key_suffix: str = "default") -> str:
    if provider and provider.current_lat and provider.current_lng:
        st.session_state.provider_lat = float(provider.current_lat)
        st.session_state.provider_lng = float(provider.current_lng)
    if provider and provider.address:
        st.session_state.provider_address = provider.address

    address_key = f"provider_address_{key_suffix}"
    if address_key not in st.session_state:
        st.session_state[address_key] = provider.address if provider and provider.address else st.session_state.provider_address

    capture_key = f"capture_provider_location_{key_suffix}"
    location = live_location_button("Use My Live Location", key=capture_key)
    if location and location.get("error"):
        st.warning(location["error"])
    elif location and location.get("latitude") and location.get("longitude"):
        location_key = f"{capture_key}:{location.get('latitude')}:{location.get('longitude')}:{location.get('timestamp')}"
        if st.session_state.get(f"{capture_key}_last_location_key") != location_key:
            st.session_state[f"{capture_key}_last_location_key"] = location_key
            st.session_state.provider_lat = float(location["latitude"])
            st.session_state.provider_lng = float(location["longitude"])
            st.session_state.provider_address = reverse_geocode(st.session_state.provider_lat, st.session_state.provider_lng, st.session_state.provider_address)
            st.session_state[address_key] = st.session_state.provider_address
            if provider:
                try:
                    api_client.request_json(
                        "PUT",
                        "/api/v1/tracking/provider/location",
                        token=st.session_state.get("jwt_token"),
                        json={
                            "provider_id": provider.id,
                            "current_lat": st.session_state.provider_lat,
                            "current_lng": st.session_state.provider_lng,
                            "address": st.session_state.provider_address,
                        },
                    )
                    push_notification("Live van location updated", "success")
                    st.rerun()
                except api_client.ApiError as exc:
                    st.warning(str(exc))
    address = st.text_input("Van live address", key=address_key)
    st.session_state.provider_address = address
    return address


def render_login() -> None:
    hero("RunEV fleet", "Driver and admin operations console", "Accept live requests, manage vans, generate bills, and monitor revenue from a premium command center.")
    col_form, col_visual = st.columns([0.9, 1.1])
    with col_form:
        tab_login, tab_signup = st.tabs(["Login", "Register Fleet"])
        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Launch Fleet Console", use_container_width=True):
                    try:
                        token_data = api_client.login(email, password)
                        token = token_data["access_token"]
                        user = api_client.me(token)
                        st.session_state.user = {"id": user["id"], "username": user["username"], "email": user["email"], "role": user["role"]}
                        st.session_state.jwt_token = token
                        st.session_state.show_add_provider_form = user["role"] == "provider"
                        st.rerun()
                    except api_client.ApiError as exc:
                        st.error(str(exc))
        with tab_signup:
            with st.form("driver_signup_form"):
                username = st.text_input("Driver Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                vehicle_number = st.text_input("Vehicle Number")
                if st.form_submit_button("Register Fleet", use_container_width=True):
                    if not username or not email or not password or not vehicle_number:
                        st.error("Please fill all fields.")
                    elif len(username.strip()) < 2:
                        st.error("Driver name must be at least 2 characters.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        try:
                            api_client.register(username.strip(), email.strip(), password, role="provider", vehicle_number=vehicle_number.strip())
                            st.success("Driver account created. Please login.")
                        except api_client.ApiError as exc:
                            st.error(str(exc))
    with col_visual:
        st.markdown(
            """
            <div class="runev-card" style="min-height:360px;display:flex;flex-direction:column;justify-content:space-between">
                <div><span class="runev-badge badge-green">Enterprise fleet UX</span><h2>Live dispatch, earnings, driver status, and service control</h2>
                <p class="runev-subtitle">Built for repeated operational use with dense metrics, fast actions, and production-grade styling.</p></div>
                <div style="font-size:4rem">🚐</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("## RunEV Fleet")
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
            st.session_state.user = None
            st.session_state.jwt_token = None
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


def render_request_card(req, user: User | None, provider: Provider | None) -> None:
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
            st.caption(reverse_geocode(req.pickup_lat, req.pickup_lng, "Customer pickup"))
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
                    if provider:
                        st.caption(f"Rate: Rs {float(provider.price_per_kwh or 20):.2f}/kWh")
                    if st.button("Complete charging", key=f"bill_{req.id}", use_container_width=True, disabled=units <= 0):
                        submit_charged_units(req.id, units)


def render_dashboard() -> None:
    db, providers, provider, providers_by_id = get_context()
    try:
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

        with st.expander("Driver live location", expanded=False):
            capture_provider_location(provider, "dashboard_quick")

        st.markdown("### Live Requests")
        if not pending:
            st.info("No users currently requesting a charge in your area.")
        for req in pending:
            request_provider = providers_by_id.get(req.provider_id, provider)
            user = db.query(User).filter(User.id == req.user_id).first()
            toast_for_status(getattr(req, "status", "pending"), f"provider_request_{req.id}")
            render_request_card(req, user, request_provider)

        st.markdown("### Active Trips")
        if not active:
            st.info("No active trips yet.")
        for req in active:
            request_provider = providers_by_id.get(req.provider_id, provider)
            user = db.query(User).filter(User.id == req.user_id).first()
            render_request_card(req, user, request_provider)

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
        active = get_active_requests(db, providers_by_id)
        hero("Live trips", "Current routes only", "Only vans that are in route, reached, charging, or waiting for payment appear here.")

        if not provider:
            st.warning("You do not have a charging van profile yet.")
            return

        with st.expander("Driver live location", expanded=True):
            capture_provider_location(provider, "live_trips_quick")

        st.markdown("### Current Trips")
        if not active:
            st.info("No current trips right now.")
        for req in active:
            request_provider = providers_by_id.get(req.provider_id, provider)
            user = db.query(User).filter(User.id == req.user_id).first()
            render_request_card(req, user, request_provider)

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
    address = capture_provider_location(existing, suffix)
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
            if not vehicle_number:
                st.error("Vehicle number is required.")
                return
            provider = existing or Provider(user_id=st.session_state.user["id"])
            provider.vehicle_number = vehicle_number
            provider.charging_speed = charging_speed
            provider.connector_types = connector_types
            provider.price_per_kwh = price_per_kwh
            provider.current_lat = st.session_state.provider_lat
            provider.current_lng = st.session_state.provider_lng
            provider.is_available = is_available
            provider.driver_name = driver_name
            provider.address = address
            if provider_user:
                provider_user.phone = driver_mobile.strip() or None
            if uploaded_photo:
                photo_data = uploaded_photo.read()
                photo_b64 = base64.b64encode(photo_data).decode()
                provider.profile_photo = f"data:image/{uploaded_photo.type.split('/')[-1]};base64,{photo_b64}"
            if existing is None:
                db.add(provider)
            db.commit()
            ensure_provider_role(db, provider)
            st.success("Charging van saved.")
            st.rerun()


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
            b.caption(req.request_time.strftime("%d %b %Y, %I:%M %p"))
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
    hero("Settings", "Console preferences", "Account state and operational placeholders.")
    st.info("Backend APIs and database logic are preserved. AI ETA, smart dispatch, battery intelligence, and demand forecasting modules are intentionally surfaced as extensible frontend architecture.")


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
