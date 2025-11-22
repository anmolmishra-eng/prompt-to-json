"""
E2E test configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client for BHIV app"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock auth headers for testing"""
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def sample_cities():
    """Sample city data for testing"""
    return ["Mumbai", "Pune", "Ahmedabad", "Nashik"]


@pytest.fixture
def sample_prompts():
    """Sample design prompts for testing"""
    return {
        "Mumbai": "Design a 4-floor residential building with parking",
        "Pune": "Create an IT office park with 3 buildings",
        "Ahmedabad": "Design a textile mill redevelopment project",
        "Nashik": "Create a wine tourism facility with tasting rooms"
    }