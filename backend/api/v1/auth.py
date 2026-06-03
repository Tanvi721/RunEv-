from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.database import get_db
from backend.models import User, UserPreference
from backend.schemas.auth import (
    EmailOtpRequest,
    EmailOtpVerifyRequest,
    LoginRequest,
    OtpChallengeResponse,
    PasswordResetRequest,
    PhoneOtpRequest,
    PhoneOtpVerifyRequest,
    RegisterRequest,
    SupabaseSessionRequest,
    TokenResponse,
    UserProfileUpdate,
    UserPreferenceRequest,
    UserPreferenceResponse,
    UserResponse,
)
from backend.services.auth_service import (
    authenticate_user,
    create_access_token,
    login_with_supabase_session,
    register_user,
    request_email_otp,
    request_phone_otp,
    verify_email_otp,
    verify_phone_otp,
    get_password_hash,
    supabase_password_sign_up,
    supabase_password_sign_in,
    supabase_send_password_reset,
)

router = APIRouter(prefix="/auth", tags=["auth"])

ALLOWED_PUBLIC_ROLES = {"user", "provider"}
ALLOWED_THEME_MODES = {"light", "dark", "system"}
ALLOWED_CARD_APPEARANCES = {"subtle", "elevated", "outlined"}
ALLOWED_RADIUS_STYLES = {"small", "medium", "large", "extra_large"}
ALLOWED_DASHBOARD_DENSITIES = {"comfortable", "balanced", "compact"}


def _default_preferences(user_id: int) -> dict:
    return {
        "user_id": user_id,
        "theme_mode": "system",
        "brand_color": None,
        "accent_color": None,
        "gradient_start": None,
        "gradient_end": None,
        "card_appearance": "subtle",
        "border_radius_style": "medium",
        "dashboard_density": "balanced",
    }


def _validate_preferences(data: UserPreferenceRequest) -> None:
    if data.theme_mode and data.theme_mode not in ALLOWED_THEME_MODES:
        raise HTTPException(status_code=400, detail="Invalid theme mode")
    if data.card_appearance and data.card_appearance not in ALLOWED_CARD_APPEARANCES:
        raise HTTPException(status_code=400, detail="Invalid card appearance")
    if data.border_radius_style and data.border_radius_style not in ALLOWED_RADIUS_STYLES:
        raise HTTPException(status_code=400, detail="Invalid border radius style")
    if data.dashboard_density and data.dashboard_density not in ALLOWED_DASHBOARD_DENSITIES:
        raise HTTPException(status_code=400, detail="Invalid dashboard density")


def _preferences_response(preferences: UserPreference | None, user_id: int) -> dict:
    if not preferences:
        return _default_preferences(user_id)
    return {
        "user_id": user_id,
        "theme_mode": preferences.theme_mode or "system",
        "brand_color": preferences.brand_color,
        "accent_color": preferences.accent_color,
        "gradient_start": preferences.gradient_start,
        "gradient_end": preferences.gradient_end,
        "card_appearance": preferences.card_appearance or "subtle",
        "border_radius_style": preferences.border_radius_style or "medium",
        "dashboard_density": preferences.dashboard_density or "balanced",
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if data.role not in ALLOWED_PUBLIC_ROLES:
        raise HTTPException(status_code=400, detail="Invalid public registration role")
    if data.role == "provider" and not data.vehicle_number:
        raise HTTPException(status_code=400, detail="Vehicle number is required for provider registration")

    try:
        supabase_password_sign_up(data.email, data.password, data.username)
    except HTTPException:
        # Supabase is used as an optional external auth mirror for OAuth/password
        # accounts. Local development and the Streamlit password flow should still
        # be able to create the app account when Supabase blocks password signup
        # because email confirmation is enabled or the service is unavailable.
        pass

    user = register_user(
        db,
        username=data.username,
        email=data.email,
        password=data.password,
        role=data.role,
        vehicle_number=data.vehicle_number,
        phone=data.phone,
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
    try:
        supabase_password_sign_in(data.email, data.password)
    except HTTPException:
        # Do not block local JWT login on Supabase password status. Supabase can
        # reject sign-in for unconfirmed emails while the local account is valid.
        pass
    return {"access_token": create_access_token(data={"sub": user.email, "role": user.role})}


@router.post("/password/reset")
def reset_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.strip().lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")

    supabase_send_password_reset(data.email)
    user.hashed_password = get_password_hash(data.new_password)
    user.failed_login_count = 0
    user.locked_until = None
    db.commit()
    return {"message": "Password reset link sent. Local password has been updated for this development backend."}


@router.post("/supabase/session", response_model=TokenResponse)
def supabase_session_login(data: SupabaseSessionRequest, db: Session = Depends(get_db)):
    user = login_with_supabase_session(db, data.access_token)
    return {"access_token": create_access_token(data={"sub": user.email, "role": user.role})}


@router.post("/login/phone/request-otp", response_model=OtpChallengeResponse)
def phone_login_request_otp(data: PhoneOtpRequest):
    return request_phone_otp(data.phone)


@router.post("/login/phone/verify", response_model=TokenResponse)
def phone_login_verify(data: PhoneOtpVerifyRequest, db: Session = Depends(get_db)):
    user = verify_phone_otp(db, data.phone, data.otp_code, data.username)
    return {"access_token": create_access_token(data={"sub": user.email, "role": user.role})}


@router.post("/login/email/request-otp", response_model=OtpChallengeResponse)
def email_login_request_otp(data: EmailOtpRequest):
    if data.role not in ALLOWED_PUBLIC_ROLES:
        raise HTTPException(status_code=400, detail="Invalid public login role")
    return request_email_otp(data.email)


@router.post("/login/email/verify", response_model=TokenResponse)
def email_login_verify(data: EmailOtpVerifyRequest, db: Session = Depends(get_db)):
    if data.role not in ALLOWED_PUBLIC_ROLES:
        raise HTTPException(status_code=400, detail="Invalid public login role")
    user = verify_email_otp(db, data.email, data.otp_code, data.username, data.role)
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


@router.get("/me/preferences", response_model=UserPreferenceResponse)
def get_my_preferences(current_user: User = Depends(get_current_user)):
    return _preferences_response(current_user.preferences, current_user.id)


@router.put("/me/preferences", response_model=UserPreferenceResponse)
def update_my_preferences(
    data: UserPreferenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_preferences(data)
    preferences = current_user.preferences
    if not preferences:
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(preferences, field, value)

    db.commit()
    db.refresh(preferences)
    return _preferences_response(preferences, current_user.id)
