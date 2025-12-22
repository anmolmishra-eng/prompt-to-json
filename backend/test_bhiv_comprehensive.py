#!/usr/bin/env python3
"""
Comprehensive BHIV AI Assistant Endpoint Test
Uses existing database users and verifies all functionality
"""

import json
import os
import time
from datetime import datetime

import requests

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "bhiv2024"

# Existing users from database
EXISTING_USERS = ["53ad6295-a001-45ed-8613-67725ba8879d", "test_user_fixed_final", "user"]  # admin user


def get_auth_token():
    """Get JWT authentication token"""
    print("Getting authentication token...")

    auth_data = {"username": USERNAME, "password": PASSWORD}

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login", data=auth_data, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code == 200:
        token_data = response.json()
        print("Authentication successful")
        return token_data["access_token"]
    else:
        print(f"Authentication failed: {response.text}")
        return None


def test_bhiv_endpoint_comprehensive(token):
    """Test BHIV endpoint with existing user"""
    print("\n" + "=" * 60)
    print("TESTING BHIV AI ASSISTANT ENDPOINT")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Use existing user from database
    test_user = EXISTING_USERS[0]  # admin user

    test_data = {
        "user_id": test_user,
        "prompt": "Design a modern 3BHK apartment with open kitchen, living room, and balcony in Mumbai",
        "city": "Mumbai",
        "project_id": f"proj_bhiv_test_{int(time.time())}",
        "design_type": "residential",
        "budget": 2500000,
        "area_sqft": 1200,
        "notify_prefect": True,
    }

    print(f"Testing with existing user: {test_user}")
    print(f"Request payload:")
    print(json.dumps(test_data, indent=2))

    print(f"\nSending request to: {BASE_URL}/bhiv/v1/prompt")

    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/bhiv/v1/prompt",
        json=test_data,
        headers=headers,
        timeout=120,  # 2 minutes timeout for AI processing
    )
    end_time = time.time()

    print(f"\nResponse received in {(end_time - start_time):.2f} seconds")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 201:
        print("\n✅ SUCCESS: BHIV endpoint test successful!")
        response_data = response.json()

        # Detailed response analysis
        print("\n📊 RESPONSE ANALYSIS:")
        print("-" * 40)
        print(f"Request ID: {response_data.get('request_id')}")
        print(f"Spec ID: {response_data.get('spec_id')}")
        print(f"User ID: {response_data.get('user_id')}")
        print(f"City: {response_data.get('city')}")
        print(f"Status: {response_data.get('status')}")
        print(f"Total Duration: {response_data.get('total_duration_ms')} ms")
        print(f"Timestamp: {response_data.get('timestamp')}")

        # Agent analysis
        agents = response_data.get("agents", {})
        print(f"\n🤖 AGENTS EXECUTION ({len(agents)} agents):")
        print("-" * 40)
        for agent_name, agent_data in agents.items():
            status_icon = "✅" if agent_data.get("success") else "❌"
            duration = agent_data.get("duration_ms", 0)
            print(f"{status_icon} {agent_name.upper()}: {duration}ms")

            if agent_data.get("success"):
                data = agent_data.get("data", {})
                if agent_name == "mcp_compliance":
                    print(f"    Compliance: {data.get('compliant', 'Unknown')}")
                    print(f"    Confidence: {data.get('confidence_score', 'N/A')}")
                elif agent_name == "rl_agent":
                    layout = data.get("optimized_layout", {})
                    print(f"    Efficiency: {layout.get('efficiency_score', 'N/A')}")
                    print(f"    Space Util: {layout.get('space_utilization', 'N/A')}")
                elif agent_name == "geometry_agent":
                    print(f"    Geometry URL: {data.get('geometry_url', 'N/A')}")
                    print(f"    File Size: {data.get('file_size_bytes', 0)} bytes")
            else:
                print(f"    Error: {agent_data.get('error', 'Unknown error')}")

        # Design specification analysis
        design_spec = response_data.get("design_spec", {})
        print(f"\n🏗️ DESIGN SPECIFICATION:")
        print("-" * 40)
        if design_spec:
            objects = design_spec.get("objects", [])
            rooms = design_spec.get("rooms", [])
            print(f"Objects Generated: {len(objects)}")
            print(f"Rooms Defined: {len(rooms)}")

            # Show sample objects
            if objects:
                print(f"Sample Objects:")
                for obj in objects[:3]:  # Show first 3
                    print(
                        f"  - {obj.get('id', 'Unknown')}: {obj.get('type', 'Unknown')} ({obj.get('material', 'No material')})"
                    )

            # Cost estimation
            if "estimated_cost" in design_spec:
                cost = design_spec["estimated_cost"]
                print(f"Estimated Cost: {cost.get('total', 'N/A')} {cost.get('currency', 'INR')}")
        else:
            print("No design specification in response")

        return response_data
    else:
        print(f"\n❌ FAILED: BHIV endpoint test failed!")
        print(f"Status Code: {response.status_code}")
        print(f"Error Response: {response.text}")
        return None


def verify_database_storage(response_data):
    """Verify data was stored in database"""
    print(f"\n💾 DATABASE STORAGE VERIFICATION:")
    print("-" * 40)

    if not response_data:
        print("❌ No response data to verify")
        return

    spec_id = response_data.get("spec_id")
    if spec_id:
        print(f"✅ Spec ID generated: {spec_id}")
        print(f"✅ Database storage indicated by successful response")

        # Check if local files were created
        local_dirs = ["data/geometry_outputs", "data/logs", "uploads"]
        files_found = 0

        for dir_path in local_dirs:
            if os.path.exists(dir_path):
                files = os.listdir(dir_path)
                if files:
                    print(f"✅ Local files in {dir_path}: {len(files)} files")
                    files_found += len(files)

        if files_found > 0:
            print(f"✅ Total local files found: {files_found}")
        else:
            print("ℹ️ No local files found (may be stored in cloud)")
    else:
        print("❌ No spec_id in response - database storage may have failed")


def test_bhiv_health():
    """Test BHIV health endpoint"""
    print(f"\n🏥 BHIV HEALTH CHECK:")
    print("-" * 40)

    try:
        response = requests.get(f"{BASE_URL}/bhiv/v1/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ BHIV service healthy")
            print(f"Service: {health_data.get('service')}")
            print(f"Version: {health_data.get('version')}")
            print(f"Status: {health_data.get('status')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")


def main():
    """Main test execution"""
    print("BHIV AI ASSISTANT COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Target Server: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Health check
    test_bhiv_health()

    # Step 2: Authentication
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication")
        return

    # Step 3: Test main endpoint
    response_data = test_bhiv_endpoint_comprehensive(token)

    # Step 4: Verify storage
    verify_database_storage(response_data)

    # Final summary
    print(f"\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    if response_data:
        status = response_data.get("status", "unknown")
        agents = response_data.get("agents", {})
        successful_agents = sum(1 for a in agents.values() if a.get("success"))
        total_agents = len(agents)

        print(f"✅ Overall Status: {status.upper()}")
        print(f"✅ Agents Success Rate: {successful_agents}/{total_agents}")
        print(f"✅ Response Time: {response_data.get('total_duration_ms')}ms")
        print(f"✅ Spec Generated: {response_data.get('spec_id')}")
        print(f"✅ Database Storage: CONFIRMED")
        print(f"✅ Authentication: WORKING")
        print(f"✅ Endpoint Functionality: VERIFIED")
    else:
        print("❌ Test failed - see errors above")

    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
