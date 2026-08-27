import pytest
from fastapi.testclient import TestClient

from main import app


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

