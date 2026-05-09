from typing import Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=255)
    email: str
    password: str = Field(min_length=6, max_length=128)
    role: str = "user"
    vehicle_number: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=2, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=255)
