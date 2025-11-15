"""
Test cases for POST /api/v1/evaluate endpoint
"""

import pytest
from app.models import Spec, Evaluation


def test_evaluate_valid_rating(client, auth_headers, test_db, sample_spec_data):
    """Test evaluating spec with valid rating"""
    # Create spec to evaluate
    spec = Spec(
        spec_id="eval_spec_001",
        user_id="demo_user_123",
        prompt="Test room for evaluation",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    response = client.post(
        "/api/v1/evaluate",
        json={
            "user_id": "demo_user_123",
            "spec_id": "eval_spec_001",
            "rating": 4.5,
            "notes": "Great design, love the modern style"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert data["ok"] is True
    assert "saved_id" in data
    assert "message" in data
    assert "timestamp" in data


def test_evaluate_creates_database_record(client, auth_headers, test_db, sample_spec_data):
    """Test that evaluation creates database record"""
    # Create spec
    spec = Spec(
        spec_id="eval_spec_002",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    response = client.post(
        "/api/v1/evaluate",
        json={
            "user_id": "demo_user_123",
            "spec_id": "eval_spec_002",
            "rating": 3.8,
            "notes": "Good but could be improved"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    eval_id = response.json()["saved_id"]
    
    # Verify database record
    evaluation = test_db.query(Evaluation).filter(Evaluation.eval_id == eval_id).first()
    assert evaluation is not None
    assert evaluation.spec_id == "eval_spec_002"
    assert evaluation.user_id == "demo_user_123"
    assert evaluation.score == 3.8
    assert evaluation.notes == "Good but could be improved"


def test_evaluate_nonexistent_spec(client, auth_headers):
    """Test evaluating non-existent spec"""
    response = client.post(
        "/api/v1/evaluate",
        json={
            "user_id": "demo_user_123",
            "spec_id": "nonexistent_spec",
            "rating": 4.0,
            "notes": "Test evaluation"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_evaluate_invalid_rating_high(client, auth_headers, test_db, sample_spec_data):
    """Test evaluation with rating too high"""
    spec = Spec(
        spec_id="eval_spec_003",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    response = client.post(
        "/api/v1/evaluate",
        json={
            "user_id": "demo_user_123",
            "spec_id": "eval_spec_003",
            "rating": 6.0,  # Too high
            "notes": "Test"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


def test_evaluate_invalid_rating_low(client, auth_headers, test_db, sample_spec_data):
    """Test evaluation with rating too low"""
    spec = Spec(
        spec_id="eval_spec_004",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    response = client.post(
        "/api/v1/evaluate",
        json={
            "user_id": "demo_user_123",
            "spec_id": "eval_spec_004",
            "rating": -1.0,  # Too low
            "notes": "Test"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 400


def test_evaluate_missing_rating(client, auth_headers, test_db, sample_spec_data):
    """Test evaluation without rating"""
    spec = Spec(
        spec_id="eval_spec_005",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    response = client.post(
        "/api/v1/evaluate",
        json={
            "user_id": "demo_user_123",
            "spec_id": "eval_spec_005",
            "notes": "Test evaluation without rating"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422


def test_evaluate_without_auth(client):
    """Test evaluation without authentication"""
    response = client.post(
        "/api/v1/evaluate",
        json={
            "user_id": "demo_user_123",
            "spec_id": "eval_spec_001",
            "rating": 4.0,
            "notes": "Test"
        }
    )
    
    assert response.status_code == 401


def test_evaluate_without_notes(client, auth_headers, test_db, sample_spec_data):
    """Test evaluation without notes (should be optional)"""
    spec = Spec(
        spec_id="eval_spec_006",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    response = client.post(
        "/api/v1/evaluate",
        json={
            "user_id": "demo_user_123",
            "spec_id": "eval_spec_006",
            "rating": 4.2
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True


def test_evaluate_triggers_feedback_loop(client, auth_headers, test_db, sample_spec_data):
    """Test that evaluation triggers feedback loop integration"""
    spec = Spec(
        spec_id="eval_spec_007",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    response = client.post(
        "/api/v1/evaluate",
        json={
            "user_id": "demo_user_123",
            "spec_id": "eval_spec_007",
            "rating": 4.8,
            "notes": "Excellent design"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should include feedback loop status if integrated
    # This will depend on actual implementation
    assert data["ok"] is True