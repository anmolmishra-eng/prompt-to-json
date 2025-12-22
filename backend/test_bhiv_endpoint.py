#!/usr/bin/env python3
"""
Test script for BHIV AI Assistant endpoint
Tests authentication, endpoint functionality, and data storage
"""

import json
import time
from datetime import datetime

import requests

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "bhiv2024"


def get_auth_token():
    """Get JWT authentication token"""
    print("Getting authentication token...")

    auth_data = {"username": USERNAME, "password": PASSWORD}

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data=auth_data,  # Form data for OAuth2
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code == 200:
        token_data = response.json()
        print(f"Authentication successful")
        return token_data["access_token"]
    else:
        print(f"Authentication failed: {response.text}")
        return None


def test_bhiv_endpoint(token):
    """Test the BHIV AI Assistant endpoint"""
    print("\n🧠 Testing BHIV AI Assistant endpoint...")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Test payload
    test_data = {
        "user_id": "admin",  # Using admin since it's authenticated
        "prompt": "Design a modern 2BHK apartment with open kitchen and balcony",
        "city": "Mumbai",
        "project_id": f"proj_test_{int(time.time())}",
        "design_type": "residential",
        "budget": 1500000,
        "area_sqft": 800,
        "notify_prefect": True,
    }

    print(f"📤 Sending request with data:")
    print(json.dumps(test_data, indent=2))

    start_time = time.time()
    response = requests.post(f"{BASE_URL}/bhiv/v1/prompt", json=test_data, headers=headers)
    end_time = time.time()

    print(f"\n⏱️  Response time: {(end_time - start_time):.2f} seconds")
    print(f"📊 Status Code: {response.status_code}")

    if response.status_code == 201:
        print("✅ BHIV endpoint test successful!")
        response_data = response.json()

        # Analyze response structure
        print("\n📋 Response Analysis:")
        print(f"  Request ID: {response_data.get('request_id', 'N/A')}")
        print(f"  Spec ID: {response_data.get('spec_id', 'N/A')}")
        print(f"  User ID: {response_data.get('user_id', 'N/A')}")
        print(f"  City: {response_data.get('city', 'N/A')}")
        print(f"  Status: {response_data.get('status', 'N/A')}")
        print(f"  Total Duration: {response_data.get('total_duration_ms', 'N/A')} ms")

        # Check agents
        agents = response_data.get("agents", {})
        print(f"\n🤖 Agents Called ({len(agents)}):")
        for agent_name, agent_data in agents.items():
            status = "✅" if agent_data.get("success") else "❌"
            duration = agent_data.get("duration_ms", 0)
            print(f"  {status} {agent_name}: {duration}ms")
            if not agent_data.get("success"):
                print(f"    Error: {agent_data.get('error', 'Unknown')}")

        # Check design spec
        design_spec = response_data.get("design_spec", {})
        if design_spec:
            print(f"\n🏗️  Design Spec Generated:")
            print(f"  Objects: {len(design_spec.get('objects', []))}")
            print(f"  Rooms: {len(design_spec.get('rooms', []))}")
            if "estimated_cost" in design_spec:
                cost = design_spec["estimated_cost"]
                print(f"  Estimated Cost: {cost.get('total', 'N/A')} {cost.get('currency', 'INR')}")

        return response_data
    else:
        print(f"❌ BHIV endpoint test failed!")
        print(f"Error: {response.text}")
        return None


def verify_data_storage(response_data):
    """Verify that data is stored properly"""
    print("\n💾 Verifying data storage...")

    if not response_data:
        print("❌ No response data to verify")
        return

    spec_id = response_data.get("spec_id")
    if spec_id:
        print(f"✅ Spec ID generated: {spec_id}")
        print(f"✅ Response indicates successful processing")

        # Check if local files were created (if any)
        import os

        local_dirs = ["data", "uploads", "logs"]
        for dir_name in local_dirs:
            if os.path.exists(dir_name):
                files = os.listdir(dir_name)
                if files:
                    print(f"✅ Local files found in {dir_name}: {len(files)} files")
    else:
        print("❌ No spec_id in response")


def main():
    """Main test function"""
    print("BHIV AI Assistant Endpoint Test")
    print("=" * 50)

    # Step 1: Authentication
    token = get_auth_token()
    if not token:
        print("Cannot proceed without authentication")
        return

    # Step 2: Test BHIV endpoint
    response_data = test_bhiv_endpoint(token)

    # Step 3: Verify data storage
    verify_data_storage(response_data)

    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    main()
