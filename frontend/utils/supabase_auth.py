from __future__ import annotations

import base64
import hashlib
import os
import secrets
from typing import Any
from urllib.parse import urlencode

import requests


class SupabaseAuthError(Exception):
    pass


def supabase_url() -> str:
    return os.getenv("SUPABASE_URL", "").rstrip("/")


def supabase_anon_key() -> str:
    return os.getenv("SUPABASE_ANON_KEY", "")


def app_url() -> str:
    return os.getenv("RUNEV_USER_APP_URL", "http://localhost:8501").rstrip("/")


def is_configured() -> bool:
    return bool(supabase_url() and supabase_anon_key())


def config_error() -> str | None:
    if not supabase_url() or not supabase_anon_key():
        return "Supabase is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY."
    if not supabase_anon_key().startswith("eyJ") or supabase_anon_key().count(".") != 2:
        return "Invalid Supabase anon key in .env. Use the project's public anon key, not the project URL or service-role secret."
    return None


def _headers() -> dict[str, str]:
    anon_key = supabase_anon_key()
    return {
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json",
    }


def create_pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def google_oauth_url(redirect_to: str, state_or_challenge: str, code_challenge: str | None = None) -> str:
    if not is_configured():
        raise SupabaseAuthError("Supabase authentication is not configured.")

    challenge = code_challenge or state_or_challenge
    params = urlencode(
        {
            "provider": "google",
            "redirect_to": redirect_to,
            "scopes": "openid email profile",
            "flow_type": "pkce",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    return f"{supabase_url()}/auth/v1/authorize?{params}"


def check_google_provider() -> str | None:
    error = config_error()
    if error:
        return error

    _, challenge = create_pkce_pair()
    try:
        response = requests.get(
            google_oauth_url(app_url(), challenge),
            allow_redirects=False,
            timeout=10,
        )
    except requests.RequestException:
        return "Could not reach Supabase Google OAuth."

    if response.status_code in {302, 303}:
        return None
    if response.status_code >= 400:
        message = _supabase_error(response, "Google OAuth is not available.")
        if "provider is not enabled" in message.lower():
            return "Google OAuth is disabled in Supabase. Enable Google under Supabase Authentication providers."
        return message
    return None


def exchange_code_for_session(code: str, code_verifier: str) -> dict[str, Any]:
    if not is_configured():
        raise SupabaseAuthError("Supabase authentication is not configured.")

    try:
        response = requests.post(
            f"{supabase_url()}/auth/v1/token?grant_type=pkce",
            headers=_headers(),
            json={"auth_code": code, "code_verifier": code_verifier},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise SupabaseAuthError("Could not reach Supabase authentication.") from exc

    if response.status_code >= 400:
        raise SupabaseAuthError(_supabase_error(response, "Could not complete Supabase sign in."))
    return response.json()


def send_magic_link(email: str, redirect_to: str, code_challenge: str) -> dict[str, Any]:
    if not is_configured():
        raise SupabaseAuthError("Supabase authentication is not configured.")

    try:
        response = requests.post(
            f"{supabase_url()}/auth/v1/otp",
            headers=_headers(),
            json={
                "email": email,
                "type": "magiclink",
                "options": {"email_redirect_to": redirect_to},
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        raise SupabaseAuthError("Could not reach Supabase authentication.") from exc

    if response.status_code >= 400:
        raise SupabaseAuthError(_supabase_error(response, "Could not send a magic link."))
    return response.json() if response.content else {}


def sign_up_with_password(email: str, password: str, full_name: str, redirect_to: str | None = None) -> dict[str, Any]:
    if not is_configured():
        raise SupabaseAuthError("Supabase authentication is not configured.")

    payload: dict[str, Any] = {
        "email": email.strip().lower(),
        "password": password,
        "data": {"full_name": full_name.strip(), "name": full_name.strip()},
    }
    if redirect_to:
        payload["options"] = {"email_redirect_to": redirect_to}
    try:
        response = requests.post(f"{supabase_url()}/auth/v1/signup", headers=_headers(), json=payload, timeout=15)
    except requests.RequestException as exc:
        raise SupabaseAuthError("Could not reach Supabase authentication.") from exc
    if response.status_code >= 400:
        raise SupabaseAuthError(_supabase_error(response, "Could not create your account."))
    return response.json() if response.content else {}


def sign_in_with_password(email: str, password: str) -> dict[str, Any]:
    if not is_configured():
        raise SupabaseAuthError("Supabase authentication is not configured.")
    try:
        response = requests.post(
            f"{supabase_url()}/auth/v1/token?grant_type=password",
            headers=_headers(),
            json={"email": email.strip().lower(), "password": password},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise SupabaseAuthError("Could not reach Supabase authentication.") from exc
    if response.status_code >= 400:
        raise SupabaseAuthError(_supabase_error(response, "Invalid email or password."))
    return response.json()


def send_password_reset(email: str, redirect_to: str | None = None) -> dict[str, Any]:
    if not is_configured():
        raise SupabaseAuthError("Supabase authentication is not configured.")
    payload: dict[str, Any] = {"email": email.strip().lower()}
    if redirect_to:
        payload["options"] = {"redirect_to": redirect_to}
    try:
        response = requests.post(f"{supabase_url()}/auth/v1/recover", headers=_headers(), json=payload, timeout=15)
    except requests.RequestException as exc:
        raise SupabaseAuthError("Could not reach Supabase authentication.") from exc
    if response.status_code >= 400:
        raise SupabaseAuthError(_supabase_error(response, "Could not send password reset email."))
    return response.json() if response.content else {}


def update_password(access_token: str, new_password: str) -> dict[str, Any]:
    if not is_configured():
        raise SupabaseAuthError("Supabase authentication is not configured.")
    headers = {
        "apikey": supabase_anon_key(),
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.put(
            f"{supabase_url()}/auth/v1/user",
            headers=headers,
            json={"password": new_password},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise SupabaseAuthError("Could not reach Supabase authentication.") from exc
    if response.status_code >= 400:
        raise SupabaseAuthError(_supabase_error(response, "Could not update password."))
    return response.json() if response.content else {}


def _supabase_error(response: requests.Response, fallback: str) -> str:
    try:
        payload = response.json()
    except ValueError:
        return fallback
    message = payload.get("msg") or payload.get("message") or payload.get("error_description") or fallback
    if "invalid api key" in str(message).lower():
        return "Invalid Supabase anon key in .env. Copy the public anon key from your Supabase project API settings."
    return message
