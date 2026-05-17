from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import Provider, ServiceRequest, User
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


def seed_completed_request(SessionLocal):
    db = SessionLocal()
    try:
        user = User(
            username="Passenger",
            email="passenger@example.com",
            hashed_password=get_password_hash("secret123"),
            role="user",
        )
        provider_user = User(
            username="Driver",
            email="driver@example.com",
            hashed_password=get_password_hash("secret123"),
            role="provider",
        )
        db.add_all([user, provider_user])
        db.commit()
        db.refresh(user)
        db.refresh(provider_user)

        provider = Provider(
            user_id=provider_user.id,
            vehicle_number="EV-101",
            current_lat=18.5204,
            current_lng=73.8567,
            is_available=True,
        )
        db.add(provider)
        db.commit()
        db.refresh(provider)

        service_request = ServiceRequest(
            user_id=user.id,
            provider_id=provider.id,
            pickup_lat=18.52,
            pickup_lng=73.85,
            status="completed",
            total_price=250,
        )
        db.add(service_request)
        db.commit()
        db.refresh(service_request)
        return user, provider, service_request
    finally:
        db.close()


def test_user_can_rate_completed_request_and_provider_average_is_exposed():
    client, SessionLocal = build_test_client()
    try:
        user, provider, service_request = seed_completed_request(SessionLocal)

        response = client.post(
            "/api/v1/ratings",
            headers=auth_headers(user),
            json={"request_id": service_request.id, "score": 5, "comment": "Quick and polite"},
        )

        assert response.status_code == 201
        assert response.json()["score"] == 5

        providers_response = client.get("/api/v1/providers", headers=auth_headers(user))
        assert providers_response.status_code == 200
        [provider_payload] = providers_response.json()
        assert provider_payload["id"] == provider.id
        assert provider_payload["average_rating"] == 5.0
        assert provider_payload["rating_count"] == 1
    finally:
        app.dependency_overrides.clear()


def test_rating_same_request_updates_existing_rating():
    client, SessionLocal = build_test_client()
    try:
        user, provider, service_request = seed_completed_request(SessionLocal)
        headers = auth_headers(user)

        first = client.post(
            "/api/v1/ratings",
            headers=headers,
            json={"request_id": service_request.id, "score": 3},
        )
        second = client.post(
            "/api/v1/ratings",
            headers=headers,
            json={"request_id": service_request.id, "score": 4, "comment": "Updated"},
        )

        assert first.status_code == 201
        assert second.status_code == 201
        assert second.json()["id"] == first.json()["id"]

        summary = client.get(f"/api/v1/ratings/provider/{provider.id}", headers=headers)
        assert summary.status_code == 200
        assert summary.json()["average_rating"] == 4.0
        assert summary.json()["rating_count"] == 1
    finally:
        app.dependency_overrides.clear()


def test_user_cannot_rate_unfinished_request():
    client, SessionLocal = build_test_client()
    try:
        user, provider, service_request = seed_completed_request(SessionLocal)
        db = SessionLocal()
        try:
            unfinished = ServiceRequest(
                user_id=user.id,
                provider_id=provider.id,
                pickup_lat=18.52,
                pickup_lng=73.85,
                status="charging",
            )
            db.add(unfinished)
            db.commit()
            db.refresh(unfinished)
            unfinished_id = unfinished.id
        finally:
            db.close()

        response = client.post(
            "/api/v1/ratings",
            headers=auth_headers(user),
            json={"request_id": unfinished_id, "score": 5},
        )

        assert response.status_code == 400
        assert "completed" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
