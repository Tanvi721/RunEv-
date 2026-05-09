from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.database import get_db
from backend.models import User
from backend.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserProfileUpdate, UserResponse
from backend.services.auth_service import authenticate_user, create_access_token, register_user

router = APIRouter(prefix="/auth", tags=["auth"])

ALLOWED_PUBLIC_ROLES = {"user", "provider"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if data.role not in ALLOWED_PUBLIC_ROLES:
        raise HTTPException(status_code=400, detail="Invalid public registration role")
    if data.role == "provider" and not data.vehicle_number:
        raise HTTPException(status_code=400, detail="Vehicle number is required for provider registration")

    user = register_user(
        db,
        username=data.username,
        email=data.email,
        password=data.password,
        role=data.role,
        vehicle_number=data.vehicle_number,
    )
    if not user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return {"access_token": create_access_token(data={"sub": user.email, "role": user.role})}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(data: UserProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if data.username is not None:
        current_user.username = data.username
    if data.phone is not None:
        current_user.phone = data.phone
    db.commit()
    db.refresh(current_user)
    return current_user
