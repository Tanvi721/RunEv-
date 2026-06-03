import math
import re
from typing import Any

EMAIL_RE = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
FULL_NAME_RE = re.compile(r"^[A-Za-z ]+$")
INDIAN_MOBILE_RE = re.compile(r"^[6-9]\d{9}$")
VEHICLE_NUMBER_RE = re.compile(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$")
GST_RE = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
SPECIAL_RE = re.compile(r"[^A-Za-z0-9]")


def normalize_email(value: str) -> str:
    email = (value or "").strip().lower()
    if not EMAIL_RE.match(email):
        raise ValueError("Enter a valid email address.")
    return email


def validate_full_name(value: str, label: str = "Full name") -> str:
    name = " ".join((value or "").strip().split())
    if not 3 <= len(name) <= 50:
        raise ValueError(f"{label} must be 3 to 50 characters.")
    if not FULL_NAME_RE.match(name):
        raise ValueError(f"{label} can contain letters and spaces only.")
    return name


def validate_password(value: str) -> str:
    password = value or ""
    if not 8 <= len(password) <= 128:
        raise ValueError("Password must be 8 to 128 characters.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must include an uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must include a lowercase letter.")
    if not re.search(r"\d", password):
        raise ValueError("Password must include a number.")
    if not SPECIAL_RE.search(password):
        raise ValueError("Password must include a special character.")
    return password


def password_strength(value: str) -> str:
    score = 0
    password = value or ""
    score += len(password) >= 8
    score += len(password) >= 12
    score += bool(re.search(r"[A-Z]", password))
    score += bool(re.search(r"[a-z]", password))
    score += bool(re.search(r"\d", password))
    score += bool(SPECIAL_RE.search(password))
    if score <= 3:
        return "Weak"
    if score <= 5:
        return "Medium"
    return "Strong"


def normalize_indian_mobile(value: str) -> str:
    phone = re.sub(r"\D", "", value or "")
    if phone.startswith("91") and len(phone) == 12:
        phone = phone[2:]
    if not INDIAN_MOBILE_RE.match(phone):
        raise ValueError("Mobile number must be 10 digits and start with 6, 7, 8, or 9.")
    return phone


def normalize_vehicle_number(value: str) -> str:
    vehicle_number = re.sub(r"\s+", "", value or "").upper()
    if not VEHICLE_NUMBER_RE.match(vehicle_number):
        raise ValueError("Vehicle number must match Indian registration format, for example MH12EV0001.")
    return vehicle_number


def validate_fleet_name(value: str) -> str:
    name = " ".join((value or "").strip().split())
    if not 3 <= len(name) <= 100:
        raise ValueError("Fleet name must be 3 to 100 characters.")
    return name


def validate_gst_number(value: str | None) -> str | None:
    if not value:
        return None
    gst = value.strip().upper()
    if not GST_RE.match(gst):
        raise ValueError("Enter a valid Indian GST number.")
    return gst


def validate_latitude(value: Any, label: str = "Latitude") -> float:
    if value is None or not math.isfinite(float(value)) or not -90 <= float(value) <= 90:
        raise ValueError(f"{label} must be a finite number between -90 and 90.")
    return float(value)


def validate_longitude(value: Any, label: str = "Longitude") -> float:
    if value is None or not math.isfinite(float(value)) or not -180 <= float(value) <= 180:
        raise ValueError(f"{label} must be a finite number between -180 and 180.")
    return float(value)


def validate_file_upload(filename: str, size_bytes: int, max_size_bytes: int = 5 * 1024 * 1024) -> None:
    extension = (filename.rsplit(".", 1)[-1] if "." in filename else "").lower()
    if extension not in {"jpg", "jpeg", "png", "pdf"}:
        raise ValueError("Allowed upload types are jpg, jpeg, png, and pdf.")
    if size_bytes > max_size_bytes:
        raise ValueError("File must be 5 MB or smaller.")
