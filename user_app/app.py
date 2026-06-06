from __future__ import annotations

import html
import json
import math
import os
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

import requests
import textwrap
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from frontend.components.analytics import render_operations_analytics
from frontend.components.auth import render_auth_divider
from frontend.components.theme import (
    apply_theme_runtime,
    init_theme_state,
    persist_theme_preference,
    render_theme_selector,
    restore_theme_preferences,
)
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
from frontend.utils import supabase_auth
from frontend.utils.live import auto_refresh, push_notification, render_live_notification, toast_for_status
from utils import api_client

from frontend.components.geolocation import live_location_button, validate_coordinates
from backend.core.validation import normalize_email, password_strength, validate_full_name, validate_password


def clean_html(html_str: str) -> str:
    import re
    no_comments = re.sub(r"<!--.*?-->", "", html_str, flags=re.DOTALL)
    return " ".join(no_comments.split())


def get_image_or_fallback(filename: str) -> str | None:
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if os.path.exists(path):
            return path
        if os.path.exists(filename):
            return filename
    except Exception:
        pass
    return None



def inject_premium_user_styles() -> None:
    css_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "styles", "premium_user.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


configure_page("RunEV - User App", "⚡")
inject_global_styles()
inject_premium_user_styles()
init_theme_state()
apply_theme_runtime()

ACTIVE_REQUEST_STATUSES = {"pending", "accepted", "en_route", "arrived", "charging", "awaiting_payment"}
SUPABASE_PKCE_STORAGE_KEY = "runev.supabase.pkce_verifier"
RUNEV_SESSION_STORAGE_KEY = "runev.user.jwt"
DEFAULT_PROVIDER_LOCATION = (18.5204, 73.8567)
LOCAL_TIMEZONE = ZoneInfo("Asia/Kolkata")


def is_default_location(latitude: float | None, longitude: float | None) -> bool:
    if latitude is None or longitude is None:
        return True
    try:
        return round(float(latitude), 4) == 18.5204 and round(float(longitude), 4) == 73.8567
    except (TypeError, ValueError):
        return True


