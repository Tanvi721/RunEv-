import hashlib
import hmac

from backend.services.payment_gateway import verify_payment_signature, verify_webhook_signature


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
