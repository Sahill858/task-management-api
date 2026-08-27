from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_create_task(client, auth_headers):
    response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Learn automated testing",
            "description": "Write my first FastAPI test",
            "status": "pending",
            "priority": "high",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Learn automated testing"
    assert data["status"] == "pending"
    assert data["priority"] == "high"

def test_create_task_without_authentication(client):
    response = client.post(
        "/tasks/",
        json={
            "title": "Unauthorized task",
            "description": "This should not be created",
            "status": "pending",
            "priority": "high",
        },
    )

    assert response.status_code == 401

def test_login_wrong_password(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "sahil@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401

def test_get_current_user(client, auth_headers):
    response = client.get(
        "/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "sahil@example.com"
    assert data["is_active"] is True

def test_get_current_user_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_refresh_token(client, auth_headers):
    login_response = client.post(
        "/auth/login",
        json={
            "email": "sahil@example.com",
            "password": "hello123",
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_logout_revokes_refresh_token(client):
    login_response = client.post(
        "/auth/login",
        json={
            "email": "sahil@example.com",
            "password": "hello123",
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    logout_response = client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert logout_response.status_code == 200

    assert logout_response.json()["message"] == "Logged out successfully"

    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh_response.status_code == 401

def test_user_cannot_access_another_users_task(client):
    # Login as User A
    login_response = client.post(
        "/auth/login",
        json={
            "email": "sahil@example.com",
            "password": "hello123",
        },
    )

    assert login_response.status_code == 200

    user_a_token = login_response.json()["access_token"]

    user_a_headers = {
        "Authorization": f"Bearer {user_a_token}"
    }

    # Create a task as User A
    create_response = client.post(
        "/tasks/",
        headers=user_a_headers,
        json={
            "title": "User A private task",
            "description": "This belongs to User A",
            "status": "pending",
            "priority": "high",
        },
    )

    assert create_response.status_code == 200

    task_id = create_response.json()["id"]

    # Login as User B
    login_response = client.post(
        "/auth/login",
        json={
            "email": "sahil@xample.com",
            "password": "sahil123",
        },
    )

    assert login_response.status_code == 200

    user_b_token = login_response.json()["access_token"]

    user_b_headers = {
        "Authorization": f"Bearer {user_b_token}"
    }

    # User B tries to access User A's task
    response = client.get(
        f"/tasks/{task_id}",
        headers=user_b_headers,
    )

    assert response.status_code == 404 


def test_user_cannot_update_another_users_task(client):
    # Login as User A
    login_response = client.post(
        "/auth/login",
        json={
            "email": "sahil@example.com",
            "password": "hello123",
        },
    )

    assert login_response.status_code == 200

    user_a_token = login_response.json()["access_token"]

    # Create User A's task
    create_response = client.post(
        "/tasks/",
        headers={
            "Authorization": f"Bearer {user_a_token}"
        },
        json={
            "title": "User A task",
            "description": "Private task",
            "status": "pending",
            "priority": "high",
        },
    )

    assert create_response.status_code == 200

    task_id = create_response.json()["id"]

    # Login as User B
    login_response = client.post(
        "/auth/login",
        json={
            "email": "sahil@xample.com",
            "password": "sahil123",
        },
    )

    assert login_response.status_code == 200

    user_b_token = login_response.json()["access_token"]

    # User B tries to update User A's task
    response = client.patch(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {user_b_token}"
        },
        json={
            "title": "Hacked task",
        },
    )

    assert response.status_code == 404


def test_user_cannot_delete_another_users_task(client):
    # Login as User A
    login_response = client.post(
        "/auth/login",
        json={
            "email": "sahil@example.com",
            "password": "hello123",
        },
    )

    assert login_response.status_code == 200

    user_a_token = login_response.json()["access_token"]

    # Create User A's task
    create_response = client.post(
        "/tasks/",
        headers={
            "Authorization": f"Bearer {user_a_token}"
        },
        json={
            "title": "User A task",
            "description": "Private task",
            "status": "pending",
            "priority": "high",
        },
    )

    assert create_response.status_code == 200

    task_id = create_response.json()["id"]

    # Login as User B
    login_response = client.post(
        "/auth/login",
        json={
            "email": "sahil@xample.com",
            "password": "sahil123",
        },
    )

    assert login_response.status_code == 200

    user_b_token = login_response.json()["access_token"]

    # User B tries to delete User A's task
    response = client.delete(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {user_b_token}"
        },
    )

    assert response.status_code == 404

def test_login_with_wrong_password(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "sahil@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401

def test_create_task_without_authentication(client):
    response = client.post(
        "/tasks/",
        json={
            "title": "Unauthorized task",
            "description": "This should fail",
            "status": "pending",
            "priority": "high",
        },
    )

    assert response.status_code == 401

def test_get_nonexistent_task(client, auth_headers):
    response = client.get(
        "/tasks/999999",
        headers=auth_headers,
    )

    assert response.status_code == 404

def test_refresh_with_invalid_token(client):
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": "invalid-refresh-token",
        },
    )

    assert response.status_code == 401