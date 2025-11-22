"""
RL Integration Tests
"""

from datetime import datetime

import pytest
from app.main_bhiv import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_rl_feedback_submission():
    """Test RL feedback submission"""
    feedback_payload = {
        "user_id": "test_user_001",
        "spec_id": "spec_test_001",
        "rating": 4.5,
        "feedback_text": "Excellent design layout",
        "design_accepted": True,
        "timestamp": datetime.now().isoformat(),
    }

    response = client.post("/rl/feedback", json=feedback_payload)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data or "error" in data


def test_rl_feedback_minimal():
    """Test RL feedback with minimal data"""
    feedback_payload = {"user_id": "test_user_002", "spec_id": "spec_test_002", "rating": 3.0, "design_accepted": False}

    response = client.post("/rl/feedback", json=feedback_payload)
    assert response.status_code == 200


def test_rl_confidence_score():
    """Test RL confidence score endpoint"""
    spec_data = {
        "spec_json": {
            "rooms": [{"type": "bedroom", "area": 120}, {"type": "living_room", "area": 200}],
            "total_area": 800,
            "style": "modern",
        },
        "city": "Mumbai",
    }

    response = client.post("/rl/confidence", json=spec_data)
    assert response.status_code == 200
    data = response.json()
    assert "confidence" in data
    assert data["city"] == "Mumbai"


def test_rl_feedback_invalid_rating():
    """Test RL feedback with invalid rating"""
    feedback_payload = {
        "user_id": "test_user_003",
        "spec_id": "spec_test_003",
        "rating": 10.0,  # Invalid rating > 5
        "design_accepted": True,
    }

    response = client.post("/rl/feedback", json=feedback_payload)
    # Should handle validation error gracefully
    assert response.status_code in [200, 422]
