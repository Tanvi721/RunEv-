import os
from typing import Any

import requests

API_BASE_URL = os.getenv(
    "RUNEV_API_BASE_URL",
    "http://127.0.0.1:8000"
)


def api_base_url() -> str:
    return os.getenv("RUNEV_API_BASE_URL", API_BASE_URL).rstrip("/")

import streamlit as st

st.write("API URL:", api_base_url())

class ApiError(Exception):
    pass


FIELD_LABELS = {
    "email": "Email",
    "password": "Password",
    "username": "Username",
    "vehicle_number": "Vehicle number",
    "phone": "Phone",
    "confirm_password": "Confirm password",
    "otp_code": "OTP",
}


def format_error_detail(detail: Any) -> str:
    if isinstance(detail, list):
        messages = []
        for item in detail:
            if not isinstance(item, dict):
                messages.append(str(item))
                continue
            loc = item.get("loc") or []
            field = next((part for part in reversed(loc) if isinstance(part, str) and part != "body"), "")
            label = FIELD_LABELS.get(field, field.replace("_", " ").title() if field else "Field")
            message = item.get("msg", "Invalid value")
            messages.append(f"{label}: {message}")
        return "\n".join(messages)

    if isinstance(detail, dict):
        return str(detail.get("message") or detail.get("detail") or detail)

    return str(detail)


def auth_headers(token: str | None) -> dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def request_json(
    method: str,
    path: str,
    token: str | None = None,
    timeout: int = 30,
    **kwargs: Any,
) -> Any:
    try:
        response = requests.request(
            method,
            f"{api_base_url()}{path}",
            headers={**auth_headers(token), **kwargs.pop("headers", {})},
            timeout=timeout,
            **kwargs,
        )
    except requests.RequestException as exc:
        raise ApiError(f"Backend is not reachable: {exc}") from exc

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise ApiError(format_error_detail(detail))

    if not response.content:
        return None
    return response.json()


def login(email: str, password: str) -> dict[str, Any]:
    return request_json("POST", "/api/v1/auth/login", json={"email": email, "password": password})


def reset_password(email: str, new_password: str) -> dict[str, Any]:
    return request_json("POST", "/api/v1/auth/password/reset", json={"email": email, "new_password": new_password})


def login_with_supabase(access_token: str, refresh_token: str | None = None) -> dict[str, Any]:
    return request_json(
        "POST",
        "/api/v1/auth/supabase/session",
        json={"access_token": access_token, "refresh_token": refresh_token},
    )


def request_phone_otp(phone: str, username: str | None = None) -> dict[str, Any]:
    return request_json("POST", "/api/v1/auth/login/phone/request-otp", json={"phone": phone, "username": username})


def verify_phone_otp(phone: str, otp_code: str, username: str | None = None) -> dict[str, Any]:
    return request_json(
        "POST",
        "/api/v1/auth/login/phone/verify",
        json={"phone": phone, "otp_code": otp_code, "username": username},
    )


def request_email_otp(email: str, username: str | None = None, role: str = "user") -> dict[str, Any]:
    return request_json(
        "POST",
        "/api/v1/auth/login/email/request-otp",
        json={"email": email, "username": username, "role": role},
    )


def verify_email_otp(email: str, otp_code: str, username: str | None = None, role: str = "user") -> dict[str, Any]:
    return request_json(
        "POST",
        "/api/v1/auth/login/email/verify",
        json={"email": email, "otp_code": otp_code, "username": username, "role": role},
    )


def me(token: str) -> dict[str, Any]:
    return request_json("GET", "/api/v1/auth/me", token=token)


def update_me(token: str, username: str | None = None, phone: str | None = None) -> dict[str, Any]:
    return request_json("PUT", "/api/v1/auth/me", token=token, json={"username": username, "phone": phone})


def get_preferences(token: str) -> dict[str, Any]:
    return request_json("GET", "/api/v1/auth/me/preferences", token=token)


def update_preferences(token: str, **preferences: Any) -> dict[str, Any]:
    return request_json("PUT", "/api/v1/auth/me/preferences", token=token, json=preferences)


def estimate_price(token: str, pickup_lat: float, pickup_lng: float, provider_id: int | None = None, estimated_energy_kwh: float = 0) -> dict[str, Any]:
    return request_json(
        "POST",
        "/api/v1/pricing/estimate",
        token=token,
        json={
            "pickup_lat": pickup_lat,
            "pickup_lng": pickup_lng,
            "provider_id": provider_id,
            "estimated_energy_kwh": estimated_energy_kwh,
        },
    )


def register(
    username: str,
    email: str,
    password: str,
    role: str = "user",
    vehicle_number: str | None = None,
    phone: str | None = None,
    confirm_password: str | None = None,
):
    return request_json(
        "POST",
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password,
            "role": role,
            "vehicle_number": vehicle_number,
            "phone": phone,
        },
    )
