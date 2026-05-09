from typing import Optional

from pydantic import BaseModel, Field


class PaymentOrderRequest(BaseModel):
    request_id: Optional[int] = None
    booking_id: Optional[int] = None
    amount: Optional[float] = Field(default=None, gt=0)


class PaymentOrderResponse(BaseModel):
    payment_id: int
    order_id: str
    amount: float
    currency: str
    status: str
    gateway: str
    key_id: Optional[str] = None


class PaymentVerifyRequest(BaseModel):
    payment_id: int
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentResponse(BaseModel):
    id: int
    request_id: Optional[int] = None
    booking_id: Optional[int] = None
    user_id: int
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    amount: float
    status: str

    class Config:
        from_attributes = True
