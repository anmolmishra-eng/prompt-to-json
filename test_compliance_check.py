#!/usr/bin/env python3
"""
Test script for /api/v1/compliance/check endpoint
Tests compliance checking with real Supabase storage integration
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

def test_compliance_check():
    """Test compliance check endpoint"""
    token = get_auth_token()
    spec_id = get_valid_spec_id(token)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("Testing /api/v1/compliance/check endpoint")
    print("=" * 60)
    print(f"Using spec_id: {spec_id}")

    # Test 1: Valid compliance check
    print("\n1. Testing valid compliance check (IBC + ADA)")
    payload = {
        "spec_id": spec_id,
        "regulations": ["IBC", "ADA"],
        "location": "California"
    }

    response = requests.post(f"{BASE_URL}/compliance/check", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")

    # Verify compliance URL is real Supabase URL
    if "compliance_url" in result:
        url = result["compliance_url"]
        print(f"Compliance URL: {url[:80]}...")
        print(f"Is Supabase URL: {'supabase.co' in url}")

    # Test 2: Different regulations
    print("\n2. Testing different regulations (OSHA + CE_MARKING)")
    payload = {
        "spec_id": spec_id,
        "regulations": ["OSHA", "CE_MARKING"],
        "location": "New York"
    }

    response = requests.post(f"{BASE_URL}/compliance/check", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Missing spec_id (should fail)
    print("\n3. Testing missing spec_id (should fail)")
    payload = {
        "regulations": ["ISO_9001"],
        "location": "Texas"
    }

    response = requests.post(f"{BASE_URL}/compliance/check", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 4: Invalid spec_id (should fail)
    print("\n4. Testing invalid spec_id (should fail)")
    payload = {
        "spec_id": "invalid_spec_123",
        "regulations": ["IBC"],
        "location": "Florida"
    }

    response = requests.post(f"{BASE_URL}/compliance/check", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 5: No authentication (should fail)
    print("\n5. Testing without authentication (should fail)")
    payload = {
        "spec_id": spec_id,
        "regulations": ["IBC"],
        "location": "Nevada"
    }

    response = requests.post(f"{BASE_URL}/compliance/check", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\nCompliance check endpoint tests completed!")

if __name__ == "__main__":
    test_compliance_check()
