from sqlalchemy.orm import Session
from backend.models import Booking, Slot, Station
from datetime import datetime

def create_booking(db: Session, user_id: int, station_id: int, slot_id: int, duration_hours: int):
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise ValueError("Station not found")
        
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot or not slot.is_available:
        raise ValueError("Slot not available")
        
    total_price = station.price_per_hour * duration_hours
    
    booking = Booking(
        user_id=user_id,
        station_id=station_id,
        slot_id=slot_id,
        duration_hours=duration_hours,
        total_price=total_price,
        status="confirmed"
    )
    
    # Mark slot as unavailable
    slot.is_available = False
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    return booking

def get_user_bookings(db: Session, user_id: int):
    return db.query(Booking).filter(Booking.user_id == user_id).order_by(Booking.booking_time.desc()).all()

def get_all_bookings(db: Session):
    return db.query(Booking).order_by(Booking.booking_time.desc()).all()
