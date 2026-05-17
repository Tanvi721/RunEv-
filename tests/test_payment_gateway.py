import hashlib
import hmac

from backend.services.payment_gateway import create_payment_order, verify_payment_signature, verify_webhook_signature


def test_verify_payment_signature_with_secret(monkeypatch):
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", "test_secret")
    order_id = "order_123"
    payment_id = "pay_123"
    signature = hmac.new(
        b"test_secret",
        f"{order_id}|{payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    assert verify_payment_signature(order_id, payment_id, signature)


def test_rejects_invalid_payment_signature(monkeypatch):
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", "test_secret")

    assert not verify_payment_signature("order_123", "pay_123", "bad_signature")


def test_verify_webhook_signature(monkeypatch):
    monkeypatch.setenv("RAZORPAY_WEBHOOK_SECRET", "webhook_secret")
    body = b'{"event":"payment.captured"}'
    signature = hmac.new(b"webhook_secret", body, hashlib.sha256).hexdigest()

    assert verify_webhook_signature(body, signature)


def test_create_payment_order_falls_back_to_mock_when_razorpay_is_unreachable(monkeypatch):
    monkeypatch.setenv("RAZORPAY_KEY_ID", "rzp_test_key")
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", "test_secret")

    def raise_connection_error(*args, **kwargs):
        import requests

        raise requests.ConnectionError("offline")

    monkeypatch.setattr("backend.services.payment_gateway.requests.post", raise_connection_error)

    order = create_payment_order(10, "receipt_123")

    assert order["gateway"] == "mock"
    assert order["id"].startswith("order_dev_")
    assert order["amount"] == 1000


def test_dev_order_signature_is_allowed_even_when_secret_exists(monkeypatch):
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", "test_secret")

    assert verify_payment_signature("order_dev_123", "pay_dev_123", "dev_order_dev_123")
