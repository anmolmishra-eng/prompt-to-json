#!/usr/bin/env python3
"""
Test script for /api/v1/rl/feedback/city endpoint
Tests city-specific RL feedback collection with multi-city integration
"""

import requests
import json
import os

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

def test_city_rl_feedback():
    """Test city RL feedback endpoint"""
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("Testing /api/v1/rl/feedback/city endpoint")
    print("=" * 60)

    # Test 1: Valid Mumbai feedback
    print("\n1. Testing valid Mumbai RL feedback")
    params = "?city=Mumbai&user_rating=4.5"
    payload = {
        "design_spec": {
            "city": "Mumbai",
            "building_type": "residential",
            "floors": 5,
            "plot_area": 1000,
            "built_area": 800,
            "building_height": 60,
            "location": "urban"
        },
        "compliance_result": {
            "status": "PASSED",
            "confidence_score": 0.85,
            "rules_applied": ["MUM-FSI-URBAN", "MUM-HEIGHT-LIMIT"],
            "violations": []
        }
    }

    response = requests.post(f"{BASE_URL}/rl/feedback/city{params}", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")

    # Test 2: Valid Pune feedback
    print("\n2. Testing valid Pune RL feedback")
    params = "?city=Pune&user_rating=3.8"
    payload = {
        "design_spec": {
            "city": "Pune",
            "building_type": "commercial",
            "floors": 8,
            "water_harvesting": True,
            "green_roof": True
        },
        "compliance_result": {
            "status": "PASSED",
            "confidence_score": 0.92,
            "rules_applied": ["PUNE-PMC", "PUNE-WATER-HARVEST"]
        }
    }

    response = requests.post(f"{BASE_URL}/rl/feedback/city{params}", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Valid Ahmedabad feedback
    print("\n3. Testing valid Ahmedabad RL feedback")
    params = "?city=Ahmedabad&user_rating=4.2"
    payload = {
        "design_spec": {
            "city": "Ahmedabad",
            "building_type": "mixed_use",
            "earthquake_resistant": True,
            "reflective_surfaces": True
        },
        "compliance_result": {
            "status": "PASSED",
            "confidence_score": 0.78,
            "rules_applied": ["AMD-EARTHQUAKE", "AMD-HEAT-ISLAND"]
        }
    }

    response = requests.post(f"{BASE_URL}/rl/feedback/city{params}", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 4: Missing city parameter (should fail)
    print("\n4. Testing missing city parameter (should fail)")
    params = "?user_rating=4.0"
    payload = {"design_spec": {"city": "Delhi"}}

    response = requests.post(f"{BASE_URL}/rl/feedback/city{params}", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 5: Missing user_rating parameter (should fail)
    print("\n5. Testing missing user_rating parameter (should fail)")
    params = "?city=Mumbai"
    payload = {"design_spec": {"city": "Mumbai"}}

    response = requests.post(f"{BASE_URL}/rl/feedback/city{params}", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 6: No authentication (should fail)
    print("\n6. Testing without authentication (should fail)")
    params = "?city=Mumbai&user_rating=4.0"
    payload = {"design_spec": {"city": "Mumbai"}}

    response = requests.post(f"{BASE_URL}/rl/feedback/city{params}", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 7: Edge case - very high rating
    print("\n7. Testing edge case - very high rating")
    params = "?city=Nashik&user_rating=5.0"
    payload = {
        "design_spec": {
            "city": "Nashik",
            "building_type": "tourism",
            "eco_friendly": True
        },
        "compliance_result": {
            "status": "PASSED",
            "confidence_score": 0.95
        }
    }

    response = requests.post(f"{BASE_URL}/rl/feedback/city{params}", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 8: Edge case - very low rating
    print("\n8. Testing edge case - very low rating")
    params = "?city=Bangalore&user_rating=1.0"
    payload = {
        "design_spec": {
            "city": "Bangalore",
            "building_type": "residential",
            "issues": ["poor_ventilation", "code_violations"]
        },
        "compliance_result": {
            "status": "FAILED",
            "confidence_score": 0.25,
            "violations": ["height_violation", "setback_violation"]
        }
    }

    response = requests.post(f"{BASE_URL}/rl/feedback/city{params}", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\nCity RL feedback endpoint tests completed!")

    # Check if feedback files were created
    print("\n" + "="*60)
    print("FEEDBACK STORAGE VERIFICATION")
    print("="*60)

    feedback_dir = "backend/data/rl_feedback"
    if os.path.exists(feedback_dir):
        files = os.listdir(feedback_dir)
        print(f"Feedback files created: {len(files)}")
        for file in files:
            if file.endswith('_feedback.jsonl'):
                city = file.replace('_feedback.jsonl', '').title()
                file_path = os.path.join(feedback_dir, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                print(f"  - {city}: {len(lines)} feedback entries")
    else:
        print("Feedback directory not found")

if __name__ == "__main__":
    test_city_rl_feedback()
