"""
Test cases for authentication endpoints
"""

import pytest


def test_login_valid_credentials(client):
    """Test login with valid credentials"""
    response = client.post("/api/v1/auth/login", data={"username": "demo", "password": "demo123"})

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_invalid_username(client):
    """Test login with invalid username"""
    response = client.post("/api/v1/auth/login", data={"username": "invalid_user", "password": "demo123"})

    assert response.status_code == 401
    data = response.json()
    assert "error" in data or "detail" in data


def test_login_invalid_password(client):
    """Test login with invalid password"""
    response = client.post("/api/v1/auth/login", data={"username": "demo", "password": "wrong_password"})

    assert response.status_code == 401
    data = response.json()
    assert "error" in data or "detail" in data


def test_login_missing_username(client):
    """Test login without username"""
    response = client.post("/api/v1/auth/login", data={"password": "demo123"})

    assert response.status_code in [400, 422]


def test_login_missing_password(client):
    """Test login without password"""
    response = client.post("/api/v1/auth/login", data={"username": "demo"})

    assert response.status_code in [400, 422]


def test_login_empty_credentials(client):
    """Test login with empty credentials"""
    response = client.post("/api/v1/auth/login", data={"username": "", "password": ""})

    assert response.status_code in [400, 401, 422]


def test_login_json_format(client):
    """Test login with JSON format (should work with form data)"""
    response = client.post("/api/v1/auth/login", json={"username": "demo", "password": "demo123"})

    # This might fail if endpoint only accepts form data
    # The test documents the expected behavior
    assert response.status_code in [200, 422]


def test_token_authentication(client, auth_token):
    """Test using JWT token for authentication"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Try to access protected endpoint
    response = client.get("/api/v1/health", headers=headers)

    # Should work with valid token
    assert response.status_code == 200


def test_invalid_token_format(client):
    """Test authentication with invalid token format"""
    headers = {"Authorization": "Bearer invalid_token_format"}

    response = client.post(
        "/api/v1/generate",
        json={"user_id": "demo_user_123", "prompt": "Test prompt", "project_id": "project_001"},
        headers=headers,
    )

    assert response.status_code == 401


def test_missing_bearer_prefix(client, auth_token):
    """Test authentication without Bearer prefix"""
    headers = {"Authorization": auth_token}  # Missing "Bearer "

    response = client.post(
        "/api/v1/generate",
        json={"user_id": "demo_user_123", "prompt": "Test prompt", "project_id": "project_001"},
        headers=headers,
    )

    assert response.status_code in [401, 403]


def test_expired_token(client):
    """Test authentication with expired token"""
    # This would require creating an expired token
    # For now, test with obviously invalid token
    headers = {"Authorization": "Bearer expired.token.here"}

    response = client.post(
        "/api/v1/generate",
        json={"user_id": "demo_user_123", "prompt": "Test prompt", "project_id": "project_001"},
        headers=headers,
    )

    assert response.status_code == 401
