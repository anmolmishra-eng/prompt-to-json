"""
Pytest configuration and shared fixtures for all tests
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models import User, Spec, Iteration, Evaluation, RLHFFeedback


# Use SQLite in-memory database for tests
SQLALCHEMY_TEST_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Create test database engine"""
    engine = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    db = TestingSessionLocal()
    
    # Seed with demo user
    demo_user = User(
        user_id="demo_user_123",
        username="demo",
        email="demo@test.com",
        password_hash="hashed_demo123"
    )
    db.add(demo_user)
    db.commit()
    
    yield db
    db.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with overridden database dependency"""
    def override_get_db():
        return test_db
    
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_token(client):
    """Get JWT token for authenticated requests"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "demo", "password": "demo123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """Headers with JWT token for authenticated requests"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="function")
def sample_spec_data():
    """Sample spec data for testing"""
    return {
        "version": "1.0",
        "objects": [
            {
                "id": "floor_001",
                "type": "floor",
                "material": "wood_oak",
                "color_hex": "#8B4513",
                "dimensions": {"width": 5.0, "length": 7.0},
                "properties": {"durability": 0.8, "cost": 100}
            },
            {
                "id": "sofa_001",
                "type": "furniture",
                "material": "fabric",
                "color_hex": "#808080",
                "dimensions": {"width": 2.5, "depth": 1.0, "height": 0.8},
                "properties": {"comfort": 0.9, "cost": 500}
            },
            {
                "id": "table_001",
                "type": "furniture",
                "material": "wood_walnut",
                "color_hex": "#3E2723",
                "dimensions": {"width": 1.5, "length": 1.0, "height": 0.45},
                "properties": {"durability": 0.7, "cost": 300}
            }
        ],
        "style": "modern",
        "budget": 50000
    }