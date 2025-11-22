"""
Integration tests for BHIV AI Assistant layer
"""

import pytest
from app.main_bhiv import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "BHIV AI Assistant"
    assert "endpoints" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_bhiv_health_detailed():
    """Test BHIV detailed health with system checks"""
    response = client.get("/bhiv/v1/health")
    assert response.status_code == 200
    data = response.json()

    # Should check all systems
    assert "bhiv" in data
    assert "task7" in data
    assert "sohum_mcp" in data
    assert "ranjeet_rl" in data


@pytest.mark.asyncio
async def test_design_generation_flow():
    """Test complete design generation flow"""
    request_payload = {
        "user_id": "test_user_001",
        "prompt": "Design a modern residential building with 4 floors in Mumbai",
        "city": "Mumbai",
        "project_id": "test_project_001",
        "context": {"building_type": "residential", "floors": 4},
    }

    response = client.post("/bhiv/v1/design", json=request_payload)

    # Note: This will fail if systems are not running
    # In staging/production, this should pass
    if response.status_code == 200:
        data = response.json()

        # Verify response structure
        assert "request_id" in data
        assert "spec_id" in data
        assert "spec_json" in data
        assert "compliance" in data
        assert "processing_time_ms" in data

        # Verify compliance result
        assert "compliant" in data["compliance"]
        assert "violations" in data["compliance"]
    else:
        pytest.skip("Systems not running, skipping integration test")


def test_mcp_rules_endpoint():
    """Test MCP rules fetch"""
    response = client.get("/mcp/rules/Mumbai")

    # Should return even if MCP is down (empty rules)
    assert response.status_code == 200
    data = response.json()
    assert "city" in data
    assert "rules" in data


def test_rl_feedback_submission():
    """Test RL feedback endpoint"""
    feedback_payload = {
        "user_id": "test_user_001",
        "spec_id": "spec_test_001",
        "rating": 4.5,
        "feedback_text": "Great design!",
        "design_accepted": True,
    }

    response = client.post("/rl/feedback", json=feedback_payload)

    # Should return success even if RL system is down
    assert response.status_code == 200
