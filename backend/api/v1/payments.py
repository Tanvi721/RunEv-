from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend import models
from backend.core.security import get_current_user
from backend.database import get_db
from backend.schemas.payment import (
    PaymentOrderRequest,
    PaymentOrderResponse,
    PaymentResponse,
    PaymentVerifyRequest,
)
from backend.services.payment_gateway import (
    create_payment_order,
    verify_payment_signature,
    verify_webhook_signature,
)

router = APIRouter(prefix="/payments", tags=["payments"])


def resolve_payment_amount(db: Session, data: PaymentOrderRequest, current_user: models.User) -> float:
    if data.amount is not None:
        return data.amount

    if data.request_id is not None:
        service_request = db.query(models.ServiceRequest).filter(models.ServiceRequest.id == data.request_id).first()
        if not service_request:
            raise HTTPException(status_code=404, detail="Service request not found")
        if current_user.role != "admin" and service_request.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only pay for your own request")
        if not service_request.total_price:
            raise HTTPException(status_code=400, detail="Request does not have a payable amount yet")
        return float(service_request.total_price)

    if data.booking_id is not None:
        booking = db.query(models.Booking).filter(models.Booking.id == data.booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if current_user.role != "admin" and booking.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only pay for your own booking")
        return float(booking.total_price)

    raise HTTPException(status_code=400, detail="Provide request_id, booking_id, or amount")


@router.post("/orders", response_model=PaymentOrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    data: PaymentOrderRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    amount = resolve_payment_amount(db, data, current_user)
    payment = models.Payment(
        request_id=data.request_id,
        booking_id=data.booking_id,
        user_id=current_user.id,
        amount=amount,
        status="pending",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    order = create_payment_order(amount, receipt=f"runev_payment_{payment.id}")
    payment.razorpay_order_id = order["id"]
    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "order_id": payment.razorpay_order_id,
        "amount": payment.amount,
        "currency": order.get("currency", "INR"),
        "status": payment.status,
        "gateway": order.get("gateway", "razorpay"),
        "key_id": order.get("key_id"),
    }


@router.post("/verify", response_model=PaymentResponse)
def verify_payment(
    data: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    payment = db.query(models.Payment).filter(models.Payment.id == data.payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if current_user.role != "admin" and payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only verify your own payment")
    if payment.razorpay_order_id != data.razorpay_order_id:
        raise HTTPException(status_code=400, detail="Order ID does not match this payment")

    if not verify_payment_signature(data.razorpay_order_id, data.razorpay_payment_id, data.razorpay_signature):
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    payment.razorpay_payment_id = data.razorpay_payment_id
    payment.status = "success"
    if payment.booking:
        payment.booking.status = "completed"
    if payment.request:
        payment.request.payment_method = "RAZORPAY"
        payment.request.status = "completed"
        if payment.request.provider:
            payment.request.provider.is_available = True
    db.commit()
    db.refresh(payment)
    return payment


@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    raw_body = await request.body()
    if not x_razorpay_signature or not verify_webhook_signature(raw_body, x_razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    payload = await request.json()
    event = payload.get("event")
    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    order_id = payment_entity.get("order_id")
    razorpay_payment_id = payment_entity.get("id")

    if event == "payment.captured" and order_id:
        payment = db.query(models.Payment).filter(models.Payment.razorpay_order_id == order_id).first()
        if payment:
            payment.razorpay_payment_id = razorpay_payment_id
            payment.status = "success"
            db.commit()

    return {"status": "ok"}
