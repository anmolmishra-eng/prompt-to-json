#!/usr/bin/env python3
"""
Test script for /api/v1/compliance/ingest_pdf endpoint
Tests PDF ingestion with Prefect workflow integration
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

def test_ingest_pdf():
    """Test PDF ingestion endpoint"""
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("Testing /api/v1/compliance/ingest_pdf endpoint")
    print("=" * 60)

    # Test 1: Valid PDF ingestion
    print("\n1. Testing valid PDF ingestion (Mumbai)")
    payload = {
        "pdf_url": "https://example.com/mumbai_dcr.pdf",
        "city": "Mumbai"
    }

    response = requests.post(f"{BASE_URL}/compliance/ingest_pdf", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 2: Different city
    print("\n2. Testing PDF ingestion (Pune)")
    payload = {
        "pdf_url": "https://example.com/pune_dcr.pdf",
        "city": "Pune"
    }

    response = requests.post(f"{BASE_URL}/compliance/ingest_pdf", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Missing pdf_url (should fail)
    print("\n3. Testing missing pdf_url (should fail)")
    payload = {"city": "Mumbai"}

    response = requests.post(f"{BASE_URL}/compliance/ingest_pdf", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 4: Default city (no city specified)
    print("\n4. Testing default city (no city specified)")
    payload = {"pdf_url": "https://example.com/default_dcr.pdf"}

    response = requests.post(f"{BASE_URL}/compliance/ingest_pdf", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 5: Check workflow status
    print("\n5. Testing workflow status")
    response = requests.get(f"{BASE_URL}/compliance/workflow_status", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\nPDF ingestion endpoint tests completed!")

if __name__ == "__main__":
    test_ingest_pdf()
