import os
from backend.database import engine, Base, SessionLocal
from backend.models import User, Provider
import bcrypt

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if we already have data
    if db.query(User).first():
        print("Database already initialized.")
        db.close()
        return

    print("Injecting dummy users and provider profiles...")
    admin = User(
        username="Admin",
        email="admin@runev.com",
        hashed_password=get_password_hash("admin123"),
        role="admin"
    )
    user1 = User(
        username="John Doe",
        email="john@example.com",
        hashed_password=get_password_hash("password123"),
        role="user"
    )
    provider_user = User(
        username="Provider One",
        email="provider@runev.com",
        hashed_password=get_password_hash("provider123"),
        role="provider"
    )

    db.add(admin)
    db.add(user1)
    db.add(provider_user)
    db.flush()

    provider = Provider(
        user_id=provider_user.id,
        vehicle_number="RNE-001",
        current_lat=18.5204,
        current_lng=73.8567,
        is_available=True,
        charging_speed="Fast",
        connector_types="Type2",
        price_per_kwh=20.0
    )
    db.add(provider)
    db.commit()
    db.close()
    print("Mock data initialized successfully!")

if __name__ == "__main__":
    init_db()
