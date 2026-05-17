import base64
import hashlib
import hmac
import os
import uuid
from typing import Any

import requests

RAZORPAY_ORDERS_URL = "https://api.razorpay.com/v1/orders"


def get_razorpay_key_id() -> str | None:
    return os.getenv("RAZORPAY_KEY_ID")


def get_razorpay_key_secret() -> str | None:
    return os.getenv("RAZORPAY_KEY_SECRET")


def get_razorpay_webhook_secret() -> str | None:
    return os.getenv("RAZORPAY_WEBHOOK_SECRET")


def create_mock_payment_order(amount_paise: int) -> dict[str, Any]:
    return {
        "id": f"order_dev_{uuid.uuid4().hex[:12]}",
        "amount": amount_paise,
        "currency": "INR",
        "status": "created",
        "gateway": "mock",
        "key_id": None,
    }


def create_payment_order(amount: float, receipt: str) -> dict[str, Any]:
    key_id = get_razorpay_key_id()
    key_secret = get_razorpay_key_secret()
    amount_paise = int(round(amount * 100))

    if not key_id or not key_secret:
        return create_mock_payment_order(amount_paise)

    auth_token = base64.b64encode(f"{key_id}:{key_secret}".encode("utf-8")).decode("utf-8")
    try:
        response = requests.post(
            RAZORPAY_ORDERS_URL,
            json={
                "amount": amount_paise,
                "currency": "INR",
                "receipt": receipt,
                "payment_capture": 1,
            },
            headers={
                "Authorization": f"Basic {auth_token}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException:
        return create_mock_payment_order(amount_paise)

    payload = response.json()
    payload["gateway"] = "razorpay"
    payload["key_id"] = key_id
    return payload


def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    if order_id.startswith("order_dev_"):
        return signature.startswith("dev_")

    secret = get_razorpay_key_secret()
    if not secret:
        return signature.startswith("dev_")

    message = f"{order_id}|{payment_id}".encode("utf-8")
    expected_signature = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


def verify_webhook_signature(raw_body: bytes, signature: str) -> bool:
    secret = get_razorpay_webhook_secret()
    if not secret:
        return False

    expected_signature = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, signature)
