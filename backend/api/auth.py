from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from services.auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
    decode_access_token,
)
from pydantic import BaseModel

router = APIRouter()


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"
    vehicle_number: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(
        db,
        data.username,
        data.email,
        data.password,
        data.role,
        data.vehicle_number,
    )

    if not user:
        raise HTTPException(status_code=400, detail="User already exists")

    token = create_access_token(
        {"sub": user.email}
    )

    return {
        "message": "User registered successfully",
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        {"sub": user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/me")
def me(token: str):
    payload = decode_access_token(token)

    return {
        "email": payload.get("sub")
    }