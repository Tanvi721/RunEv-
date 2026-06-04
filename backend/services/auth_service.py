import bcrypt
import jwt
import os
import random
import re
import requests
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from fastapi import HTTPException, status
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from backend.models import User, Provider
from backend.core.validation import (
    normalize_email as strict_normalize_email,
    normalize_indian_mobile,
    normalize_vehicle_number,
    validate_password,
)

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "b42312bbd986cdf6e901a5c82fdf6d1165287948dfea21fdabc90e17f35ef2c7")
ALGORITHM = "HS256"
PHONE_OTP_TTL_SECONDS = int(os.getenv("PHONE_OTP_TTL_SECONDS", "300"))
PHONE_OTP_DEV_MODE = os.getenv("PHONE_OTP_DEV_MODE", "true").lower() in {"1", "true", "yes", "on"}
PHONE_OTP_PROVIDER = os.getenv("PHONE_OTP_PROVIDER", "local").lower()
EMAIL_OTP_TTL_SECONDS = int(os.getenv("EMAIL_OTP_TTL_SECONDS", str(PHONE_OTP_TTL_SECONDS)))
EMAIL_OTP_PROVIDER = os.getenv("EMAIL_OTP_PROVIDER", "smtp").lower()
EMAIL_OTP_DEV_MODE = os.getenv("EMAIL_OTP_DEV_MODE", "true").lower() in {"1", "true", "yes", "on"}
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
MAX_FAILED_LOGIN_ATTEMPTS = int(os.getenv("MAX_FAILED_LOGIN_ATTEMPTS", "5"))
LOGIN_LOCKOUT_MINUTES = int(os.getenv("LOGIN_LOCKOUT_MINUTES", "15"))
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM") or SMTP_USERNAME
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
DEFAULT_PHONE_COUNTRY_CODE = os.getenv("DEFAULT_PHONE_COUNTRY_CODE", "+91")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")
TWILIO_VERIFY_CHANNEL = os.getenv("TWILIO_VERIFY_CHANNEL", "sms")
_phone_otp_store: dict[str, dict[str, object]] = {}
_email_otp_store: dict[str, dict[str, object]] = {}

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def authenticate_user(db: Session, email: str, password: str):
    normalized_email = normalize_email(email)
    user = db.query(User).filter(User.email == normalized_email).first()
    if not user:
        return None
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed sign-in attempts. Try again after {user.locked_until.isoformat()} UTC.",
        )
    if not verify_password(password, user.hashed_password):
        user.failed_login_count = int(user.failed_login_count or 0) + 1
        if user.failed_login_count >= MAX_FAILED_LOGIN_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
        db.commit()
        return None
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    db.commit()
    return user


def normalize_phone(phone: str) -> str:
    cleaned = re.sub(r"[\s\-().]", "", phone or "")
    if cleaned.startswith("+"):
        number = "+" + re.sub(r"\D", "", cleaned[1:])
    else:
        number = re.sub(r"\D", "", cleaned)
        if len(number) == 10:
            number = f"{DEFAULT_PHONE_COUNTRY_CODE}{number}"
    if len(number.lstrip("+")) < 8:
        raise HTTPException(status_code=400, detail="Enter a valid phone number")
    return number


def normalize_email(email: str) -> str:
    try:
        return strict_normalize_email(email)
    except ValueError:
        raise HTTPException(status_code=400, detail="Enter a valid email")


def twilio_verify_configured() -> bool:
    return bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_VERIFY_SERVICE_SID)


