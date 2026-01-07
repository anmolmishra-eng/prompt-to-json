#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Mobile Generate Endpoint Test
Tests API response, local storage, and database persistence
"""

import json
import sys
import requests
from datetime import datetime
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def get_auth_token():
    """Get JWT token for authentication"""
    print("[1/5] Authenticating...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "bhiv2024"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"   [OK] Authentication successful")
        return token
    print(f"   [FAIL] Authentication failed: {response.text}")
    return None

def test_mobile_generate(token):
    """Test mobile generate endpoint"""
    print("\n[2/5] Testing Mobile Generate Endpoint...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "user_id": "mobile_test_user",
        "prompt": "Create a modern living room with minimalist furniture and natural lighting",
        "project_id": "proj_mobile_001",
        "context": {
            "device": "android",
            "app_version": "1.0.0",
            "screen_size": "1080x2400"
        }
    }

    print(f"   Request: POST {BASE_URL}/mobile/generate")
    print(f"   Payload: {json.dumps(payload, indent=6)}")

    try:
        response = requests.post(
            f"{BASE_URL}/mobile/generate",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n   Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"   [OK] Design generated successfully")
            return result
        else:
            print(f"   [FAIL] Error: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print(f"   [FAIL] Request timed out after 30 seconds")
        return None
    except Exception as e:
        print(f"   [FAIL] Request failed: {e}")
        return None

def save_response_locally(result):
    """Save response to local file"""
    print("\n[3/5] Saving Response Locally...")

    if not result:
        print(f"   [SKIP] No response to save")
        return None

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mobile_generate_response_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        file_size = os.path.getsize(filename)
        print(f"   [OK] Saved to: {filename}")
        print(f"   [OK] File size: {file_size} bytes")
        return filename

    except Exception as e:
        print(f"   [FAIL] Failed to save: {e}")
        return None

def verify_response_structure(result):
    """Verify response has all expected fields"""
    print("\n[4/5] Verifying Response Structure...")

    if not result:
        print(f"   [SKIP] No response to verify")
        return False

    expected_fields = {
        'spec_id': str,
        'user_id': str,
        'spec_json': dict,
        'preview_url': str,
        'estimated_cost': (int, float),
        'spec_version': int,
        'created_at': str
    }

    all_valid = True
    for field, expected_type in expected_fields.items():
        if field in result:
            value = result[field]
            if isinstance(value, expected_type):
                print(f"   [OK] {field}: {type(value).__name__}")
            else:
                print(f"   [WARN] {field}: Expected {expected_type}, got {type(value).__name__}")
                all_valid = False
        else:
            print(f"   [MISSING] {field}")
            all_valid = False

    # Check spec_json structure
    if 'spec_json' in result:
        spec_json = result['spec_json']
        spec_fields = ['design_type', 'objects', 'materials', 'dimensions']
        print(f"\n   Checking spec_json structure:")
        for field in spec_fields:
            status = '[OK]' if field in spec_json else '[MISSING]'
            print(f"      {status} {field}")

    return all_valid

def verify_database_storage(result, token):
    """Verify design was saved to database"""
    print("\n[5/5] Verifying Database Storage...")

    if not result or 'spec_id' not in result:
        print(f"   [SKIP] No spec_id to verify")
        return False

    spec_id = result['spec_id']
    print(f"   Checking spec_id: {spec_id}")

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/specs/{spec_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            db_result = response.json()
            print(f"   [OK] Design found in database")
            print(f"   [OK] Spec ID: {db_result.get('spec_id')}")
            print(f"   [OK] User ID: {db_result.get('user_id')}")
            print(f"   [OK] Version: {db_result.get('spec_version')}")
            print(f"   [OK] Cost: ₹{db_result.get('estimated_cost', 0):,.0f}")
            return True
        else:
            print(f"   [FAIL] Design not found in database: {response.status_code}")
            return False

    except Exception as e:
        print(f"   [FAIL] Database verification failed: {e}")
        return False

def print_summary(result, filename, structure_valid, db_valid):
    """Print test summary"""
    print_section("TEST SUMMARY")

    tests = [
        ("Authentication", result is not None or filename is not None),
        ("API Response", result is not None),
        ("Local Storage", filename is not None),
        ("Response Structure", structure_valid),
        ("Database Storage", db_valid)
    ]

    passed = sum(1 for _, status in tests if status)
    total = len(tests)

    for test_name, status in tests:
        status_str = "[PASS]" if status else "[FAIL]"
        print(f"   {status_str} {test_name}")

    print(f"\n   Results: {passed}/{total} tests passed")

    if result and 'spec_id' in result:
        print(f"\n   Generated Design:")
        print(f"      Spec ID: {result['spec_id']}")
        print(f"      User ID: {result.get('user_id')}")
        print(f"      Cost: ₹{result.get('estimated_cost', 0):,.0f}")
        print(f"      Preview: {result.get('preview_url', 'N/A')}")

    if filename:
        print(f"\n   Local File: {filename}")

    print(f"\n{'='*60}\n")

def main():
    """Main test execution"""
    print_section("MOBILE GENERATE ENDPOINT TEST")

    # Step 1: Authenticate
    token = get_auth_token()
    if not token:
        print("\n[ABORT] Cannot proceed without authentication\n")
        return

    # Step 2: Test mobile generate
    result = test_mobile_generate(token)

    # Step 3: Save locally
    filename = save_response_locally(result)

    # Step 4: Verify structure
    structure_valid = verify_response_structure(result)

    # Step 5: Verify database
    db_valid = verify_database_storage(result, token)

    # Print summary
    print_summary(result, filename, structure_valid, db_valid)

if __name__ == "__main__":
    main()
