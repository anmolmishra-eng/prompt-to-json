"""
Test cases for POST /api/v1/generate endpoint
"""

import pytest
from app.models import Spec


def test_generate_valid_prompt(client, auth_headers, sample_spec_data):
    """Test generating spec from valid prompt"""
    response = client.post(
        "/api/v1/generate",
        json={
            "user_id": "demo_user_123",
            "prompt": "Design a modern living room with marble floor and grey sofa",
            "project_id": "project_001",
            "context": {"style": "modern", "budget": 50000}
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify required response fields
    assert "spec_id" in data
    assert "spec_json" in data
    assert "preview_url" in data
    assert "created_at" in data
    assert "spec_version" in data
    
    # Verify spec structure
    spec = data["spec_json"]
    assert "objects" in spec
    assert isinstance(spec["objects"], list)
    assert len(spec["objects"]) > 0
    
    # Each object should have required fields
    for obj in spec["objects"]:
        assert "id" in obj
        assert "type" in obj
        assert "material" in obj


def test_generate_missing_prompt(client, auth_headers):
    """Test error when prompt is missing"""
    response = client.post(
        "/api/v1/generate",
        json={
            "user_id": "demo_user_123",
            "project_id": "project_001"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error


def test_generate_short_prompt(client, auth_headers):
    """Test error when prompt is too short"""
    response = client.post(
        "/api/v1/generate",
        json={
            "user_id": "demo_user_123",
            "prompt": "Room",  # Too short
            "project_id": "project_001"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "error_code" in data or "detail" in data


def test_generate_long_prompt(client, auth_headers):
    """Test error when prompt exceeds max length"""
    response = client.post(
        "/api/v1/generate",
        json={
            "user_id": "demo_user_123",
            "prompt": "x" * 6000,  # Too long
            "project_id": "project_001"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 400


def test_generate_missing_user_id(client, auth_headers):
    """Test error when user_id is missing"""
    response = client.post(
        "/api/v1/generate",
        json={
            "prompt": "Design a modern living room",
            "project_id": "project_001"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422


def test_generate_without_auth(client):
    """Test that unauthenticated request is rejected"""
    response = client.post(
        "/api/v1/generate",
        json={
            "user_id": "demo_user_123",
            "prompt": "Design a modern living room",
            "project_id": "project_001"
        }
    )
    
    assert response.status_code == 401


def test_generate_preview_url_valid(client, auth_headers):
    """Test that preview URL is properly formatted and signed"""
    response = client.post(
        "/api/v1/generate",
        json={
            "user_id": "demo_user_123",
            "prompt": "Design a modern living room with marble floor",
            "project_id": "project_001"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    preview_url = response.json()["preview_url"]
    
    # Verify URL structure
    assert "previews" in preview_url or "glb" in preview_url
    assert preview_url.startswith("http://") or preview_url.startswith("https://")


def test_generate_with_context(client, auth_headers):
    """Test generation with additional context parameters"""
    response = client.post(
        "/api/v1/generate",
        json={
            "user_id": "demo_user_123",
            "prompt": "Design a bedroom",
            "project_id": "project_001",
            "context": {
                "style": "minimalist",
                "budget": 30000,
                "dimensions": {"length": 4.0, "width": 3.5, "height": 2.8}
            }
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "spec_json" in data


def test_generate_creates_database_record(client, auth_headers, test_db):
    """Test that generation creates proper database record"""
    response = client.post(
        "/api/v1/generate",
        json={
            "user_id": "demo_user_123",
            "prompt": "Design a kitchen",
            "project_id": "project_001"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    spec_id = response.json()["spec_id"]
    
    # Verify database record was created
    spec = test_db.query(Spec).filter(Spec.spec_id == spec_id).first()
    assert spec is not None
    assert spec.user_id == "demo_user_123"
    assert spec.prompt == "Design a kitchen"
    assert spec.project_id == "project_001"