#!/usr/bin/env python3
"""
Test script for /api/v1/rl/feedback endpoint
Tests RL feedback collection for training reinforcement learning models
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get JWT token for authentication"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "user", "password": "pass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Auth failed: {response.text}")

def get_valid_spec_id(token):
    """Get a valid spec_id from user history"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/history?user_id=user123", headers=headers)
    if response.status_code == 200:
        specs = response.json().get("specs", [])
        if specs:
            return specs[0]["spec_id"]
    return None

def test_rl_feedback():
    """Test RL feedback endpoint"""
    token = get_auth_token()
    spec_id = get_valid_spec_id(token)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("Testing /api/v1/rl/feedback endpoint")
    print("=" * 60)
    print(f"Using spec_id: {spec_id}")

    # Test 1: Valid RL feedback (design_a_id format)
    print("\n1. Testing valid RL feedback (design_a_id format)")
    payload = {
        "design_a_id": spec_id,
        "design_b_id": spec_id,
        "preference": "A",
        "reason": "Better layout and functionality",
        "user_id": "user123",
        "rating_a": 4
    }

    response = requests.post(f"{BASE_URL}/rl/feedback", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 2: Valid RL feedback (spec_a_id format)
    print("\n2. Testing valid RL feedback (spec_a_id format)")
    payload = {
        "spec_a_id": spec_id,
        "spec_b_id": spec_id,
        "preference": "B",
        "reason": "More cost-effective design",
        "user_id": "user123",
        "rating_a": 3
    }

    response = requests.post(f"{BASE_URL}/rl/feedback", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Missing design_b_id (should fail)
    print("\n3. Testing missing design_b_id (should fail)")
    payload = {
        "design_a_id": spec_id,
        "preference": "A",
        "reason": "Testing validation"
    }

    response = requests.post(f"{BASE_URL}/rl/feedback", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 4: Missing design_a_id (should fail)
    print("\n4. Testing missing design_a_id (should fail)")
    payload = {
        "design_b_id": spec_id,
        "preference": "B",
        "reason": "Testing validation"
    }

    response = requests.post(f"{BASE_URL}/rl/feedback", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 5: Invalid spec ID (should fail)
    print("\n5. Testing invalid spec ID (should fail)")
    payload = {
        "design_a_id": "invalid_spec_123",
        "design_b_id": spec_id,
        "preference": "A",
        "reason": "Testing invalid spec"
    }

    response = requests.post(f"{BASE_URL}/rl/feedback", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 6: Empty feedback data (should fail)
    print("\n6. Testing empty feedback data (should fail)")
    payload = {}

    response = requests.post(f"{BASE_URL}/rl/feedback", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 7: No authentication (should fail)
    print("\n7. Testing without authentication (should fail)")
    payload = {
        "design_a_id": spec_id,
        "design_b_id": spec_id,
        "preference": "A"
    }

    response = requests.post(f"{BASE_URL}/rl/feedback", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 8: Complex feedback with all fields
    print("\n8. Testing complex feedback with all fields")
    payload = {
        "design_a_id": spec_id,
        "design_b_id": spec_id,
        "preference": "A",
        "reason": "Design A has better space utilization and modern aesthetics",
        "user_id": "user123",
        "rating_a": 5,
        "rating_b": 3,
        "feedback_type": "explicit",
        "context": "Comparing residential designs for urban setting"
    }

    response = requests.post(f"{BASE_URL}/rl/feedback", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\nRL feedback endpoint tests completed!")

if __name__ == "__main__":
    test_rl_feedback()