def request_twilio_phone_otp(phone: str) -> dict:
    if not twilio_verify_configured():
        raise HTTPException(status_code=500, detail="SMS verification is not configured")

    url = f"https://verify.twilio.com/v2/Services/{TWILIO_VERIFY_SERVICE_SID}/Verifications"
    try:
        response = requests.post(
            url,
            data={"To": phone, "Channel": TWILIO_VERIFY_CHANNEL},
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=10,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Could not send OTP right now") from exc

    if response.status_code >= 400:
        try:
            provider_detail = response.json().get("message") or response.json().get("detail")
        except ValueError:
            provider_detail = response.text
        raise HTTPException(status_code=502, detail=f"OTP provider rejected the request: {provider_detail or response.status_code}")

    return {
        "message": "OTP sent to your phone number",
        "expires_in_seconds": PHONE_OTP_TTL_SECONDS,
        "delivery_channel": TWILIO_VERIFY_CHANNEL,
        "dev_otp": None,
    }


def request_local_phone_otp(phone: str) -> dict:
    normalized_phone = normalize_phone(phone)
    otp_code = f"{random.SystemRandom().randint(0, 999999):06d}"
    expires_at = datetime.utcnow() + timedelta(seconds=PHONE_OTP_TTL_SECONDS)
    _phone_otp_store[normalized_phone] = {
        "otp_code": otp_code,
        "expires_at": expires_at,
        "attempts": 0,
    }
    print(f"RunEV login OTP for {normalized_phone}: {otp_code}")
    return {
        "message": "OTP sent to your phone number",
        "expires_in_seconds": PHONE_OTP_TTL_SECONDS,
        "delivery_channel": "sms",
        "dev_otp": otp_code if PHONE_OTP_DEV_MODE else None,
    }


def request_phone_otp(phone: str) -> dict:
    normalized_phone = normalize_phone(phone)
    if PHONE_OTP_PROVIDER == "twilio":
        return request_twilio_phone_otp(normalized_phone)
    return request_local_phone_otp(normalized_phone)


def send_email_otp(email: str, otp_code: str, subject: str = "Your RunEV verification code", body: str | None = None) -> None:
    if EMAIL_OTP_PROVIDER != "smtp":
        print(f"RunEV email OTP for {email}: {otp_code}")
        return

    if not SMTP_HOST or not SMTP_FROM:
        raise HTTPException(status_code=500, detail="Email verification is not configured")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = email
    message.set_content(body or f"Your RunEV verification code is {otp_code}.\n\nThis code expires in {EMAIL_OTP_TTL_SECONDS // 60} minutes.")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            if SMTP_USE_TLS:
                server.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
    except OSError as exc:
        raise HTTPException(status_code=502, detail="Could not send email OTP right now") from exc


def send_trip_otp_email(email: str, otp_code: str) -> None:
    send_email_otp(
        email,
        otp_code,
        subject="Your RunEV trip OTP",
        body=(
            f"Your RunEV trip OTP is {otp_code}.\n\n"
            "Share this code with the driver only after the charging van reaches you."
        ),
    )


def request_email_otp(email: str) -> dict:
    normalized_email = normalize_email(email)
    otp_code = f"{random.SystemRandom().randint(0, 999999):06d}"
    expires_at = datetime.utcnow() + timedelta(seconds=EMAIL_OTP_TTL_SECONDS)
    _email_otp_store[normalized_email] = {
        "otp_code": otp_code,
        "expires_at": expires_at,
        "attempts": 0,
    }
    send_email_otp(normalized_email, otp_code)
    return {
        "message": "OTP sent to your email",
        "expires_in_seconds": EMAIL_OTP_TTL_SECONDS,
        "delivery_channel": "email",
        "dev_otp": otp_code if EMAIL_OTP_PROVIDER != "smtp" and EMAIL_OTP_DEV_MODE else None,
    }


def get_or_create_phone_user(db: Session, phone: str, username: str | None = None) -> User:
    normalized_phone = normalize_phone(phone)
    user = db.query(User).filter(User.phone == normalized_phone).first()
    if user:
        if username and user.username != username:
            user.username = username
            db.commit()
            db.refresh(user)
        return user

    phone_digits = re.sub(r"\D", "", normalized_phone)
    new_user = User(
        username=username or f"RunEV User {phone_digits[-4:]}",
        email=f"{phone_digits}@phone.runev.local",
        hashed_password=get_password_hash(os.urandom(16).hex()),
        role="user",
        phone=normalized_phone,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_or_create_email_user(db: Session, email: str, username: str | None = None, role: str = "user") -> User:
    normalized_email = normalize_email(email)
    user = db.query(User).filter(User.email == normalized_email).first()
    if user:
        if username and user.username != username:
            user.username = username
            db.commit()
            db.refresh(user)
        return user

    if role == "provider":
        raise HTTPException(status_code=404, detail="Create your fleet account before email OTP login")

    local_name = normalized_email.split("@")[0].replace(".", " ").replace("_", " ").strip()
    new_user = User(
        username=username or local_name.title() or "RunEV User",
        email=normalized_email,
        hashed_password=get_password_hash(os.urandom(16).hex()),
        role="user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def verify_twilio_phone_otp(phone: str, otp_code: str) -> None:
    if not twilio_verify_configured():
        raise HTTPException(status_code=500, detail="SMS verification is not configured")

    url = f"https://verify.twilio.com/v2/Services/{TWILIO_VERIFY_SERVICE_SID}/VerificationCheck"
    try:
        response = requests.post(
            url,
            data={"To": phone, "Code": otp_code.strip()},
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=10,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Could not verify OTP right now") from exc

    if response.status_code >= 400:
        try:
            provider_detail = response.json().get("message") or response.json().get("detail")
        except ValueError:
            provider_detail = response.text
        raise HTTPException(status_code=400, detail=f"Invalid OTP: {provider_detail or response.status_code}")
    if response.json().get("status") != "approved":
        raise HTTPException(status_code=400, detail="Invalid OTP")


def verify_local_phone_otp(phone: str, otp_code: str) -> None:
    normalized_phone = normalize_phone(phone)
    challenge = _phone_otp_store.get(normalized_phone)
    if not challenge:
        raise HTTPException(status_code=400, detail="Please request a fresh OTP")
    if datetime.utcnow() > challenge["expires_at"]:
        _phone_otp_store.pop(normalized_phone, None)
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new one")

    challenge["attempts"] = int(challenge.get("attempts", 0)) + 1
    if challenge["attempts"] > 5:
        _phone_otp_store.pop(normalized_phone, None)
        raise HTTPException(status_code=400, detail="Too many OTP attempts. Please request a new one")

    if str(otp_code).strip() != challenge["otp_code"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    _phone_otp_store.pop(normalized_phone, None)


def verify_phone_otp(db: Session, phone: str, otp_code: str, username: str | None = None) -> User:
    normalized_phone = normalize_phone(phone)
    if PHONE_OTP_PROVIDER == "twilio":
        verify_twilio_phone_otp(normalized_phone, otp_code)
    else:
        verify_local_phone_otp(normalized_phone, otp_code)
    return get_or_create_phone_user(db, normalized_phone, username)


def verify_local_email_otp(email: str, otp_code: str) -> None:
    normalized_email = normalize_email(email)
    challenge = _email_otp_store.get(normalized_email)
    if not challenge:
        raise HTTPException(status_code=400, detail="Please request a fresh OTP")
    if datetime.utcnow() > challenge["expires_at"]:
        _email_otp_store.pop(normalized_email, None)
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new one")

    challenge["attempts"] = int(challenge.get("attempts", 0)) + 1
    if challenge["attempts"] > 5:
        _email_otp_store.pop(normalized_email, None)
        raise HTTPException(status_code=400, detail="Too many OTP attempts. Please request a new one")

    if str(otp_code).strip() != challenge["otp_code"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    _email_otp_store.pop(normalized_email, None)


def verify_email_otp(db: Session, email: str, otp_code: str, username: str | None = None, role: str = "user") -> User:
    normalized_email = normalize_email(email)
    verify_local_email_otp(normalized_email, otp_code)
    return get_or_create_email_user(db, normalized_email, username, role)


def verify_supabase_access_token(access_token: str) -> dict:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Supabase authentication is not configured")

    try:
        response = requests.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Could not verify Supabase session") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=401, detail="Invalid Supabase session")
    return response.json()


def supabase_auth_request(path: str, payload: dict, token: str | None = None) -> dict:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Supabase authentication is not configured")
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {token or SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(f"{SUPABASE_URL}{path}", headers=headers, json=payload, timeout=15)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Could not reach Supabase authentication") from exc
    if response.status_code >= 400:
        try:
            detail = response.json().get("msg") or response.json().get("message") or response.json().get("error_description")
        except ValueError:
            detail = response.text
        raise HTTPException(status_code=400, detail=detail or "Supabase authentication failed")
    return response.json() if response.content else {}


def supabase_password_sign_up(email: str, password: str, username: str, redirect_to: str | None = None) -> dict:
    payload = {
        "email": normalize_email(email),
        "password": validate_password(password),
        "data": {"full_name": username, "name": username},
    }
    if redirect_to:
        payload["gotrue_meta_security"] = {"captcha_token": None}
        payload["options"] = {"email_redirect_to": redirect_to}
    return supabase_auth_request("/auth/v1/signup", payload)


def supabase_password_sign_in(email: str, password: str) -> dict:
    return supabase_auth_request(
        "/auth/v1/token?grant_type=password",
        {"email": normalize_email(email), "password": password},
    )


def supabase_send_password_reset(email: str, redirect_to: str | None = None) -> dict:
    payload = {"email": normalize_email(email)}
    if redirect_to:
        payload["gotrue_meta_security"] = {"captcha_token": None}
        payload["options"] = {"redirect_to": redirect_to}
    return supabase_auth_request("/auth/v1/recover", payload)


def login_with_supabase_session(db: Session, access_token: str) -> User:
    supabase_user = verify_supabase_access_token(access_token)
    email = normalize_email(supabase_user.get("email") or "")
    metadata = supabase_user.get("user_metadata") or {}
    username = (
        metadata.get("full_name")
        or metadata.get("name")
        or email.split("@")[0].replace(".", " ").replace("_", " ").title()
        or "RunEV User"
    )
    user = get_or_create_email_user(db, email, username, "user")
    user.auth_provider = "google"
    user.last_login_at = datetime.utcnow()
    user.failed_login_count = 0
    user.locked_until = None
    db.commit()
    db.refresh(user)
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

def register_user(db: Session, username: str, email: str, password: str, role: str = "user", vehicle_number: str = None, phone: str = None, auth_provider: str = "email"):
    normalized_email = normalize_email(email)
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        return None
    
    hashed_password = get_password_hash(validate_password(password))
    new_user = User(
        username=username,
        email=normalized_email,
        hashed_password=hashed_password,
        role=role,
        phone=normalize_indian_mobile(phone) if phone else None,
        auth_provider=auth_provider,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    if role == "provider" and vehicle_number:
        new_provider = Provider(user_id=new_user.id, vehicle_number=normalize_vehicle_number(vehicle_number))
        db.add(new_provider)
        db.commit()
        
    return new_user
