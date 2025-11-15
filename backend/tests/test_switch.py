"""
Test cases for POST /api/v1/switch endpoint
"""

import pytest
from app.models import Spec, Iteration


def test_switch_valid_material(client, auth_headers, test_db, sample_spec_data):
    """Test switching material on existing spec"""
    # First create a spec
    spec = Spec(
        spec_id="test_spec_001",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    # Now switch material
    response = client.post(
        "/api/v1/switch",
        json={
            "user_id": "demo_user_123",
            "spec_id": "test_spec_001",
            "target": {"object_id": "floor_001"},
            "update": {"material": "marble_white", "color_hex": "#FFFFFF"},
            "note": "Change to white marble"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "spec_id" in data
    assert "iteration_id" in data
    assert "updated_spec_json" in data
    assert "changed" in data
    assert "saved_at" in data
    
    # Verify change details
    change = data["changed"]
    assert change["object_id"] == "floor_001"
    assert change["field"] == "material"
    assert change["after"] == "marble_white"


def test_switch_nonexistent_spec(client, auth_headers):
    """Test switching on non-existent spec"""
    response = client.post(
        "/api/v1/switch",
        json={
            "user_id": "demo_user_123",
            "spec_id": "nonexistent_spec",
            "target": {"object_id": "floor_001"},
            "update": {"material": "marble"}
        },
        headers=auth_headers
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_switch_invalid_object_id(client, auth_headers, test_db, sample_spec_data):
    """Test switching invalid object ID"""
    # Create spec
    spec = Spec(
        spec_id="test_spec_002",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    # Try to switch non-existent object
    response = client.post(
        "/api/v1/switch",
        json={
            "user_id": "demo_user_123",
            "spec_id": "test_spec_002",
            "target": {"object_id": "invalid_object_999"},
            "update": {"material": "marble"}
        },
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


def test_switch_missing_target(client, auth_headers, test_db, sample_spec_data):
    """Test switch without target specification"""
    spec = Spec(
        spec_id="test_spec_003",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    response = client.post(
        "/api/v1/switch",
        json={
            "user_id": "demo_user_123",
            "spec_id": "test_spec_003",
            "update": {"material": "marble"}
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422


def test_switch_missing_update(client, auth_headers, test_db, sample_spec_data):
    """Test switch without update specification"""
    spec = Spec(
        spec_id="test_spec_004",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    response = client.post(
        "/api/v1/switch",
        json={
            "user_id": "demo_user_123",
            "spec_id": "test_spec_004",
            "target": {"object_id": "floor_001"}
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422


def test_switch_without_auth(client):
    """Test switch without authentication"""
    response = client.post(
        "/api/v1/switch",
        json={
            "user_id": "demo_user_123",
            "spec_id": "test_spec_001",
            "target": {"object_id": "floor_001"},
            "update": {"material": "marble"}
        }
    )
    
    assert response.status_code == 401


def test_switch_creates_iteration(client, auth_headers, test_db, sample_spec_data):
    """Test that switch creates iteration record"""
    # Create spec
    spec = Spec(
        spec_id="test_spec_005",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    # Switch material
    response = client.post(
        "/api/v1/switch",
        json={
            "user_id": "demo_user_123",
            "spec_id": "test_spec_005",
            "target": {"object_id": "sofa_001"},
            "update": {"material": "leather_brown"},
            "note": "Switch to leather"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    iteration_id = response.json()["iteration_id"]
    
    # Verify iteration was created
    iteration = test_db.query(Iteration).filter(Iteration.iter_id == iteration_id).first()
    assert iteration is not None
    assert iteration.spec_id == "test_spec_005"
    assert iteration.user_id == "demo_user_123"
    assert iteration.note == "Switch to leather"


def test_switch_multiple_properties(client, auth_headers, test_db, sample_spec_data):
    """Test switching multiple properties at once"""
    spec = Spec(
        spec_id="test_spec_006",
        user_id="demo_user_123",
        prompt="Test room",
        project_id="project_001",
        spec_json=sample_spec_data
    )
    test_db.add(spec)
    test_db.commit()
    
    response = client.post(
        "/api/v1/switch",
        json={
            "user_id": "demo_user_123",
            "spec_id": "test_spec_006",
            "target": {"object_id": "table_001"},
            "update": {
                "material": "glass",
                "color_hex": "#CCCCCC",
                "properties": {"durability": 0.6, "cost": 400}
            }
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify updated spec contains changes
    updated_spec = data["updated_spec_json"]
    table = next(obj for obj in updated_spec["objects"] if obj["id"] == "table_001")
    assert table["material"] == "glass"
    assert table["color_hex"] == "#CCCCCC"