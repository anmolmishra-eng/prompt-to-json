"""
Simple test for generate endpoint without database dependency
"""

from unittest.mock import MagicMock, patch

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_generate_simple():
    """Test generate endpoint with mocked database"""

    # First login to get a real token
    login_response = client.post("/api/v1/auth/login", data={"username": "demo", "password": "demo123"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Test the endpoint with real auth token
    response = client.post(
        "/api/v1/generate",
        json={"user_id": "demo", "prompt": "Design a modern living room", "project_id": "test_project"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Should succeed now
    assert response.status_code == 200
    data = response.json()
    assert "spec_id" in data
    assert "spec_json" in data
    assert "preview_url" in data
