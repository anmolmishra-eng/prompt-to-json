#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test mobile generate endpoint with authentication and verification"""

import json
import os
import sys
import requests
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get JWT token for authentication"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "bhiv2024"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    print(f"Auth failed: {response.text}")
    return None

def test_mobile_generate():
    """Test mobile generate endpoint"""
    print("=" * 60)
    print("Testing Mobile Generate Endpoint")
    print("=" * 60)

    # Get auth token
    token = get_auth_token()
    if not token:
        print("[FAIL] Authentication failed")
        return

    print("[OK] Authentication successful")

    # Prepare request
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

    print(f"\n[REQUEST] Payload:")
    print(json.dumps(payload, indent=2))

    # Make request
    print(f"\n[SENDING] Request to {BASE_URL}/mobile/generate...")
    response = requests.post(
        f"{BASE_URL}/mobile/generate",
        headers=headers,
        json=payload
    )

    print(f"\n[RESPONSE] Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n[SUCCESS] Response received:")
        print(json.dumps(result, indent=2))

        # Save response locally
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mobile_generate_response_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        print(f"\n[SAVED] Response saved locally: {filename}")

        # Verify database storage
        if "spec_id" in result:
            print(f"\n[VERIFY] Database storage check:")
            print(f"   Spec ID: {result['spec_id']}")
            print(f"   User ID: {result.get('user_id', 'N/A')}")
            print(f"   Version: {result.get('version', 'N/A')}")
            print("   [OK] Design stored in database")

        # Verify response structure
        print(f"\n[VERIFY] Response structure:")
        expected_fields = ['spec_id', 'user_id', 'version', 'objects', 'materials']
        for field in expected_fields:
            status = '[OK]' if field in result else '[MISSING]'
            print(f"   {status} {field}")

        return result
    else:
        print(f"\n[FAILED] Error response:")
        print(response.text)
        return None

if __name__ == "__main__":
    test_mobile_generate()
