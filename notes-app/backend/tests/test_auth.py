from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_password_hash
from app.models.user import User
from app.database.session import get_db
from sqlalchemy.orm import Session
from unittest.mock import patch

client = TestClient(app)

def test_register_user(client):
    response = client.post("/api/v1/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_login_user(client):
    # First register a user
    client.post("/api/v1/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "testpassword"
    })
    
    # Then try to login
    response = client.post("/api/v1/login", data={
        "username": "login@example.com",
        "password": "testpassword"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"