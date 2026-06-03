from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from pydantic import field_validator, model_validator

from backend.core.validation import (
    normalize_email,
    normalize_indian_mobile,
    normalize_vehicle_number,
    validate_full_name,
    validate_password,
)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=8, max_length=128)
    confirm_password: Optional[str] = None
    role: str = "user"
    vehicle_number: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, value: str) -> str:
        return validate_full_name(value, "Full name")

    @field_validator("email")
    @classmethod
    def email_valid(cls, value: str) -> str:
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def password_valid(cls, value: str) -> str:
        return validate_password(value)

    @field_validator("phone")
    @classmethod
    def phone_valid(cls, value: Optional[str]) -> Optional[str]:
        return normalize_indian_mobile(value) if value else value

    @field_validator("vehicle_number")
    @classmethod
    def vehicle_valid(cls, value: Optional[str]) -> Optional[str]:
        return normalize_vehicle_number(value) if value else value

    @model_validator(mode="after")
    def passwords_match(self):
        if self.confirm_password is not None and self.password != self.confirm_password:
            raise ValueError("Confirm password must match password.")
        return self


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_valid(cls, value: str) -> str:
        return normalize_email(value)


class PasswordResetRequest(BaseModel):
    email: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def email_valid(cls, value: str) -> str:
        return normalize_email(value)

    @field_validator("new_password")
    @classmethod
    def password_valid(cls, value: str) -> str:
        return validate_password(value)


class SupabaseSessionRequest(BaseModel):
    access_token: str = Field(min_length=20)
    refresh_token: Optional[str] = None


class PhoneOtpRequest(BaseModel):
    phone: str = Field(min_length=8, max_length=20)
    username: Optional[str] = Field(default=None, min_length=2, max_length=255)


class PhoneOtpVerifyRequest(BaseModel):
    phone: str = Field(min_length=8, max_length=20)
    otp_code: str = Field(min_length=4, max_length=8)
    username: Optional[str] = Field(default=None, min_length=2, max_length=255)


class EmailOtpRequest(BaseModel):
    email: str
    username: Optional[str] = Field(default=None, min_length=2, max_length=255)
    role: str = "user"

    @field_validator("email")
    @classmethod
    def email_valid(cls, value: str) -> str:
        return normalize_email(value)


class EmailOtpVerifyRequest(BaseModel):
    email: str
    otp_code: str = Field(min_length=4, max_length=8)
    username: Optional[str] = Field(default=None, min_length=2, max_length=255)
    role: str = "user"

    @field_validator("email")
    @classmethod
    def email_valid(cls, value: str) -> str:
        return normalize_email(value)


class OtpChallengeResponse(BaseModel):
    message: str
    expires_in_seconds: int
    delivery_channel: str = "sms"
    dev_otp: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    phone: Optional[str] = None
    auth_provider: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    failed_login_count: int = 0

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=2, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=255)

    @field_validator("username")
    @classmethod
    def username_valid(cls, value: Optional[str]) -> Optional[str]:
        return validate_full_name(value, "Full name") if value else value

    @field_validator("phone")
    @classmethod
    def phone_valid(cls, value: Optional[str]) -> Optional[str]:
        return normalize_indian_mobile(value) if value else value


class UserPreferenceRequest(BaseModel):
    theme_mode: Optional[str] = "system"
    brand_color: Optional[str] = None
    accent_color: Optional[str] = None
    gradient_start: Optional[str] = None
    gradient_end: Optional[str] = None
    card_appearance: Optional[str] = "subtle"
    border_radius_style: Optional[str] = "medium"
    dashboard_density: Optional[str] = "balanced"


class UserPreferenceResponse(UserPreferenceRequest):
    user_id: int
