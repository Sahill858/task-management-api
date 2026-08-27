import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from main import app
from app.database import SessionLocal
from app.models.user import User
from app.security import hash_password


@pytest.fixture(scope="session", autouse=True)
def create_test_users():
    db = SessionLocal()

    try:
        users = [
            ("sahil@example.com", "hello123"),
            ("sahil@xample.com", "sahil123"),
        ]

        for email, password in users:
            existing_user = db.execute(
                select(User).where(User.email == email)
            ).scalar_one_or_none()

            if not existing_user:
                db.add(
                    User(
                        email=email,
                        password_hash=hash_password(password),
                        is_active=True,
                    )
                )

        db.commit()

    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user_a_headers(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "sahil@example.com",
            "password": "hello123",
        },
    )

    assert response.status_code == 200

    access_token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}"
    }


@pytest.fixture
def auth_headers(user_a_headers):
    return user_a_headers


@pytest.fixture
def user_b_headers(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "sahil@xample.com",
            "password": "sahil123",
        },
    )

    assert response.status_code == 200

    access_token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}"
    }