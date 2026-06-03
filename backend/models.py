from sqlalchemy import CheckConstraint, Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import relationship
import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(255), default="user") # 'user', 'admin', 'provider'
    phone = Column(String(255), nullable=True)
    auth_provider = Column(String(32), default="email")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    failed_login_count = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)

    requests = relationship("ServiceRequest", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    provider_profiles = relationship("Provider", back_populates="user")
    ratings = relationship("Rating", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    theme_mode = Column(String(32), default="system")
    brand_color = Column(String(32), nullable=True)
    accent_color = Column(String(32), nullable=True)
    gradient_start = Column(String(32), nullable=True)
    gradient_end = Column(String(32), nullable=True)
    card_appearance = Column(String(32), default="subtle")
    border_radius_style = Column(String(32), default="medium")
    dashboard_density = Column(String(32), default="balanced")

    user = relationship("User", back_populates="preferences")


class PricingSetting(Base):
    __tablename__ = "pricing_settings"

    id = Column(Integer, primary_key=True, index=True)
    base_visit_fee = Column(Float, default=99.0, nullable=False)
    distance_rate_per_km = Column(Float, default=12.0, nullable=False)
    charging_rate_per_kwh = Column(Float, default=20.0, nullable=False)
    platform_fee = Column(Float, default=20.0, nullable=False)
    emergency_fee_limit = Column(Float, default=0.0, nullable=False)
    night_fee_limit = Column(Float, default=0.0, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)


class Provider(Base):
    __tablename__ = "providers"
    __table_args__ = (
        Index("ix_providers_available_location", "is_available", "current_lat", "current_lng"),
        UniqueConstraint("vehicle_number", name="uq_providers_vehicle_number"),
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
    ratings = relationship("Rating", back_populates="provider")

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    __table_args__ = (
        Index("ix_service_requests_provider_status", "provider_id", "status"),
        Index("ix_service_requests_user_status", "user_id", "status"),
        CheckConstraint("pickup_lat BETWEEN -90 AND 90", name="ck_service_requests_pickup_lat"),
        CheckConstraint("pickup_lng BETWEEN -180 AND 180", name="ck_service_requests_pickup_lng"),
        CheckConstraint("charged_units_kwh IS NULL OR charged_units_kwh > 0", name="ck_service_requests_charged_units_positive"),
        CheckConstraint("total_price IS NULL OR total_price > 0", name="ck_service_requests_total_price_positive"),
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
    estimated_distance_km = Column(Float, nullable=True)
    base_visit_fee = Column(Float, nullable=True)
    distance_rate_per_km = Column(Float, nullable=True)
    charging_rate_per_kwh = Column(Float, nullable=True)
    platform_fee = Column(Float, nullable=True)
    distance_charge = Column(Float, nullable=True)
    charging_cost = Column(Float, nullable=True)
    emergency_fee = Column(Float, default=0.0, nullable=False)
    night_fee = Column(Float, default=0.0, nullable=False)
    driver_earnings = Column(Float, nullable=True)
    runev_earnings = Column(Float, nullable=True)
    charging_revenue = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)
    otp_code = Column(String(10), nullable=True)
    otp_verified_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="requests")
    provider = relationship("Provider", back_populates="accepted_requests")
    payment = relationship("Payment", back_populates="request", uselist=False)
    rating = relationship("Rating", back_populates="request", uselist=False)

class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
    )

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


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("request_id", name="uq_ratings_request_id"),
        Index("ix_ratings_provider_score", "provider_id", "score"),
    )

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    comment = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    request = relationship("ServiceRequest", back_populates="rating")
    user = relationship("User", back_populates="ratings")
    provider = relationship("Provider", back_populates="ratings")

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
