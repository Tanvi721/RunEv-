from __future__ import annotations

import html
import math
import os
import sys
from datetime import datetime

import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from frontend.components.analytics import render_operations_analytics
from frontend.components.maps import render_trip_map, render_user_map
from frontend.components.payment import (
    render_charging_summary,
    render_driver_card,
    sample_upi_qr,
    render_secure_payment_note,
    render_success_screen,
)
from frontend.components.ui import hero, metric_card, money, safe_text, status_badge, timeline
from frontend.styles.theme import configure_page, inject_global_styles
from frontend.utils.live import auto_refresh, push_notification, render_live_notification, toast_for_status
from utils import api_client

try:
    from streamlit_geolocation import streamlit_geolocation
except Exception:
    streamlit_geolocation = None


configure_page("RunEV - User App", "⚡")
inject_global_styles()

ACTIVE_REQUEST_STATUSES = {"pending", "accepted", "en_route", "arrived", "charging", "awaiting_payment"}


def init_state() -> None:
    defaults = {
        "user": None,
        "jwt_token": None,
        "user_lat": 18.5204,
        "user_lng": 73.8567,
        "user_address": "Detecting your live pickup location",
        "active_request_id": None,
        "payment_gateway_request_id": None,
        "payment_gateway_order": None,
        "last_paid_invoice": None,
        "user_nav": "Dashboard",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return radius * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def estimate_eta_minutes(distance_km: float | None) -> int:
    return max(2, round(((distance_km or 0) / 25.0) * 60))


def reverse_geocode(lat: float, lng: float, fallback: str) -> str:
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


def format_date(value: str | None) -> str:
    if not value:
        return "Recent"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b, %I:%M %p")
    except ValueError:
        return value


def load_my_requests() -> list[dict]:
    try:
        return api_client.request_json("GET", "/api/v1/requests/mine", token=st.session_state.get("jwt_token")) or []
    except api_client.ApiError as exc:
        st.error(str(exc))
        return []


def load_request_status(request_id: int) -> dict | None:
    try:
        return api_client.request_json("GET", f"/api/v1/requests/charge/{request_id}", token=st.session_state.get("jwt_token"))
    except api_client.ApiError as exc:
        st.error(str(exc))
        return None


def load_all_providers(user_lat: float | None = None, user_lng: float | None = None) -> list[dict]:
    try:
        providers = api_client.request_json("GET", "/api/v1/providers", token=st.session_state.get("jwt_token")) or []
    except api_client.ApiError as exc:
        st.error(str(exc))
        return []

    rows = []
    for provider in providers:
        lat, lng = provider.get("current_lat"), provider.get("current_lng")
        if lat is None or lng is None:
            continue
        distance = calculate_distance(user_lat, user_lng, lat, lng) if user_lat is not None and user_lng is not None else None
        rows.append(
            {
                **provider,
                "charging_speed": provider.get("charging_speed") or "Standard",
                "connector_types": provider.get("connector_types") or "Universal",
                "price_per_kwh": provider.get("price_per_kwh") or 20.0,
                "distance_km": distance,
            }
        )
    return sorted(rows, key=lambda row: row["distance_km"] if row["distance_km"] is not None else 99999)


def sync_active_request_from_backend() -> None:
    if st.session_state.active_request_id:
        return
    active = [req for req in load_my_requests() if req.get("status") in ACTIVE_REQUEST_STATUSES]
    if active:
        st.session_state.active_request_id = active[0]["id"]


def create_charge_request(provider_id: int | None = None) -> None:
    try:
        data = api_client.request_json(
            "POST",
            "/api/v1/requests/charge",
            token=st.session_state.get("jwt_token"),
            json={
                "user_id": st.session_state.user["id"],
                "provider_id": provider_id,
                "pickup_lat": float(st.session_state.user_lat),
                "pickup_lng": float(st.session_state.user_lng),
            },
        )
        st.session_state.active_request_id = data["request_id"]
        push_notification("Request sent to charging van", "success")
        st.rerun()
    except api_client.ApiError as exc:
        st.error(str(exc))


def choose_payment_method(request_id: int, method: str) -> None:
    try:
        api_client.request_json(
            "POST",
            f"/api/v1/requests/charge/{request_id}/payment-method",
            token=st.session_state.get("jwt_token"),
            json={"payment_method": method},
        )
        previous_paid = st.session_state.get("last_paid_invoice") or {}
        st.session_state.last_paid_invoice = {
            "invoice_id": request_id,
            "amount": previous_paid.get("amount"),
            "order_id": method,
        }
        st.session_state.active_request_id = None
        push_notification("Payment received", "success")
        st.rerun()
    except api_client.ApiError as exc:
        st.error(str(exc))


def create_payment_order(request_id: int) -> dict | None:
    try:
        return api_client.request_json(
            "POST",
            "/api/v1/payments/orders",
            token=st.session_state.get("jwt_token"),
            json={"request_id": request_id},
        )
    except api_client.ApiError as exc:
        st.error(str(exc))
        return None


def verify_gateway_payment(order: dict) -> bool:
    try:
        api_client.request_json(
            "POST",
            "/api/v1/payments/verify",
            token=st.session_state.get("jwt_token"),
            json={
                "payment_id": order["payment_id"],
                "razorpay_order_id": order["order_id"],
                "razorpay_payment_id": f"pay_dev_{order['payment_id']}",
                "razorpay_signature": f"dev_{order['order_id']}",
            },
        )
        st.session_state.active_request_id = None
        st.session_state.payment_gateway_request_id = None
        st.session_state.payment_gateway_order = None
        if order.get("request_id"):
            st.session_state.pop(f"gateway_upi_app_{order.get('request_id')}", None)
        st.session_state.last_paid_invoice = {
            "invoice_id": order.get("request_id"),
            "amount": order.get("amount"),
            "order_id": order.get("order_id"),
        }
        push_notification("Payment received", "success")
        st.rerun()
        return True
    except api_client.ApiError as exc:
        st.error(str(exc))
        return False


def render_bill_totals(request_status: dict, provider: dict, amount: float, compact: bool = False) -> None:
    units = float(request_status.get("charged_units_kwh") or 0)
    rate = float(provider.get("price_per_kwh") or 20)
    vehicle = html.escape(provider.get("vehicle_number") or "Charging van")
    driver = html.escape(provider.get("driver_name") or "Assigned driver")
    padding = "18px" if compact else "22px"
    title_size = "28px" if compact else "34px"
    total_size = "34px" if compact else "44px"
    st.markdown(
        f"""
        <div style="background:linear-gradient(145deg,rgba(30,41,59,.96),rgba(15,23,42,.84));border:1px solid rgba(148,163,184,.24);border-radius:20px;padding:{padding};box-shadow:0 24px 80px rgba(2,6,23,.34);">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:18px;">
                <div>
                    <span class="runev-badge badge-blue">Bill Ready</span>
                    <h3 style="margin:12px 0 0;font-size:{title_size};line-height:1.05;">Invoice #{request_status.get('id')}</h3>
                </div>
                <div style="font-size:{total_size};line-height:1;font-weight:850;color:#f8fafc;white-space:nowrap;">{money(amount)}</div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:18px;">
                <div style="min-width:0;padding:14px;border:1px solid rgba(148,163,184,.20);border-radius:14px;background:rgba(15,23,42,.58);">
                    <span style="display:block;color:#cbd5e1;font-size:13px;font-weight:800;margin-bottom:6px;">Units</span>
                    <strong style="display:block;color:#f8fafc;font-size:20px;line-height:1.15;">{units:.2f} kWh</strong>
                </div>
                <div style="min-width:0;padding:14px;border:1px solid rgba(148,163,184,.20);border-radius:14px;background:rgba(15,23,42,.58);">
                    <span style="display:block;color:#cbd5e1;font-size:13px;font-weight:800;margin-bottom:6px;">Rate</span>
                    <strong style="display:block;color:#f8fafc;font-size:20px;line-height:1.15;">Rs {rate:.2f}/kWh</strong>
                </div>
                <div style="min-width:0;padding:14px;border:1px solid rgba(148,163,184,.20);border-radius:14px;background:rgba(15,23,42,.58);">
                    <span style="display:block;color:#cbd5e1;font-size:13px;font-weight:800;margin-bottom:6px;">Total</span>
                    <strong style="display:block;color:#f8fafc;font-size:20px;line-height:1.15;">{money(amount)}</strong>
                </div>
            </div>
            <div style="display:grid;gap:12px;">
                <div style="display:flex;justify-content:space-between;gap:16px;border-bottom:1px solid rgba(148,163,184,.14);padding-bottom:10px;">
                    <span style="color:#cbd5e1;font-weight:800;">Driver</span>
                    <strong style="color:#f8fafc;text-align:right;">{driver}</strong>
                </div>
                <div style="display:flex;justify-content:space-between;gap:16px;border-bottom:1px solid rgba(148,163,184,.14);padding-bottom:10px;">
                    <span style="color:#cbd5e1;font-weight:800;">Vehicle</span>
                    <strong style="color:#f8fafc;text-align:right;">{vehicle}</strong>
                </div>
                <div style="display:flex;justify-content:space-between;gap:16px;">
                    <span style="color:#cbd5e1;font-weight:800;">Energy</span>
                    <strong style="color:#f8fafc;text-align:right;">{units:.2f} kWh at Rs {rate:.2f}/kWh</strong>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_razorpay_checkout(order: dict, request_status: dict, method: str, selected_upi_app: str | None = None) -> None:
    key_id = order.get("key_id")
    if not key_id:
        st.error("Razorpay key is missing for this order.")
        return

    user = st.session_state.user or {}
    api_base_url = api_client.API_BASE_URL
    token = st.session_state.get("jwt_token") or ""
    amount_paise = int(round(float(order.get("amount") or 0) * 100))
    method_prefill = {
        "UPI": "upi",
        "Card": "card",
        "NetBanking": "netbanking",
        "Other payment options": "upi",
    }.get(method, "upi")
    checkout_html = f"""
    <html>
    <head>
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        <style>
            body {{ margin: 0; font-family: Inter, system-ui, sans-serif; background: transparent; color: #f8fafc; }}
            button {{
                width: 100%;
                min-height: 56px;
                border: 1px solid rgba(0, 229, 168, 0.35);
                border-radius: 999px;
                background: linear-gradient(135deg, #00e5a8, #3b82f6);
                color: #03111f;
                font-size: 18px;
                font-weight: 800;
                cursor: pointer;
                box-shadow: 0 18px 50px rgba(0, 229, 168, .24);
                transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
            }}
            button:hover {{
                transform: translateY(-2px);
                filter: brightness(1.06);
                box-shadow: 0 22px 68px rgba(0, 229, 168, .34), 0 0 0 1px rgba(255,255,255,.16) inset;
            }}
            button.loading {{
                color: transparent;
                position: relative;
            }}
            button.loading::after {{
                content: "";
                position: absolute;
                top: 50%;
                left: 50%;
                width: 22px;
                height: 22px;
                margin: -11px 0 0 -11px;
                border-radius: 999px;
                border: 3px solid rgba(3, 17, 31, 0.22);
                border-top-color: #03111f;
                animation: spin 850ms linear infinite;
            }}
            .msg {{ margin-top: 12px; color: #cbd5e1; font-size: 14px; line-height: 1.5; }}
            .choice {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                margin-bottom: 12px;
                padding: 12px 14px;
                border: 1px solid rgba(59, 130, 246, 0.28);
                border-radius: 18px;
                background: rgba(30, 41, 59, 0.72);
                box-shadow: 0 16px 38px rgba(2, 6, 23, 0.22);
            }}
            .choice span {{ color: #94a3b8; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }}
            .choice strong {{ color: #f8fafc; font-size: 15px; }}
            .error {{ color: #fecaca; }}
            @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="choice">
            <span>UPI app</span>
            <strong>{selected_upi_app or "Razorpay UPI"}</strong>
        </div>
        <button id="pay">Pay Securely</button>
        <div id="msg" class="msg">Razorpay checkout will open in a secure popup with UPI shown first.</div>
        <script>
            const msg = document.getElementById("msg");
            const payButton = document.getElementById("pay");
            const options = {{
                key: {key_id!r},
                amount: {amount_paise},
                currency: {order.get("currency", "INR")!r},
                name: "RunEV",
                description: "Invoice #{request_status.get('id')}",
                order_id: {order.get("order_id")!r},
                prefill: {{
                    name: {user.get("username", "")!r},
                    email: {user.get("email", "")!r},
                    contact: {user.get("phone", "") or ""!r}
                }},
                notes: {{
                    runev_invoice_id: {str(request_status.get("id"))!r},
                    preferred_upi_app: {(selected_upi_app or "Razorpay UPI")!r}
                }},
                method: {{
                    upi: true,
                    card: true,
                    netbanking: true,
                    wallet: true
                }},
                config: {{
                    display: {{
                        sequence: ["upi", "card", "netbanking", "wallet", "paylater"],
                        preferences: {{
                            show_default_blocks: true
                        }}
                    }}
                }},
                handler: async function (response) {{
                    msg.textContent = "Verifying payment...";
                    payButton.className = "loading";
                    const verifyResponse = await fetch({(api_base_url + "/api/v1/payments/verify")!r}, {{
                        method: "POST",
                        headers: {{
                            "Content-Type": "application/json",
                            "Authorization": "Bearer " + {token!r}
                        }},
                        body: JSON.stringify({{
                            payment_id: {order.get("payment_id")},
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature
                        }})
                    }});
                    if (verifyResponse.ok) {{
                        msg.textContent = "Payment successful. Refreshing RunEV...";
                        window.parent.location.reload();
                    }} else {{
                        const errorText = await verifyResponse.text();
                        msg.textContent = "Payment verification failed: " + errorText;
                        msg.className = "msg error";
                        payButton.className = "";
                    }}
                }},
                modal: {{
                    ondismiss: function () {{
                        msg.textContent = "Payment popup closed.";
                        payButton.className = "";
                    }}
                }}
            }};
            payButton.onclick = function () {{
                payButton.className = "loading";
                msg.textContent = "Opening Razorpay checkout...";
                new Razorpay(options).open();
                setTimeout(function () {{
                    if (msg.textContent === "Opening Razorpay checkout...") {{
                        payButton.className = "";
                    }}
                }}, 1400);
            }};
        </script>
    </body>
    </html>
    """
    components.html(checkout_html, height=650, scrolling=True)


def capture_user_location() -> None:
    st.markdown("#### Pickup")
    if st.button("Use My Live Location", key="capture_user_location_button", use_container_width=True):
        st.session_state.capture_user_location = True

    if streamlit_geolocation and st.session_state.get("capture_user_location"):
        location = streamlit_geolocation()
        if location and location.get("latitude") and location.get("longitude"):
            st.session_state.user_lat = float(location["latitude"])
            st.session_state.user_lng = float(location["longitude"])
            st.session_state.user_address = reverse_geocode(
                st.session_state.user_lat,
                st.session_state.user_lng,
                st.session_state.user_address,
            )
            push_notification("Live pickup location captured", "success")
            st.session_state.capture_user_location = False
    elif not streamlit_geolocation:
        st.info("Install streamlit-geolocation to enable browser live location.")
    else:
        st.caption("Tap the live location button to update pickup from this device.")

    st.text_input("Pickup address", key="user_address")


def render_login() -> None:
    hero("RunEV passenger", "On-demand EV charging, at your location", "Request a mobile charging van, track it live, and complete payment in one polished flow.")
    col_form, col_visual = st.columns([0.9, 1.1])
    with col_form:
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Launch RunEV", use_container_width=True):
                    try:
                        token_data = api_client.login(email, password)
                        token = token_data["access_token"]
                        user = api_client.me(token)
                        st.session_state.user = {
                            "id": user["id"],
                            "username": user["username"],
                            "email": user["email"],
                            "role": user["role"],
                            "phone": user.get("phone"),
                        }
                        st.session_state.jwt_token = token
                        st.rerun()
                    except api_client.ApiError as exc:
                        st.error(str(exc))
        with tab_signup:
            with st.form("signup_form"):
                username = st.text_input("Username")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not username or not email or not password:
                        st.error("Please fill all fields.")
                    else:
                        try:
                            api_client.register(username, email, password, role="user")
                            st.success("Account created. You can login now.")
                        except api_client.ApiError as exc:
                            st.error(str(exc))
    with col_visual:
        st.markdown(
            """
            <div class="runev-card" style="min-height:360px;display:flex;flex-direction:column;justify-content:space-between">
                <div>
                    <span class="runev-badge badge-green">Live network</span>
                    <h2>Premium charging support for city EV owners</h2>
                    <p class="runev-subtitle">Smart dispatch, driver visibility, billing, route maps, and future AI ETA architecture are ready inside the app.</p>
                </div>
                <div style="font-size:4.5rem;line-height:1">⚡</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("## RunEV")
        st.caption(st.session_state.user.get("email"))
        sync_label = "Live Trips" if st.session_state.active_request_id else "Dashboard"
        choices = ["Dashboard", "Live Trips", "Analytics", "Payments", "History", "Settings"]
        icon_map = {
            "Dashboard": "🏠",
            "Live Trips": "🛰️",
            "Analytics": "📈",
            "Payments": "💳",
            "History": "🧾",
            "Settings": "⚙️",
        }
        default_index = choices.index(sync_label if sync_label in choices else "Dashboard")
        labels = [f"{icon_map[item]}  {item}" for item in choices]
        nav_label = st.radio("Navigation", labels, index=default_index, key="user_nav_radio")
        nav = choices[labels.index(nav_label)]
        st.divider()
        auto_refresh(12, enabled=nav in {"Dashboard", "Live Trips"})
        if st.button("Refresh", use_container_width=True):
            st.rerun()
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.jwt_token = None
            st.session_state.active_request_id = None
            st.rerun()
    return nav


def render_dashboard() -> None:
    user = st.session_state.user
    requests_list = load_my_requests()
    providers = load_all_providers(float(st.session_state.user_lat), float(st.session_state.user_lng))
    completed = [req for req in requests_list if req.get("status") == "completed"]
    active = [req for req in requests_list if req.get("status") in ACTIVE_REQUEST_STATUSES]
    pending_payments = [req for req in requests_list if req.get("status") == "awaiting_payment"]

    hero("Passenger dashboard", f"Hello, {user['username']}", "Find nearby mobile chargers, track your request live, and settle bills instantly.")
    cols = st.columns(5)
    metrics = [
        ("Active Trips", len(active), "🛰️", "live monitored"),
        ("Total Spend", money(sum(float(req.get("total_price") or 0) for req in completed)), "💳", "completed rides"),
        ("Available Drivers", sum(1 for provider in providers if provider.get("is_available")), "🚐", "nearby vans"),
        ("Charging Sessions", len(requests_list), "⚡", "all time"),
        ("Pending Payments", len(pending_payments), "🧾", "needs action"),
    ]
    for col, args in zip(cols, metrics):
        with col:
            metric_card(*args)

    st.markdown("### Request Charging")
    col_map, col_side = st.columns([1.7, 1])
    with col_map:
        capture_user_location()
        render_user_map(float(st.session_state.user_lat), float(st.session_state.user_lng), providers, st.session_state.user_address, key="dashboard_user_map")
    with col_side:
        st.markdown("#### Vans Around You")
        if not providers:
            st.info("No charging vans found yet. Ask a driver to create a van profile and allow live location.")
        for provider in providers:
            with st.container(border=True):
                st.markdown(f"**{provider.get('vehicle_number') or 'Charging Van'}** {status_badge('online' if provider.get('is_available') else 'offline', 'Available' if provider.get('is_available') else 'Busy')}", unsafe_allow_html=True)
                st.caption(provider.get("driver_name") or "Driver")
                distance = provider.get("distance_km")
                if distance is not None:
                    st.metric("ETA", f"{estimate_eta_minutes(distance)} min", f"{distance:.2f} km")
                st.caption(f"{provider.get('charging_speed')} · {provider.get('connector_types')} · Rs {provider.get('price_per_kwh')}/kWh")
                if st.button("Request Van ⚡", key=f"request_{provider['id']}", use_container_width=True, disabled=not provider.get("is_available")):
                    create_charge_request(provider["id"])


def render_payment_selector(request_status: dict, key_prefix: str) -> None:
    provider = request_status.get("provider") or {}
    amount = float(request_status.get("total_price") or 0)
    st.markdown("#### Bill")
    render_bill_totals(request_status, provider, amount, compact=True)
    if st.button("Make payment", use_container_width=True, key=f"{key_prefix}_make_payment"):
        st.session_state.payment_gateway_request_id = request_status["id"]
        st.session_state.payment_gateway_order = None
        st.rerun()


def render_live_trip() -> None:
    if not st.session_state.active_request_id:
        st.info("No active trip right now.")
        if st.button("Go to Dashboard", use_container_width=True):
            st.session_state.user_nav_radio = "Dashboard"
            st.rerun()
        return

    request_status = load_request_status(st.session_state.active_request_id)
    if not request_status:
        st.session_state.active_request_id = None
        return

    status = request_status.get("status")
    provider = request_status.get("provider")
    toast_for_status(status, f"user_trip_{request_status['id']}")
    if status == "cancelled":
        st.session_state.active_request_id = None
        st.error("Driver rejected this request.")
        return
    if status not in ACTIVE_REQUEST_STATUSES:
        st.session_state.active_request_id = None
        st.info("This trip is finished. Previous trips are available in History.")
        return

    route_label = request_status.get("route_status_label") or status.replace("_", " ").title()
    hero("Live charging trip", f"Request #{request_status['id']} · {route_label}", "Real-time status, route tracking, billing, and payment confirmation.")
    timeline(status)

    cols = st.columns(4)
    cols[0].metric("ETA", f"{request_status.get('estimated_eta_minutes') or 'Live'} min")
    cols[1].metric("Distance", f"{float(request_status.get('estimated_distance_km') or 0):.2f} km")
    cols[2].metric("Driver", (provider or {}).get("driver_name") or "Assigned driver")
    cols[3].metric("Vehicle", (provider or {}).get("vehicle_number") or "Charging van")

    col_map, col_info = st.columns([1.6, 1])
    with col_map:
        render_trip_map(request_status["pickup_lat"], request_status["pickup_lng"], provider, key=f"live_trip_map_{request_status['id']}")
    with col_info:
        st.markdown(f"### Status {status_badge(status, route_label)}", unsafe_allow_html=True)
        if request_status.get("notification_message"):
            st.success(request_status["notification_message"])
        if status == "pending":
            st.info("Waiting for the driver to accept the request.")
        elif status in {"accepted", "en_route"}:
            st.info("Your charging van is in route. Keep your phone nearby for arrival updates.")
        elif status == "awaiting_payment":
            st.success("Charging completed. Please review and pay.")
            render_payment_selector(request_status, key_prefix=f"tracking_{request_status['id']}")
        elif status == "completed":
            st.success("Payment received.")
            st.session_state.active_request_id = None
        else:
            st.info(f"Current status: {status.replace('_', ' ').title()}")


def render_payment_gateway() -> None:
    request_id = st.session_state.get("payment_gateway_request_id")
    if not request_id:
        last_paid = st.session_state.get("last_paid_invoice")
        if last_paid:
            render_success_screen(
                float(last_paid.get("amount") or 0),
                last_paid.get("invoice_id") or "Paid",
                last_paid.get("order_id"),
            )
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button(
                    "Download invoice",
                    data=f"RunEV invoice #{last_paid.get('invoice_id')}\nAmount: {money(last_paid.get('amount'))}\nOrder: {last_paid.get('order_id')}\n",
                    file_name=f"runev_invoice_{last_paid.get('invoice_id')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with col_b:
                if st.button("Back to dashboard", use_container_width=True):
                    st.session_state.last_paid_invoice = None
                    st.session_state.user_nav_radio = "Dashboard"
                    st.rerun()
            return
        hero("Payments", "Pending bills", "Open a pending bill from Live Trips or History to continue payment.")
        pending = [req for req in load_my_requests() if req.get("status") == "awaiting_payment"]
        if not pending:
            st.info("No pending bills right now.")
            return
        for req in pending:
            with st.container(border=True):
                cols = st.columns([1.2, 0.9])
                cols[0].markdown(f"**Invoice #{req.get('id')}**")
                cols[0].caption(format_date(req.get("request_time")))
                cols[1].metric("Amount", money(req.get("total_price")))
                if st.button("Make payment", key=f"pending_payment_{req['id']}", use_container_width=True):
                    st.session_state.payment_gateway_request_id = req["id"]
                    st.session_state.payment_gateway_order = None
                    st.rerun()
        return

    request_status = load_request_status(request_id)
    if not request_status:
        st.session_state.payment_gateway_request_id = None
        return
    if request_status.get("status") == "completed":
        render_success_screen(amount := float(request_status.get("total_price") or 0), request_id, st.session_state.payment_gateway_order.get("order_id") if st.session_state.get("payment_gateway_order") else None)
        st.session_state.payment_gateway_request_id = None
        st.session_state.payment_gateway_order = None
        if st.button("Back to dashboard", use_container_width=True, key=f"paid_back_{request_id}"):
            st.session_state.user_nav_radio = "Dashboard"
            st.rerun()
        return

    provider = request_status.get("provider") or {}
    amount = float(request_status.get("total_price") or 0)
    if request_status.get("status") != "awaiting_payment" or amount <= 0:
        hero("Payment", f"Invoice #{request_id}", "Your bill is not ready yet. Please wait for the driver to complete charging.")
        timeline(request_status.get("status"))
        st.info("Payment will unlock once charging is completed and the driver generates the bill.")
        return

    if not st.session_state.payment_gateway_order or st.session_state.payment_gateway_order.get("request_id") != request_id:
        order = create_payment_order(request_id)
        if not order:
            return
        order["request_id"] = request_id
        st.session_state.payment_gateway_order = order

    order = st.session_state.payment_gateway_order
    hero("Payment", f"Invoice #{request_id}", "Complete your bill and close the charging session.")
    timeline("awaiting_payment")

    col_bill, col_payment = st.columns([1.05, 1], gap="large")
    with col_bill:
        render_driver_card(provider, eta=request_status.get("estimated_eta_minutes") or "Live")
        render_charging_summary(request_status, provider, amount)
        st.markdown("#### Live route")
        render_trip_map(request_status["pickup_lat"], request_status["pickup_lng"], provider, key=f"payment_trip_map_{request_status['id']}")

    with col_payment:
        st.markdown(
            f"""
            <div class="runev-pay-panel">
                <span>Amount due</span>
                <strong>{money(order.get("amount"))}</strong>
                <p>Invoice #{request_id} / Order {safe_text(order.get("order_id"))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("#### Choose payment method")
        method = st.radio(
            "Payment mode",
            ["UPI", "Cash", "Other payment options"],
            horizontal=True,
            key=f"gateway_method_{request_id}",
            help="Scan UPI QR, pay cash to the driver, or use Razorpay checkout.",
        )
        if method == "UPI":
            st.markdown(
                f"""
                <div class="runev-manual-upi-card">
                    <div>
                        <span>UPI QR payment</span>
                        <strong>Scan with any UPI app</strong>
                        <p>Use Google Pay, PhonePe, Paytm, BHIM, or any UPI app to pay {money(order.get("amount"))}.</p>
                    </div>
                    {sample_upi_qr("runev@upi")}
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("I have paid with UPI", use_container_width=True, key=f"gateway_upi_confirm_{request_id}"):
                st.session_state.last_paid_invoice = {"invoice_id": request_id, "amount": amount, "order_id": "UPI QR"}
                choose_payment_method(request_id, "UPI")
        elif method == "Cash":
            st.info("Collect the cash payment with the driver, then confirm to close this bill.")
            if st.button("Confirm cash payment", use_container_width=True, key=f"gateway_cash_{request_id}"):
                st.session_state.last_paid_invoice = {"invoice_id": request_id, "amount": amount, "order_id": "Cash"}
                choose_payment_method(request_id, "CASH")
        elif order.get("gateway") == "mock":
            render_secure_payment_note()
            st.info("Demo Razorpay checkout is ready. Press Pay Securely to simulate a successful payment.")
            if st.button(
                f"Pay Securely - {money(order.get('amount'))}",
                use_container_width=True,
                key=f"gateway_pay_{request_id}",
            ):
                verify_gateway_payment(order)
        else:
            render_secure_payment_note()
            st.info("Use Razorpay checkout for card, UPI, netbanking, wallet, or pay later.")
            render_razorpay_checkout(order, request_status, method)
        if st.button("Back to live trip", use_container_width=True, key=f"gateway_back_{request_id}"):
            st.session_state.payment_gateway_request_id = None
            st.session_state.payment_gateway_order = None
            st.rerun()


def render_history() -> None:
    requests_list = load_my_requests()
    hero("History", "Charging sessions", "Past requests, bills, payment state, and driver information.")
    if not requests_list:
        st.info("No previous charging requests yet.")
        return
    for req in requests_list:
        provider = req.get("provider") or {}
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([1.4, 1, 0.8])
            col_a.markdown(f"**{provider.get('vehicle_number') or 'Charging Van'}**")
            col_a.caption(provider.get("driver_name") or "Driver")
            col_b.markdown(status_badge(req.get("status")), unsafe_allow_html=True)
            col_b.caption(format_date(req.get("request_time")))
            col_c.metric("Amount", money(req.get("total_price")))
            if req.get("status") == "awaiting_payment":
                with st.expander("Complete payment", expanded=True):
                    render_payment_selector(req, key_prefix=f"history_{req['id']}")


def render_analytics() -> None:
    requests_list = load_my_requests()
    providers = load_all_providers(float(st.session_state.user_lat), float(st.session_state.user_lng))
    hero("Analytics", "Personal EV charging intelligence", "Spend, usage, charging volume, peak hours, and future forecasting surfaces.")
    render_operations_analytics(requests_list, providers)
    st.markdown("#### Advanced Intelligence")
    col_a, col_b, col_c, col_d = st.columns(4)
    for col, item in zip(
        [col_a, col_b, col_c, col_d],
        [("AI ETA Prediction", "Ready for model hook"), ("Smart Dispatch", "Policy placeholder"), ("Battery Intelligence", "SOC-ready schema"), ("Demand Forecasting", "Trend pipeline ready")],
    ):
        with col:
            metric_card(item[0], item[1], "✨", "architecture placeholder")


def render_settings() -> None:
    user = st.session_state.user
    hero("Settings", "Account and preferences", "Manage passenger profile information without changing backend contracts.")
    with st.form("user_profile_form"):
        username = st.text_input("Name", value=user.get("username") or "")
        st.text_input("Email", value=user.get("email") or "", disabled=True)
        phone = st.text_input("Phone", value=user.get("phone") or "")
        if st.form_submit_button("Save Profile", use_container_width=True):
            try:
                updated = api_client.update_me(st.session_state.get("jwt_token"), username=username, phone=phone)
                st.session_state.user.update({"username": updated["username"], "email": updated["email"], "role": updated["role"], "phone": updated.get("phone")})
                st.success("Profile saved.")
            except api_client.ApiError as exc:
                st.error(str(exc))


def main() -> None:
    init_state()
    render_live_notification()
    if st.session_state.user is None:
        render_login()
        return

    sync_active_request_from_backend()
    nav = render_sidebar()
    if st.session_state.get("payment_gateway_request_id"):
        render_payment_gateway()
    elif nav == "Dashboard":
        render_dashboard()
    elif nav == "Live Trips":
        render_live_trip()
    elif nav == "Analytics":
        render_analytics()
    elif nav == "Payments":
        render_payment_gateway()
    elif nav == "History":
        render_history()
    else:
        render_settings()


main()
