import uuid
from sqlalchemy.orm import Session
from backend.models import Payment, Booking

def process_payment(db: Session, booking_id: int, user_id: int, amount: float):
    # This is a mock implementation for Razorpay
    # In a real app you would use razorpay.Client() to create an order
    
    mock_order_id = f"order_{uuid.uuid4().hex[:10]}"
    mock_payment_id = f"pay_{uuid.uuid4().hex[:10]}"
    
    payment = Payment(
        booking_id=booking_id,
        user_id=user_id,
        razorpay_order_id=mock_order_id,
        razorpay_payment_id=mock_payment_id,
        amount=amount,
        status="success"
    )
    db.add(payment)
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        booking.status = "completed"
        
    db.commit()
    return payment
