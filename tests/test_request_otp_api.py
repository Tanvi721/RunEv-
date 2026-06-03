from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import Provider, ServiceRequest, User
from backend.services import auth_service
from backend.services.auth_service import create_access_token, get_password_hash


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
    return TestClient(app), TestingSessionLocal


def auth_headers(user: User) -> dict:
    token = create_access_token({"sub": user.email, "role": user.role})
    return {"Authorization": f"Bearer {token}"}


def seed_request(SessionLocal):
    db = SessionLocal()
    try:
        user = User(
            username="Passenger",
            email="passenger-otp@example.com",
            hashed_password=get_password_hash("secret123"),
            role="user",
            phone="9000000001",
        )
        provider_user = User(
            username="Driver",
            email="driver-otp@example.com",
            hashed_password=get_password_hash("secret123"),
            role="provider",
            phone="9000000002",
        )
        db.add_all([user, provider_user])
        db.commit()
        db.refresh(user)
        db.refresh(provider_user)

        provider = Provider(
            user_id=provider_user.id,
            vehicle_number="EV-OTP",
            current_lat=18.5204,
            current_lng=73.8567,
            is_available=True,
            driver_name="RunEV Driver",
        )
        db.add(provider)
        db.commit()
        db.refresh(provider)

        service_request = ServiceRequest(
            user_id=user.id,
            provider_id=provider.id,
            pickup_lat=18.52,
            pickup_lng=73.85,
            status="pending",
        )
        db.add(service_request)
        db.commit()
        db.refresh(service_request)
        return user, provider_user, provider, service_request
    finally:
        db.close()


def use_local_email_otp():
    original_provider = auth_service.EMAIL_OTP_PROVIDER
    auth_service.EMAIL_OTP_PROVIDER = "local"
    return original_provider


def test_accept_generates_email_only_otp_and_contact_details():
    client, SessionLocal = build_test_client()
    original_provider = use_local_email_otp()
    try:
        user, provider_user, _, service_request = seed_request(SessionLocal)

        accept_response = client.post(
            f"/api/v1/requests/charge/{service_request.id}/accept",
            headers=auth_headers(provider_user),
        )
        assert accept_response.status_code == 200

        passenger_response = client.get(
            f"/api/v1/requests/charge/{service_request.id}",
            headers=auth_headers(user),
        )
        payload = passenger_response.json()
        assert payload["otp_code"].isdigit()
        assert len(payload["otp_code"]) == 6
        assert payload["provider"]["phone"] == "9000000002"
        assert payload["user"]["phone"] == "9000000001"

        db = SessionLocal()
        try:
            stored_request = db.get(ServiceRequest, service_request.id)
            assert stored_request.otp_code.isdigit()
            assert len(stored_request.otp_code) == 6
        finally:
            db.close()
    finally:
        auth_service.EMAIL_OTP_PROVIDER = original_provider
        app.dependency_overrides.clear()


def test_accept_does_not_fail_when_smtp_is_not_configured():
    client, SessionLocal = build_test_client()
    original_provider = auth_service.EMAIL_OTP_PROVIDER
    original_host = auth_service.SMTP_HOST
    auth_service.EMAIL_OTP_PROVIDER = "smtp"
    auth_service.SMTP_HOST = None
    try:
        _, provider_user, _, service_request = seed_request(SessionLocal)

        accept_response = client.post(
            f"/api/v1/requests/charge/{service_request.id}/accept",
            headers=auth_headers(provider_user),
        )
        assert accept_response.status_code == 200
        assert accept_response.json()["status"] == "en_route"

        db = SessionLocal()
        try:
            stored_request = db.get(ServiceRequest, service_request.id)
            assert stored_request.otp_code.isdigit()
            assert len(stored_request.otp_code) == 6
        finally:
            db.close()
    finally:
        auth_service.EMAIL_OTP_PROVIDER = original_provider
        auth_service.SMTP_HOST = original_host
        app.dependency_overrides.clear()


def test_driver_must_verify_otp_before_charging_starts():
    client, SessionLocal = build_test_client()
    original_provider = use_local_email_otp()
    try:
        _, provider_user, _, service_request = seed_request(SessionLocal)
        client.post(
            f"/api/v1/requests/charge/{service_request.id}/accept",
            headers=auth_headers(provider_user),
        )
        db = SessionLocal()
        try:
            stored_request = db.get(ServiceRequest, service_request.id)
            otp_code = stored_request.otp_code
        finally:
            db.close()
        client.post(
            f"/api/v1/requests/charge/{service_request.id}/arrived",
            headers=auth_headers(provider_user),
        )

        invalid_response = client.post(
            f"/api/v1/requests/charge/{service_request.id}/start-charging",
            headers=auth_headers(provider_user),
            json={"otp_code": "000000"},
        )
        assert invalid_response.status_code == 400

        valid_response = client.post(
            f"/api/v1/requests/charge/{service_request.id}/start-charging",
            headers=auth_headers(provider_user),
            json={"otp_code": otp_code},
        )
        assert valid_response.status_code == 200
        assert valid_response.json()["status"] == "charging"
        assert valid_response.json()["otp_verified_at"] is not None
    finally:
        auth_service.EMAIL_OTP_PROVIDER = original_provider
        app.dependency_overrides.clear()


def test_arrived_trip_without_otp_gets_one_when_passenger_opens_status():
    client, SessionLocal = build_test_client()
    original_provider = use_local_email_otp()
    try:
        user, _, _, service_request = seed_request(SessionLocal)
        db = SessionLocal()
        try:
            stored_request = db.get(ServiceRequest, service_request.id)
            stored_request.status = "arrived"
            stored_request.otp_code = None
            db.commit()
        finally:
            db.close()

        response = client.get(
            f"/api/v1/requests/charge/{service_request.id}",
            headers=auth_headers(user),
        )
        payload = response.json()
        assert response.status_code == 200
        assert payload["otp_code"].isdigit()
        assert len(payload["otp_code"]) == 6

        db = SessionLocal()
        try:
            stored_request = db.get(ServiceRequest, service_request.id)
            assert stored_request.otp_code.isdigit()
            assert len(stored_request.otp_code) == 6
        finally:
            db.close()
    finally:
        auth_service.EMAIL_OTP_PROVIDER = original_provider
        app.dependency_overrides.clear()
