from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.services import auth_service


def build_test_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_phone_otp_login_creates_user_and_returns_token():
    client = build_test_client()
    original_provider = auth_service.PHONE_OTP_PROVIDER
    original_dev_mode = auth_service.PHONE_OTP_DEV_MODE
    auth_service.PHONE_OTP_PROVIDER = "local"
    auth_service.PHONE_OTP_DEV_MODE = True
    try:
        otp_response = client.post(
            "/api/v1/auth/login/phone/request-otp",
            json={"phone": "+91 90000 00001", "username": "Phone User"},
        )
        assert otp_response.status_code == 200
        otp_code = otp_response.json()["dev_otp"]
        assert otp_code.isdigit()

        verify_response = client.post(
            "/api/v1/auth/login/phone/verify",
            json={"phone": "+91 90000 00001", "otp_code": otp_code, "username": "Phone User"},
        )
        assert verify_response.status_code == 200
        token = verify_response.json()["access_token"]

        profile_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert profile_response.status_code == 200
        assert profile_response.json()["phone"] == "+919000000001"
    finally:
        auth_service.PHONE_OTP_PROVIDER = original_provider
        auth_service.PHONE_OTP_DEV_MODE = original_dev_mode
        app.dependency_overrides.clear()


def test_supabase_session_login_verifies_supabase_user_and_returns_token(monkeypatch):
    client = build_test_client()

    def fake_verify_supabase_access_token(access_token):
        assert access_token == "supabase_access_token_for_google"
        return {
            "email": "oauth.rider@example.com",
            "user_metadata": {"full_name": "OAuth Rider"},
            "app_metadata": {"provider": "google"},
        }

    monkeypatch.setattr(auth_service, "verify_supabase_access_token", fake_verify_supabase_access_token)
    try:
        login_response = client.post(
            "/api/v1/auth/supabase/session",
            json={"access_token": "supabase_access_token_for_google", "refresh_token": "refresh"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        profile_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert profile_response.status_code == 200
        assert profile_response.json()["email"] == "oauth.rider@example.com"
        assert profile_response.json()["username"] == "OAuth Rider"
    finally:
        app.dependency_overrides.clear()


def test_user_preferences_default_and_update():
    client = build_test_client()
    original_provider = auth_service.EMAIL_OTP_PROVIDER
    auth_service.EMAIL_OTP_PROVIDER = "local"
    try:
        otp_response = client.post(
            "/api/v1/auth/login/email/request-otp",
            json={"email": "theme.user@example.com", "username": "Theme User"},
        )
        assert otp_response.status_code == 200
        otp_code = auth_service._email_otp_store["theme.user@example.com"]["otp_code"]
        login_response = client.post(
            "/api/v1/auth/login/email/verify",
            json={"email": "theme.user@example.com", "otp_code": otp_code, "username": "Theme User"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        default_response = client.get("/api/v1/auth/me/preferences", headers=headers)
        assert default_response.status_code == 200
        assert default_response.json()["theme_mode"] == "system"

        update_response = client.put(
            "/api/v1/auth/me/preferences",
            headers=headers,
            json={"theme_mode": "dark", "dashboard_density": "compact"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["theme_mode"] == "dark"
        assert update_response.json()["dashboard_density"] == "compact"

        restored_response = client.get("/api/v1/auth/me/preferences", headers=headers)
        assert restored_response.json()["theme_mode"] == "dark"
    finally:
        auth_service.EMAIL_OTP_PROVIDER = original_provider
        app.dependency_overrides.clear()


def test_user_preferences_reject_invalid_theme():
    client = build_test_client()
    original_provider = auth_service.EMAIL_OTP_PROVIDER
    auth_service.EMAIL_OTP_PROVIDER = "local"
    try:
        client.post(
            "/api/v1/auth/login/email/request-otp",
            json={"email": "bad.theme@example.com", "username": "Bad Theme"},
        )
        otp_code = auth_service._email_otp_store["bad.theme@example.com"]["otp_code"]
        login_response = client.post(
            "/api/v1/auth/login/email/verify",
            json={"email": "bad.theme@example.com", "otp_code": otp_code, "username": "Bad Theme"},
        )
        token = login_response.json()["access_token"]

        response = client.put(
            "/api/v1/auth/me/preferences",
            headers={"Authorization": f"Bearer {token}"},
            json={"theme_mode": "midnight"},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid theme mode"
    finally:
        auth_service.EMAIL_OTP_PROVIDER = original_provider
        app.dependency_overrides.clear()


def test_driver_password_reset_updates_provider_password():
    client = build_test_client()
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "Fleet Reset",
            "email": "fleet.reset@example.com",
            "password": "oldpass123",
            "role": "provider",
            "vehicle_number": "MH12RESET",
        },
    )
    assert register_response.status_code == 201

    reset_response = client.post(
        "/api/v1/auth/password/reset",
        json={"email": "fleet.reset@example.com", "new_password": "newpass123"},
    )
    assert reset_response.status_code == 200

    old_login = client.post("/api/v1/auth/login", json={"email": "fleet.reset@example.com", "password": "oldpass123"})
    assert old_login.status_code == 401

    new_login = client.post("/api/v1/auth/login", json={"email": "fleet.reset@example.com", "password": "newpass123"})
    assert new_login.status_code == 200
    app.dependency_overrides.clear()


def test_email_otp_login_creates_user_and_returns_token():
    client = build_test_client()
    original_provider = auth_service.EMAIL_OTP_PROVIDER
    auth_service.EMAIL_OTP_PROVIDER = "local"
    try:
        otp_response = client.post(
            "/api/v1/auth/login/email/request-otp",
            json={"email": "email.otp@example.com", "username": "Email User"},
        )
        assert otp_response.status_code == 200
        otp_code = auth_service._email_otp_store["email.otp@example.com"]["otp_code"]
        assert otp_code.isdigit()

        verify_response = client.post(
            "/api/v1/auth/login/email/verify",
            json={"email": "email.otp@example.com", "otp_code": otp_code, "username": "Email User"},
        )
        assert verify_response.status_code == 200
        token = verify_response.json()["access_token"]

        profile_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert profile_response.status_code == 200
        assert profile_response.json()["email"] == "email.otp@example.com"
        assert profile_response.json()["username"] == "Email User"
    finally:
        auth_service.EMAIL_OTP_PROVIDER = original_provider
        app.dependency_overrides.clear()
