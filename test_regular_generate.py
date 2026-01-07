#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test regular generate endpoint to isolate mobile issue"""

import json
import sys
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"

# Get token
print("Authenticating...")
auth_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "bhiv2024"}
)

if auth_response.status_code != 200:
    print(f"Auth failed: {auth_response.text}")
    exit(1)

token = auth_response.json()["access_token"]
print("Auth successful\n")

# Test regular generate endpoint
print("Testing /api/v1/generate...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "user_id": "test_user_123",
    "prompt": "Create a modern kitchen with island",
    "project_id": "proj_test_001"
}

print(f"Payload: {json.dumps(payload, indent=2)}\n")

response = requests.post(
    f"{BASE_URL}/generate",
    headers=headers,
    json=payload,
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
