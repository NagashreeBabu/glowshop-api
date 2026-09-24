import pytest
import json
from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret"
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_success(client):
    response = client.post("/api/auth/register", json={
        "username": "glowuser",
        "email": "glow@test.com",
        "password": "password123",
        "skin_type": "Oily"
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "Welcome to GlowShop" in data["message"]

def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={
        "username": "user1", "email": "test@test.com", "password": "pass123"
    })
    response = client.post("/api/auth/register", json={
        "username": "user2", "email": "test@test.com", "password": "pass456"
    })
    assert response.status_code == 409

def test_register_missing_fields(client):
    response = client.post("/api/auth/register", json={"username": "user1"})
    assert response.status_code == 400

def test_login_success(client):
    client.post("/api/auth/register", json={
        "username": "skinuser", "email": "skin@test.com", "password": "mypassword"
    })
    response = client.post("/api/auth/login", json={
        "email": "skin@test.com", "password": "mypassword"
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "token" in data
    assert data["username"] == "skinuser"

def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "user3", "email": "user3@test.com", "password": "correctpassword"
    })
    response = client.post("/api/auth/login", json={
        "email": "user3@test.com", "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    response = client.post("/api/auth/login", json={
        "email": "nobody@test.com", "password": "anypassword"
    })
    assert response.status_code == 401
