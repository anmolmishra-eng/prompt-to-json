"""
Test cases for POST /api/v1/iterate endpoint
"""

import pytest


def test_iterate_with_strategy(client, auth_headers):
    """Test iterating a spec with improvement strategy"""
    # 1. Generate spec
    gen_response = client.post(
        "/api/v1/generate",
        json={
            "user_id": "demo_user_123",
            "prompt": "modern living room with wooden floor",
            "project_id": "project_001",
        },
        headers=auth_headers,
    )
    assert gen_response.status_code == 200
    spec_id = gen_response.json()["spec_id"]

    # 2. Iterate with strategy
    iterate_response = client.post(
        "/api/v1/iterate",
        json={"user_id": "demo_user_123", "spec_id": spec_id, "strategy": "improve_materials"},
        headers=auth_headers,
    )

    assert iterate_response.status_code == 200
    result = iterate_response.json()

    # 3. Verify response structure
    assert "before" in result
    assert "after" in result
    assert "feedback" in result
    assert "iteration_id" in result


def test_iterate_invalid_strategy(client, auth_headers):
    """Test error for invalid strategy"""
    gen_response = client.post(
        "/api/v1/generate",
        json={"user_id": "demo_user_123", "prompt": "living room", "project_id": "project_001"},
        headers=auth_headers,
    )
    assert gen_response.status_code == 200
    spec_id = gen_response.json()["spec_id"]

    response = client.post(
        "/api/v1/iterate",
        json={"user_id": "demo_user_123", "spec_id": spec_id, "strategy": "invalid_strategy_xyz"},
        headers=auth_headers,
    )

    assert response.status_code == 400


def test_iterate_spec_not_found(client, auth_headers):
    """Test error when spec doesn't exist"""
    response = client.post(
        "/api/v1/iterate",
        json={"user_id": "demo_user_123", "spec_id": "nonexistent_spec", "strategy": "improve_materials"},
        headers=auth_headers,
    )

    assert response.status_code == 404
