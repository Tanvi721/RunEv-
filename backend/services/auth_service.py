from sqlalchemy.orm import Session
from models import User, Provider
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from fastapi import HTTPException, status

JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_jwt_key_change_in_production")
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60*24) # 1 day
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def register_user(db: Session, username: str, email: str, password: str, role: str = "user", vehicle_number: str = None):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return None
    
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    if role == "provider" and vehicle_number:
        new_provider = Provider(user_id=new_user.id, vehicle_number=vehicle_number)
        db.add(new_provider)
        db.commit()
        
    return new_user
