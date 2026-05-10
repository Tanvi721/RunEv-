from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(255), default="user") # 'user', 'admin', 'provider'
    phone = Column(String(255), nullable=True)

    requests = relationship("ServiceRequest", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    provider_profiles = relationship("Provider", back_populates="user")

class Provider(Base):
    __tablename__ = "providers"
    __table_args__ = (
        Index("ix_providers_available_location", "is_available", "current_lat", "current_lng"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    vehicle_number = Column(String(255), index=True)
    current_lat = Column(Float, nullable=True, index=True)
    current_lng = Column(Float, nullable=True, index=True)
    is_available = Column(Boolean, default=True, index=True)
    
    charging_speed = Column(String(255), nullable=True)
    connector_types = Column(String(255), nullable=True)
    price_per_kwh = Column(Float, nullable=True)
    
    # Driver profile information
    profile_photo = Column(String(512), nullable=True)  # Path or URL to profile photo
    driver_name = Column(String(255), nullable=True)    # Driver name
    address = Column(String(512), nullable=True)         # Address

    user = relationship("User", back_populates="provider_profiles")
    accepted_requests = relationship("ServiceRequest", back_populates="provider")

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    __table_args__ = (
        Index("ix_service_requests_provider_status", "provider_id", "status"),
        Index("ix_service_requests_user_status", "user_id", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True, index=True)
    
    request_time = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    pickup_lat = Column(Float)
    pickup_lng = Column(Float)
    status = Column(String(255), default="pending", index=True) # pending, accepted, arrived, charging, completed, cancelled
    payment_method = Column(String(255), default="CASH") # CASH, CARD, UPI, PAY_LATER
    charged_units_kwh = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)

    user = relationship("User", back_populates="requests")
    provider = relationship("Provider", back_populates="accepted_requests")
    payment = relationship("Payment", back_populates="request", uselist=False)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    razorpay_order_id = Column(String(255), nullable=True)
    razorpay_payment_id = Column(String(255), nullable=True)
    amount = Column(Float)
    status = Column(String(255), default="pending", index=True) # pending, success, failed

    request = relationship("ServiceRequest", back_populates="payment")
    booking = relationship("Booking", back_populates="payments")
    user = relationship("User", back_populates="payments")

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(512), nullable=True)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    price_per_hour = Column(Float, default=0.0)
    total_slots = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    slots = relationship("Slot", back_populates="station")
    bookings = relationship("Booking", back_populates="station")

class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"))
    slot_number = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)

    station = relationship("Station", back_populates="slots")
    bookings = relationship("Booking", back_populates="slot")

class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        Index("ix_bookings_user_status", "user_id", "status"),
        Index("ix_bookings_station_slot", "station_id", "slot_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    station_id = Column(Integer, ForeignKey("stations.id"), index=True)
    slot_id = Column(Integer, ForeignKey("slots.id"), index=True)
    booking_time = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    duration_hours = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    status = Column(String(255), default="confirmed", index=True)

    user = relationship("User", back_populates="bookings")
    station = relationship("Station", back_populates="bookings")
    slot = relationship("Slot", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")
