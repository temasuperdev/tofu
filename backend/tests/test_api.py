import pytest
import json
from fastapi.testclient import TestClient
from app.security.password import hash_password


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_register_user(client):
    """Test user registration endpoint."""
    user_data = {
        "username": "testregister",
        "email": "testregister@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code in [200, 201]

    data = response.json()
    assert "id" in data
    assert data["username"] == "testregister"
    assert data["email"] == "testregister@example.com"


def test_login_user(client, test_user):
    """Test user login endpoint."""
    # Сначала зарегистрируем пользователя, потому что хэшированный пароль отличается
    user_data = {
        "username": "test_login_user",
        "email": "test_login@example.com",
        "password": "testpassword123"
    }
    
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 200
    
    login_data = {
        "username": "test_login_user",
        "password": "testpassword123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client, test_user):
    """Test get current user endpoint."""
    # First login to get token
    login_data = {
        "username": test_user.username,
        "password": "password"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    # Then use token to get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == test_user.id
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


def test_create_category(client, test_user):
    """Test creating a category."""
    # Login first
    login_data = {
        "username": test_user.username,
        "password": "password"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    category_data = {
        "name": "API Test Category"
    }
    
    response = client.post("/api/v1/categories/", json=category_data, headers=headers)
    assert response.status_code in [200, 201]

    data = response.json()
    assert data["name"] == "API Test Category"
    assert data["user_id"] == test_user.id


def test_get_categories(client, test_user):
    """Test getting user's categories."""
    # Login first
    login_data = {
        "username": test_user.username,
        "password": "password"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/categories/", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_create_note(client, test_user, test_category):
    """Test creating a note."""
    # Login first
    login_data = {
        "username": test_user.username,
        "password": "password"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    note_data = {
        "title": "API Test Note",
        "content": "This is a test note created via API",
        "category_id": test_category.id
    }
    
    response = client.post("/api/v1/notes/", json=note_data, headers=headers)
    assert response.status_code in [200, 201]

    data = response.json()
    assert data["title"] == "API Test Note"
    assert data["content"] == "This is a test note created via API"
    assert data["user_id"] == test_user.id
    assert data["category_id"] == test_category.id


def test_get_notes(client, test_user):
    """Test getting user's notes."""
    # Login first
    login_data = {
        "username": test_user.username,
        "password": "password"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/notes/", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_get_note(client, test_user, test_note):
    """Test getting a specific note."""
    # Login first
    login_data = {
        "username": test_user.username,
        "password": "password"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(f"/api/v1/notes/{test_note.id}", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == test_note.id
    assert data["title"] == test_note.title


def test_update_note(client, test_user, test_note):
    """Test updating a note."""
    # Login first
    login_data = {
        "username": test_user.username,
        "password": "password"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "title": "Updated API Test Note",
        "content": "This is an updated test note",
        "category_id": test_note.category_id
    }
    
    response = client.put(f"/api/v1/notes/{test_note.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Updated API Test Note"
    assert data["content"] == "This is an updated test note"


def test_delete_note(client, test_user, test_note):
    """Test deleting a note."""
    # Login first
    login_data = {
        "username": test_user.username,
        "password": "password"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.delete(f"/api/v1/notes/{test_note.id}", headers=headers)
    assert response.status_code in [200, 204]
    
    if response.status_code == 200:
        data = response.json()
        assert "message" in data
    # При успешном удалении обычно возвращается 204 No Content или сообщение об успехе

def test_metrics_endpoint(client):
    """Test metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]