def init_state() -> None:
    defaults = {
        "user": None,
        "jwt_token": None,
        "supabase_session": None,
        "user_lat": 18.5204,
        "user_lng": 73.8567,
        "user_address": "Detecting your live pickup location",
        "user_location_accuracy": None,
        "user_location_captured": False,
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
            timeout=5,
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
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(LOCAL_TIMEZONE).strftime("%d %b, %I:%M %p")
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
        try:
            lat_value, lng_value, _ = validate_coordinates(lat, lng)
        except ValueError:
            continue
        if (
            round(lat_value, 4) == DEFAULT_PROVIDER_LOCATION[0]
            and round(lng_value, 4) == DEFAULT_PROVIDER_LOCATION[1]
            and "pune" not in str(provider.get("address") or "").lower()
        ):
            continue
        distance = calculate_distance(user_lat, user_lng, lat_value, lng_value) if user_lat is not None and user_lng is not None else None
        rows.append(
            {
                **provider,
                "current_lat": lat_value,
                "current_lng": lng_value,
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
        pickup_lat, pickup_lng, _ = validate_coordinates(st.session_state.user_lat, st.session_state.user_lng)
    except ValueError as exc:
        st.error(f"Pickup location is invalid: {exc}")
        return
    if not st.session_state.get("user_location_captured"):
        st.error("Please click Use My Live Location and allow location access before requesting a van.")
        return
    if is_default_location(pickup_lat, pickup_lng):
        st.error("Pickup is still set to the default Pune location. Please share your live location again.")
        return
    try:
        data = api_client.request_json(
            "POST",
            "/api/v1/requests/charge",
            token=st.session_state.get("jwt_token"),
            json={
                "user_id": st.session_state.user["id"],
                "provider_id": provider_id,
                "pickup_lat": pickup_lat,
                "pickup_lng": pickup_lng,
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
        st.session_state.payment_gateway_request_id = None
        st.session_state.payment_gateway_order = None
        st.error(f"Payment could not be opened: {exc}")
        if st.button("Back to pending bills", use_container_width=True, key=f"payment_order_error_back_{request_id}"):
            st.rerun()
        return None


def submit_rating(request_id: int, score: int, comment: str | None = None) -> bool:
    try:
        api_client.request_json(
            "POST",
            "/api/v1/ratings",
            token=st.session_state.get("jwt_token"),
            json={"request_id": request_id, "score": score, "comment": comment or None},
        )
        st.session_state[f"rating_submitted_{request_id}"] = True
        push_notification("Thanks for rating your driver", "success")
        st.rerun()
        return True
    except api_client.ApiError as exc:
        st.error(str(exc))
        return False


def provider_rating_label(provider: dict) -> str:
    average = provider.get("average_rating")
    count = int(provider.get("rating_count") or 0)
    if average is None or count == 0:
        return "No ratings yet"
    return f"{float(average):.1f}/5 from {count} rating{'s' if count != 1 else ''}"


def render_rating_form(request_status: dict, key_prefix: str) -> None:
    request_id = request_status.get("id")
    provider = request_status.get("provider") or {}
    if not request_id or request_status.get("status") != "completed" or not provider:
        return
    if st.session_state.get(f"rating_submitted_{request_id}"):
        st.success("Your rating has been saved.")
        return

    st.markdown("#### Rate your charging experience")
    st.caption(f"{provider.get('driver_name') or 'Driver'} / {provider.get('vehicle_number') or 'Charging van'}")
    with st.form(f"{key_prefix}_rating_form_{request_id}"):
        score = st.slider("Rating", min_value=1, max_value=5, value=5, key=f"{key_prefix}_rating_score_{request_id}")
        comment = st.text_area("Comment", max_chars=1000, key=f"{key_prefix}_rating_comment_{request_id}")
        if st.form_submit_button("Submit rating", use_container_width=True):
            submit_rating(request_id, score, comment.strip())


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
    breakdown = request_status.get("fare_breakdown") or {}
    rate = float(breakdown.get("charging_rate_per_kwh") or provider.get("price_per_kwh") or 20)
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
                    <span style="color:#cbd5e1;font-weight:800;">Base visit</span>
                    <strong style="color:#f8fafc;text-align:right;">{money(breakdown.get('base_visit_fee') or 0)}</strong>
                </div>
                <div style="display:flex;justify-content:space-between;gap:16px;border-bottom:1px solid rgba(148,163,184,.14);padding-bottom:10px;">
                    <span style="color:#cbd5e1;font-weight:800;">Distance</span>
                    <strong style="color:#f8fafc;text-align:right;">{money(breakdown.get('distance_charge') or 0)}</strong>
                </div>
                <div style="display:flex;justify-content:space-between;gap:16px;border-bottom:1px solid rgba(148,163,184,.14);padding-bottom:10px;">
                    <span style="color:#cbd5e1;font-weight:800;">Charging</span>
                    <strong style="color:#f8fafc;text-align:right;">{money(breakdown.get('charging_cost') or 0)}</strong>
                </div>
                <div style="display:flex;justify-content:space-between;gap:16px;border-bottom:1px solid rgba(148,163,184,.14);padding-bottom:10px;">
                    <span style="color:#cbd5e1;font-weight:800;">Platform</span>
                    <strong style="color:#f8fafc;text-align:right;">{money(breakdown.get('platform_fee') or 0)}</strong>
                </div>
                <div style="display:flex;justify-content:space-between;gap:16px;border-bottom:1px solid rgba(148,163,184,.14);padding-bottom:10px;">
                    <span style="color:#cbd5e1;font-weight:800;">Emergency / Night</span>
                    <strong style="color:#f8fafc;text-align:right;">{money((breakdown.get('emergency_fee') or 0) + (breakdown.get('night_fee') or 0))}</strong>
                </div>
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
    capture_key = "capture_user_location"
    if st.session_state.pop("sync_user_address_input", False):
        st.session_state.user_address_input = st.session_state.user_address
    else:
        st.session_state.setdefault("user_address_input", st.session_state.user_address)
    st.session_state.user_address = st.text_input("Pickup address", key="user_address_input")

    location = live_location_button("Use My Live Location", key=capture_key)
    if not location:
        return
    if location.get("error"):
        st.warning(str(location["error"]))
        return

    try:
        latitude, longitude, accuracy = validate_coordinates(
            location.get("latitude"),
            location.get("longitude"),
            location.get("accuracy"),
        )
    except ValueError as exc:
        st.warning(str(exc))
        return

    location_key = f"{latitude}:{longitude}:{accuracy}:{location.get('timestamp')}"
    if st.session_state.get("last_user_location_key") == location_key:
        return

    st.session_state.last_user_location_key = location_key
    st.session_state.user_lat = latitude
    st.session_state.user_lng = longitude
    st.session_state.user_location_accuracy = accuracy
    st.session_state.user_location_captured = True
    fallback_address = f"Live pickup: {latitude:.6f}, {longitude:.6f}"
    st.session_state.user_address = reverse_geocode(latitude, longitude, fallback_address)
    st.session_state.sync_user_address_input = True
    push_notification("Pickup location updated", "success")
    st.rerun()


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
    persist_user_session(token)
    restore_theme_preferences(token)
    st.rerun()


def persist_user_session(token: str | None = None) -> None:
    token = token or st.session_state.get("jwt_token")
    if not token:
        return
    components.html(
        f"""
        <script>
        try {{ window.parent.localStorage.setItem({json.dumps(RUNEV_SESSION_STORAGE_KEY)}, {json.dumps(str(token))}); }} catch (_) {{}}
        </script>
        """,
        height=0,
        width=0,
    )


def recover_user_session() -> None:
    query_token = st.query_params.get("runev_token")
    if isinstance(query_token, list):
        query_token = query_token[0]
    if query_token:
        try:
            clear_auth_query_params()
            complete_login(str(query_token))
        except api_client.ApiError:
            clear_user_session()
        return
    components.html(
        f"""
        <script>
        (() => {{
            const url = new URL(window.parent.location.href);
            if (url.searchParams.has("runev_token")) return;
            let token = "";
            try {{ token = window.parent.localStorage.getItem({json.dumps(RUNEV_SESSION_STORAGE_KEY)}) || ""; }} catch (_) {{}}
            if (token) {{
                url.searchParams.set("runev_token", token);
                window.parent.location.replace(url.toString());
            }}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def clear_user_session() -> None:
    st.session_state.user = None
    st.session_state.jwt_token = None
    st.session_state.supabase_session = None
    components.html(
        f"""
        <script>
        try {{ window.parent.localStorage.removeItem({json.dumps(RUNEV_SESSION_STORAGE_KEY)}); }} catch (_) {{}}
        </script>
        """,
        height=0,
        width=0,
    )


def complete_supabase_login(session: dict) -> None:
    access_token = session.get("access_token")
    if not access_token:
        st.session_state.auth_error = "Supabase did not return a valid session."
        return
    token_data = api_client.login_with_supabase(access_token, session.get("refresh_token"))
    st.session_state.supabase_session = {
        "access_token": access_token,
        "refresh_token": session.get("refresh_token"),
        "expires_at": session.get("expires_at"),
        "token_type": session.get("token_type"),
        "provider_token": session.get("provider_token"),
    }
    complete_login(token_data["access_token"])


def clear_auth_query_params() -> None:
    try:
        st.query_params.clear()
    except Exception:
        pass


def persist_supabase_pkce_verifier(verifier: str | None = None) -> None:
    verifier = verifier or st.session_state.get("supabase_code_verifier")
    if not verifier:
        return
    components.html(
        f"""
        <script>
        (() => {{
            try {{
                window.parent.localStorage.setItem({json.dumps(SUPABASE_PKCE_STORAGE_KEY)}, {json.dumps(str(verifier))});
            }} catch (_) {{}}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def recover_supabase_pkce_verifier() -> None:
    components.html(
        f"""
        <script>
        (() => {{
            const key = {json.dumps(SUPABASE_PKCE_STORAGE_KEY)};
            const url = new URL(window.parent.location.href);
            const hasCallback = url.searchParams.has("code") || url.searchParams.has("token_hash");
            if (!hasCallback || url.searchParams.has("runev_verifier")) {{
                return;
            }}
            let verifier = "";
            try {{
                verifier = window.parent.localStorage.getItem(key) || "";
            }} catch (_) {{}}
            if (!verifier) {{
                url.searchParams.set("runev_verifier_missing", "1");
                window.parent.location.replace(url.toString());
                return;
            }}
            url.searchParams.set("runev_verifier", verifier);
            window.parent.location.replace(url.toString());
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def clear_supabase_pkce_verifier() -> None:
    components.html(
        f"""
        <script>
        (() => {{
            try {{
                window.parent.localStorage.removeItem({json.dumps(SUPABASE_PKCE_STORAGE_KEY)});
            }} catch (_) {{}}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def expose_supabase_hash_tokens() -> None:
    components.html(
        """
        <script>
        (() => {
            const url = new URL(window.parent.location.href);
            if (!window.parent.location.hash || url.searchParams.has("supabase_access_token")) return;
            const hash = new URLSearchParams(window.parent.location.hash.slice(1));
            const accessToken = hash.get("access_token");
            if (!accessToken) return;
            url.hash = "";
            url.searchParams.set("supabase_access_token", accessToken);
            url.searchParams.set("supabase_refresh_token", hash.get("refresh_token") || "");
            url.searchParams.set("supabase_type", hash.get("type") || "");
            window.parent.location.replace(url.toString());
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def render_supabase_recovery_if_present() -> bool:
    expose_supabase_hash_tokens()
    access_token = st.query_params.get("supabase_access_token")
    recovery_type = st.query_params.get("supabase_type")
    if isinstance(access_token, list):
        access_token = access_token[0]
    if isinstance(recovery_type, list):
        recovery_type = recovery_type[0]
    if not access_token or recovery_type != "recovery":
        return False

    st.markdown('<div class="runev-auth-page"></div>', unsafe_allow_html=True)
    _, col_form, _ = st.columns([1, 0.62, 1], gap="large")
    with col_form:
        st.markdown("### Create New Password")
        with st.form("supabase_recovery_password_form"):
            password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if password:
                st.caption(f"Password strength: {password_strength(password)}")
            if st.form_submit_button("Update Password", use_container_width=True):
                try:
                    validate_password(password)
                    if password != confirm_password:
                        raise ValueError("Confirm password must match password.")
                    supabase_auth.update_password(str(access_token), password)
                    clear_auth_query_params()
                    st.success("Password updated. Sign in with your new password.")
                except (ValueError, supabase_auth.SupabaseAuthError) as exc:
                    st.error(str(exc))
    return True


def handle_supabase_auth_callback() -> None:
    query_params = st.query_params
    code = query_params.get("code")
    error = query_params.get("error_description") or query_params.get("error")
    callback_verifier = query_params.get("runev_verifier")
    verifier_missing = query_params.get("runev_verifier_missing")
    if isinstance(code, list):
        code = code[0]
    if isinstance(error, list):
        error = error[0]
    if isinstance(callback_verifier, list):
        callback_verifier = callback_verifier[0]
    if isinstance(verifier_missing, list):
        verifier_missing = verifier_missing[0]

    if error:
        st.session_state.auth_error = str(error)
        clear_auth_query_params()
        return
    if not code:
        return

    code_verifier = st.session_state.get("supabase_code_verifier") or callback_verifier
    if not code_verifier:
        if verifier_missing:
            st.session_state.auth_error = "Sign in expired. Please start again from this tab."
            st.session_state.auth_loading = None
            clear_auth_query_params()
            return
        st.session_state.auth_loading = "Completing secure sign in..."
        st.session_state.auth_error = None
        st.info("Completing secure sign in...")
        recover_supabase_pkce_verifier()
        st.stop()

    st.session_state.auth_loading = "Completing secure sign in..."
    try:
        session = supabase_auth.exchange_code_for_session(str(code), str(code_verifier))
        st.session_state.pop("supabase_code_verifier", None)
        st.session_state.pop("supabase_pending_verifier", None)
        st.session_state.pop("google_oauth_url", None)
        st.session_state.pop("auth_error", None)
        clear_auth_query_params()
        clear_supabase_pkce_verifier()
        complete_supabase_login(session)
    except (supabase_auth.SupabaseAuthError, api_client.ApiError) as exc:
        st.session_state.auth_error = str(exc)
        clear_auth_query_params()
    finally:
        st.session_state.auth_loading = None


def supabase_callback_url(code_verifier: str) -> str:
    url = urlsplit(supabase_auth.app_url())
    query = dict(parse_qsl(url.query, keep_blank_values=True))
    query["runev_verifier"] = code_verifier
    return urlunsplit((url.scheme, url.netloc, url.path, urlencode(query), url.fragment))


def prepare_supabase_google_login() -> str:
    verifier, challenge = supabase_auth.create_pkce_pair()
    st.session_state.supabase_code_verifier = verifier
    persist_supabase_pkce_verifier(verifier)
    return supabase_auth.google_oauth_url(supabase_callback_url(verifier), challenge)


def send_supabase_magic_link(email: str) -> None:
    verifier, challenge = supabase_auth.create_pkce_pair()
    st.session_state.supabase_code_verifier = verifier
    st.session_state.supabase_pending_verifier = verifier
    supabase_auth.send_magic_link(email, supabase_callback_url(verifier), challenge)
    st.session_state.auth_email_sent = email


def render_login() -> None:
    persist_supabase_pkce_verifier(st.session_state.get("supabase_pending_verifier"))
    if render_supabase_recovery_if_present():
        return
    recover_user_session()
    handle_supabase_auth_callback()
    if st.session_state.get("auth_loading") == "Opening Google...":
        st.session_state.auth_loading = None
    # Read query parameter for forgot password / views
    auth_view = st.query_params.get("auth_view", "login")
    
    # Global Header with runev-auth-page class
    st.markdown(
        textwrap.dedent("""
        <div class="runev-auth-page" style="display:none;"></div>
        <div class="premium-header brand-header">
            <div class="logo-container">
                <div class="runev-logo">RunEV<span>.</span></div>
                <span class="user-app-badge app-badge">USER APP</span>
            </div>
            <a href="mailto:support@runev.com" class="help-btn">Need help? 💬</a>
        </div>
        """),
        unsafe_allow_html=True,
    )
    
    # Split Layout columns: 35% Left, 65% Right
    col_left, col_right = st.columns([0.35, 0.65], gap="large")
    st.markdown("""
<style>
.block-container{
    padding-top:0rem !important;
}
</style>
""", unsafe_allow_html=True)
    
    with col_left:
        st.markdown(
            textwrap.dedent("""
            <div class="small-label">ON-DEMAND EV CHARGING</div>
            <h1 class="main-title hero-title">Run Out of Charge?<br><span>RunEV Comes To You. ⚡</span></h1>
            <p class="supporting-text">Request a charging van in minutes, track it live, pay securely, and continue your trip without waiting.</p>
            """),
            unsafe_allow_html=True,
        )
        
        # Feature cards
        st.markdown(
            textwrap.dedent("""
            <div class="feature-cards-container" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 15px;">
                <div class="feature-card green-card" style="padding: 10px 12px; display: flex; flex-direction: row; align-items: center; gap: 10px; background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px;">
                    <div class="feature-icon-wrapper" style="width: 28px; height: 28px; font-size: 14px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: rgba(16, 185, 129, 0.15); color: #10b981; min-width: 28px;">⚡</div>
                    <div style="display: flex; flex-direction: column; text-align: left;">
                        <h4 class="feature-title" style="font-size: 14px; margin: 0; font-weight: 700; color: #FFFFFF; line-height: 1.2;">Fast Response</h4>
                    </div>
                </div>
                <div class="feature-card blue-card" style="padding: 10px 12px; display: flex; flex-direction: row; align-items: center; gap: 10px; background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px;">
                    <div class="feature-icon-wrapper" style="width: 28px; height: 28px; font-size: 14px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: rgba(139, 92, 246, 0.15); color: #8b5cf6; min-width: 28px;">📍</div>
                    <div style="display: flex; flex-direction: column; text-align: left;">
                        <h4 class="feature-title" style="font-size: 14px; margin: 0; font-weight: 700; color: #FFFFFF; line-height: 1.2;">Live Tracking</h4>
                        <p class="feature-desc" style="font-size: 11px; margin: 0; color: #94A3B8; line-height: 1.2;">Track your charging van in real time</p>
                    </div>
                </div>
                <div class="feature-card purple-card" style="padding: 10px 12px; display: flex; flex-direction: row; align-items: center; gap: 10px; background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px;">
                    <div class="feature-icon-wrapper" style="width: 28px; height: 28px; font-size: 14px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: rgba(59, 130, 246, 0.15); color: #3b82f6; min-width: 28px;">🧭</div>
                    <div style="display: flex; flex-direction: column; text-align: left;">
                        <h4 class="feature-title" style="font-size: 14px; margin: 0; font-weight: 700; color: #FFFFFF; line-height: 1.2;">Track Map</h4>
                        <p class="feature-desc" style="font-size: 11px; margin: 0; color: #94A3B8; line-height: 1.2;">Track Map in real time</p>
                    </div>
                </div>
                <div class="feature-card purple-card" style="padding: 10px 12px; display: flex; flex-direction: row; align-items: center; gap: 10px; background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px;">
                    <div class="feature-icon-wrapper" style="width: 28px; height: 28px; font-size: 14px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: rgba(59, 130, 246, 0.15); color: #3b82f6; min-width: 28px;">🛡️</div>
                    <div style="display: flex; flex-direction: column; text-align: left;">
                        <h4 class="feature-title" style="font-size: 14px; margin: 0; font-weight: 700; color: #FFFFFF; line-height: 1.2;">Secure Payments</h4>
                        <p class="feature-desc" style="font-size: 11px; margin: 0; color: #94A3B8; line-height: 1.2;">UPI, Cards, Wallets</p>
                    </div>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )
        
        auth_error = st.session_state.get("auth_error")
        if isinstance(auth_error, str) and auth_error.startswith("Invalid Supabase anon key"):
            st.session_state.pop("auth_error", None)
            auth_error = None
        auth_loading = st.session_state.get("auth_loading")
        if auth_loading:
            st.info(auth_loading)
        if auth_error:
            st.error(auth_error)
            
        supabase_config_error = supabase_auth.config_error()
        if supabase_config_error:
            st.session_state.pop("google_oauth_url", None)
            st.info("Authentication setup required. Add a valid Supabase public anon key in .env, then restart RunEV.")
        else:
            if auth_view == "forgot":
                # Forgot Password Card
                st.markdown('<h3 style="margin-top:0; font-size: 22px; font-weight: 800; color: #FFFFFF;">Forgot Password?</h3>', unsafe_allow_html=True)
                st.markdown('<p class="supporting-text">Enter your email below to receive a password reset link.</p>', unsafe_allow_html=True)
                
                with st.form("forgot_password_form"):
                    forgot_email = st.text_input("Email Address", key="user_forgot_email", placeholder="Enter your email")
                    
                    submit_forgot = st.form_submit_button("Send Reset Link", use_container_width=True)
                    if submit_forgot:
                        try:
                            normalized_email = normalize_email(forgot_email)
                            supabase_auth.send_password_reset(normalized_email, redirect_to=supabase_auth.app_url())
                            st.success("Password reset link sent. Check your email inbox.")
                        except (ValueError, supabase_auth.SupabaseAuthError) as exc:
                            st.error(str(exc))
                            
                st.markdown(
                    textwrap.dedent("""
                    <div class="bottom-auth-section">
                        Already have an account? <a href="?auth_view=login" target="_self">Login</a>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )
            else:
                # Regular Auth Container with Tabs
                pass
                tab_login, tab_signup, tab_magic = st.tabs(["Login", "Sign Up", "Passwordless Login"])
                
                with tab_login:
                    google_url = st.session_state.get("google_oauth_url") or prepare_supabase_google_login()
                    st.session_state.google_oauth_url = google_url
                    st.link_button("Continue with Google", google_url, use_container_width=True, disabled=bool(auth_loading))
                    
                    st.markdown('<div class="premium-divider">OR</div>', unsafe_allow_html=True)
                    
                    # Passwordless Login Form inside the same tab
                    st.markdown('<div class="magic-link-form-wrap">', unsafe_allow_html=True)
                    with st.form("user_magic_link_form_login"):
                        magic_email = st.text_input("Email Address", key="user_login_magic_email", placeholder="Enter your email")
                        magic_submit = st.form_submit_button("Send Magic Link", use_container_width=True, disabled=bool(auth_loading))
                        if magic_submit:
                            try:
                                normalized_email = normalize_email(magic_email)
                                send_supabase_magic_link(normalized_email)
                                st.success("Sign-in link sent. Open the email on this device to finish signing in.")
                            except (ValueError, supabase_auth.SupabaseAuthError) as exc:
                                st.error(str(exc))
                    st.markdown('</div>', unsafe_allow_html=True)
                                
                    st.markdown('<div class="premium-divider">OR</div>', unsafe_allow_html=True)
                    st.markdown('<div class="passwordless-helper-text" style="font-weight: 800; font-size: 15px; margin-bottom: 8px; color: #FFFFFF;">Password Login</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="password-login-form-wrap">', unsafe_allow_html=True)
                    with st.form("user_password_login_form"):
                        email = st.text_input("Email Address", key="user_login_email", placeholder="Enter your email")
                        password = st.text_input("Password", key="user_login_password", type="password", placeholder="Enter your password")
                        
                        # Remember me & Forgot Password Row
                        st.markdown('<div class="remember-forgot-row">', unsafe_allow_html=True)
                        col_chk, col_lnk = st.columns([1.1, 0.9])
                        with col_chk:
                            st.checkbox("Remember me", key="user_remember_me")
                        with col_lnk:
                            st.markdown(
                                textwrap.dedent("""
                                <div class="forgot-password-btn-wrap" style="text-align: right; width:100%;">
                                    <a href="?auth_view=forgot" target="_self" style="color: #00E5A8; font-size: 13px; font-weight: 600; text-decoration: none;">Forgot Password?</a>
                                </div>
                                """),
                                unsafe_allow_html=True,
                            )
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        submit = st.form_submit_button("Login to RunEV  →", use_container_width=True, disabled=bool(auth_loading))
                        if submit:
                            try:
                                normalized_email = normalize_email(email)
                                if not password:
                                    raise ValueError("Enter your password.")
                                token_data = api_client.login(normalized_email, password)
                                complete_login(token_data["access_token"])
                            except (ValueError, api_client.ApiError) as exc:
                                st.error(str(exc))
                    st.markdown('</div>', unsafe_allow_html=True)
                                
                    st.markdown(
                        textwrap.dedent("""
                        <div class="bottom-auth-section" style="margin-top: 16px; text-align: center;">
                            <span style="color: #94A3B8; font-size: 14px; display: block; margin-bottom: 4px;">Don't have an account yet?</span>
                            <a href="?auth_view=signup" target="_self" style="color: #00E5A8; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-block;">Create Free Account →</a>
                        </div>
                        """),
                        unsafe_allow_html=True,
                    )
                    
                with tab_signup:
                    google_url = st.session_state.get("google_oauth_url") or prepare_supabase_google_login()
                    st.session_state.google_oauth_url = google_url
                    st.link_button("Continue with Google", google_url, use_container_width=True, disabled=bool(auth_loading))
                    
                    st.markdown('<div class="premium-divider">OR</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="signup-form-wrap">', unsafe_allow_html=True)
                    with st.form("user_signup_form"):
                        name = st.text_input("Full Name", key="user_signup_name", placeholder="Enter your full name")
                        email = st.text_input("Email Address", key="user_signup_email", placeholder="Enter your email")
                        password = st.text_input("Password", key="user_signup_password", type="password", placeholder="Create password")
                        confirm_password = st.text_input("Confirm Password", key="user_signup_confirm", type="password", placeholder="Confirm password")
                        
                        if password:
                            st.caption(f"Password strength: {password_strength(password)}")
                            
                        signup_errors = []
                        for validator in (
                            lambda: validate_full_name(name),
                            lambda: normalize_email(email),
                            lambda: validate_password(password) if password else (_ for _ in ()).throw(ValueError("Password is required.")),
                            lambda: None if password == confirm_password else (_ for _ in ()).throw(ValueError("Confirm password must match password.")),
                        ):
                            try:
                                validator()
                            except ValueError as exc:
                                signup_errors.append(str(exc))
                                
                        for message in signup_errors[:2]:
                            st.caption(message)
                            
                        submit_signup = st.form_submit_button("Create Account", use_container_width=True, disabled=bool(auth_loading))
                        if submit_signup:
                            if signup_errors:
                                st.error(signup_errors[0])
                            else:
                                try:
                                    normalized_name = validate_full_name(name)
                                    normalized_email = normalize_email(email)
                                    validate_password(password)
                                    if password != confirm_password:
                                        raise ValueError("Confirm password must match password.")
                                    api_client.register(normalized_name, normalized_email, password, confirm_password=confirm_password)
                                    token_data = api_client.login(normalized_email, password)
                                    st.success("Account created.")
                                    complete_login(token_data["access_token"])
                                except (ValueError, api_client.ApiError) as exc:
                                    st.error(str(exc))
                    st.markdown('</div>', unsafe_allow_html=True)
                                    
                    st.markdown(
                        textwrap.dedent("""
                        <div class="bottom-auth-section">
                            Already have an account? <a href="?auth_view=login" target="_self">Login</a>
                        </div>
                        """),
                        unsafe_allow_html=True,
                    )
                    
                with tab_magic:
                    st.markdown('<div class="magic-link-form-wrap">', unsafe_allow_html=True)
                    with st.form("user_magic_link_form"):
                        magic_email = st.text_input("Email Address", key="user_magic_email", placeholder="Enter your email")
                        
                        magic_submit = st.form_submit_button("Send Sign-in Link", use_container_width=True, disabled=bool(auth_loading))
                        if magic_submit:
                            try:
                                normalized_email = normalize_email(magic_email)
                                send_supabase_magic_link(normalized_email)
                                st.success("Sign-in link sent. Open the email on this device to finish signing in.")
                            except (ValueError, supabase_auth.SupabaseAuthError) as exc:
                                st.error(str(exc))
                    st.markdown('</div>', unsafe_allow_html=True)
                                
                    if st.session_state.get("auth_email_sent"):
                        st.success(f"Sign-in link sent to {st.session_state.auth_email_sent}.")
                        
                    st.markdown(
                        textwrap.dedent("""
                        <div class="bottom-auth-section" style="margin-top: 16px; text-align: center;">
                            <span style="color: #94A3B8; font-size: 14px; display: block; margin-bottom: 4px;">Don't have an account yet?</span>
                            <a href="?auth_view=signup" target="_self" style="color: #00E5A8; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-block;">Create Free Account →</a>
                        </div>
                        """),
                        unsafe_allow_html=True,
                    )
                        
                # Left column footer copyright
                st.markdown(
                    textwrap.dedent("""
                    <div style="width: 100%; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 15px; margin-top: 25px; text-align: center; font-size: 12px; color: #94a3b8;">
                        © 2024 RunEV. All rights reserved.
                    </div>
                    """),
                    unsafe_allow_html=True,
                )
                pass
        
    with col_right:
        # Right panel header
        st.markdown(
            textwrap.dedent("""
            <div class="right-panel-header">
                <div class="trust-badge">
                    <span class="trust-badge-icon">✓</span> Trusted by <span>10K+</span> EV owners across India
                </div>
                <div class="right-panel-title">Your Charging Van is on the Way</div>
                <div class="right-panel-subtitle">Reliable. Fast. On-Demand.</div>
            </div>
            """),
            unsafe_allow_html=True,
        )
        
        # Render the large premium EV visual image robustly
        hero_img = get_image_or_fallback("hero_visual.png")
        if hero_img:
            st.image(hero_img, use_column_width=True)
        else:
            st.info("⚡ RunEV Hero Visual Placeholder")
        
        # Live status dashboard layout
        dashboard_html = """
        <!-- Live Tracking Card -->
        <div class="dash-card tracking-card text-tracking-card" style="width: 100%; min-height: 110px; margin-bottom: 12px; display: flex; flex-direction: column; justify-content: space-between; padding: 12px 16px; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; background: rgba(15, 23, 42, 0.6); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);">
            <div class="dash-card-header" style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                <span>Live Tracking</span>
                <span class="dash-card-icon" style="color: #ef4444; font-size: 14px;">📍</span>
            </div>
            <div class="tracking-status-wrap" style="margin-top: 6px;">
                <div class="tracking-status-title" style="font-size: 15px; font-weight: 800; color: #FFFFFF; margin-bottom: 6px;">Vehicle En Route</div>
                <div class="tracking-progress-container" style="position: relative; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 2px; margin-bottom: 10px; width: 100%;">
                    <div class="tracking-progress-line" style="position: absolute; left: 0; top: 0; height: 100%; width: 60%; background: #00E5A8; border-radius: inherit;"></div>
                    <div class="tracking-nodes" style="display: flex; justify-content: space-between; position: absolute; width: 100%; top: -3px;">
                        <span class="node active" style="width: 10px; height: 10px; border-radius: 50%; background: #00E5A8; box-shadow: 0 0 8px #00E5A8; display: inline-block;"></span>
                        <span class="node animate-pulse" style="width: 10px; height: 10px; border-radius: 50%; background: #00E5A8; box-shadow: 0 0 8px #00E5A8; display: inline-block;"></span>
                        <span class="node" style="width: 10px; height: 10px; border-radius: 50%; background: rgba(255, 255, 255, 0.2); display: inline-block;"></span>
                    </div>
                </div>
                <div class="tracking-details-row" style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="tracking-eta-badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">ETA 12 MIN</div>
                    <div class="tracking-dist-lbl" style="font-size: 12px; color: #94A3B8;">2.4 km away</div>
                </div>
            </div>
        </div>
        
        <!-- 2x2 Grid -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px; width: 100%;">
            <!-- Battery Card -->
            <div class="dash-card" style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between; height: 96px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); box-sizing: border-box;">
                <div class="dash-card-header" style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Battery Status</span>
                    <span class="dash-card-icon" style="color: #10b981; font-size: 14px;">🔋</span>
                </div>
                <div>
                    <div class="dash-card-value" style="font-size: 18px; font-weight: 800; color: #FFFFFF; line-height: 1.1; margin: 2px 0;">18%</div>
                    <div class="dash-card-desc" style="font-size: 11px; color: #94A3B8;">Needs charging soon</div>
                </div>
            </div>
            <!-- Charging Power Card -->
            <div class="dash-card" style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between; height: 96px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); box-sizing: border-box;">
                <div class="dash-card-header" style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Charging Power</span>
                    <span class="dash-card-icon" style="color: #fb923c; font-size: 14px;">⚡</span>
                </div>
                <div>
                    <div class="dash-card-value" style="font-size: 18px; font-weight: 800; color: #FFFFFF; line-height: 1.1; margin: 2px 0;">22 kW</div>
                    <div class="dash-card-desc" style="font-size: 11px; color: #94A3B8;">DC Fast Charging</div>
                </div>
            </div>
            <!-- Payment Card -->
            <div class="dash-card" style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between; height: 96px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); box-sizing: border-box;">
                <div class="dash-card-header" style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Secure Payments</span>
                    <span class="dash-card-icon" style="color: #60a5fa; font-size: 14px;">💳</span>
                </div>
                <div>
                    <div class="dash-card-value" style="font-size: 13px; font-weight: 800; color: #FFFFFF; line-height: 1.1; margin: 2px 0; white-space: normal !important;">UPI, Cards, Wallets, Net Banking</div>
                </div>
            </div>
            <!-- Support Card -->
            <div class="dash-card" style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between; height: 96px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); box-sizing: border-box;">
                <div class="dash-card-header" style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>24/7 Support</span>
                    <span class="dash-card-icon" style="color: #cbd5e1; font-size: 14px;">🎧</span>
                </div>
                <div>
                    <div class="dash-card-value" style="font-size: 15px; font-weight: 800; color: #FFFFFF; line-height: 1.1; margin: 2px 0;">24/7 Available</div>
                    <div class="dash-card-desc" style="font-size: 11px; color: #94A3B8;">Chat, Phone, Emergency</div>
                </div>
            </div>
        </div>
        """
        st.markdown(clean_html(dashboard_html), unsafe_allow_html=True)
        
    # Bottom Benefits Bar
    benefits_html = """<div class="benefits-bar">
<div class="benefit-item">
<div class="benefit-icon">🛡️</div>
<div class="benefit-text-wrap">
<div class="benefit-title">Safe & Reliable</div>
<div class="benefit-desc">Verified professionals</div>
</div>
</div>
<div class="benefit-item">
<div class="benefit-icon">🏷️</div>
<div class="benefit-text-wrap">
<div class="benefit-title">Affordable</div>
<div class="benefit-desc">Transparent pricing</div>
</div>
</div>
<div class="benefit-item">
<div class="benefit-icon">🌱</div>
<div class="benefit-text-wrap">
<div class="benefit-title">Eco Friendly</div>
<div class="benefit-desc">Zero Emission Future</div>
</div>
</div>
<div class="benefit-item">
<div class="benefit-icon">⏱️</div>
<div class="benefit-text-wrap">
<div class="benefit-title">Always On</div>
<div class="benefit-desc">24/7 Service</div>
</div>
</div>
</div>"""
    st.markdown(clean_html(benefits_html), unsafe_allow_html=True)


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div class="runev-sidebar-brand">
                <div class="runev-sidebar-logo">RunEV</div>
                <p class="runev-sidebar-subtitle">Passenger console</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
        current_nav = st.session_state.get("user_nav_radio")
        if current_nav not in choices:
            st.session_state.user_nav_radio = sync_label if sync_label in choices else "Dashboard"
        nav = st.radio(
            "Navigation",
            choices,
            index=choices.index(st.session_state.user_nav_radio),
            key="user_nav_radio",
            label_visibility="collapsed",
            format_func=lambda item: f"{icon_map[item]}  {item}",
        )
        st.divider()
        auto_refresh(12, enabled=nav in {"Dashboard", "Live Trips"})
        if st.button("Refresh", use_container_width=True):
            st.rerun()
        if st.button("Logout", use_container_width=True):
            clear_user_session()
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
        if st.session_state.get("user_location_captured") and not is_default_location(st.session_state.user_lat, st.session_state.user_lng):
            render_user_map(float(st.session_state.user_lat), float(st.session_state.user_lng), providers, st.session_state.user_address, key="dashboard_user_map")
        else:
            st.info("Share your live pickup location to show nearby vans on the map.")
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
                st.caption(f"Rating: {provider_rating_label(provider)}")
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


def render_trip_map_for_status(request_status: dict, provider: dict | None, key: str) -> None:
    if is_default_location(request_status.get("pickup_lat"), request_status.get("pickup_lng")):
        st.warning("This request was created with the old default pickup location. Please create a new request after sharing live location.")
        return
    try:
        render_trip_map(
            request_status["pickup_lat"],
            request_status["pickup_lng"],
            provider,
            key=key,
            trip_status=request_status.get("status"),
        )
    except TypeError:
        render_trip_map(
            request_status["pickup_lat"],
            request_status["pickup_lng"],
            provider,
            key=key,
        )


def render_trip_contacts(request_status: dict, provider: dict | None) -> None:
    provider = provider or {}
    driver_phone = provider.get("phone")
    st.markdown("#### Driver details")
    detail_cols = st.columns(3)
    detail_cols[0].caption("Driver")
    detail_cols[0].markdown(f"**{safe_text(provider.get('driver_name') or 'Assigned driver')}**")
    detail_cols[1].caption("Vehicle")
    detail_cols[1].markdown(f"**{safe_text(provider.get('vehicle_number') or 'Charging van')}**")
    detail_cols[2].caption("Mobile")
    if driver_phone:
        detail_cols[2].markdown(f"**[{safe_text(driver_phone)}](tel:{safe_text(driver_phone)})**")
    else:
        detail_cols[2].markdown("**Not added**")

    if request_status.get("status") in {"en_route", "accepted", "arrived"}:
        st.divider()
        otp_code = request_status.get("otp_code")
        if otp_code:
            st.info(f"Your trip OTP is {otp_code}. Share it with the driver only after the van reaches you.")
        else:
            st.info("Your trip OTP is being generated. Refresh this trip status in a moment.")


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

    col_details, col_info = st.columns([1.6, 1])
    with col_details:
        with st.container(border=True):
            render_trip_contacts(request_status, provider)
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

    st.markdown("#### Route map")
    render_trip_map_for_status(request_status, provider, key=f"live_trip_map_{request_status['id']}")


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
            if last_paid.get("invoice_id"):
                paid_request = load_request_status(last_paid.get("invoice_id"))
                if paid_request:
                    render_rating_form(paid_request, "last_paid")
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
        render_rating_form(request_status, "paid_gateway")
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
        render_trip_map_for_status(request_status, provider, key=f"payment_trip_map_{request_status['id']}")

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
            elif req.get("status") == "completed":
                with st.expander("Rate this session", expanded=False):
                    render_rating_form(req, key_prefix=f"history_{req['id']}")


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
    st.markdown("#### Theme")
    mode = render_theme_selector("user_theme_selector")
    persist_theme_preference(st.session_state.get("jwt_token"), mode)
    st.caption("Theme preferences are restored from your account and mirrored to browser local storage on this device.")
    st.divider()
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
