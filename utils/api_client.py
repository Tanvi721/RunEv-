import os
from typing import Any

import requests

API_BASE_URL = os.getenv(
    "RUNEV_API_BASE_URL",
    "https://runev-1b1v.onrender.com"
)

class ApiError(Exception):
    pass


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
            f"{API_BASE_URL}{path}",
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
        raise ApiError(str(detail))

    if not response.content:
        return None
    return response.json()


def login(email: str, password: str) -> dict[str, Any]:
    return request_json("POST", "/api/v1/auth/login", json={"email": email, "password": password})


def me(token: str) -> dict[str, Any]:
    return request_json("GET", "/api/v1/auth/me", token=token)


def update_me(token: str, username: str | None = None, phone: str | None = None) -> dict[str, Any]:
    return request_json("PUT", "/api/v1/auth/me", token=token, json={"username": username, "phone": phone})


def register(username: str, email: str, password: str, role: str = "user", vehicle_number: str | None = None):
    return request_json(
        "POST",
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role": role,
            "vehicle_number": vehicle_number,
        },
    )
