#!/usr/bin/env python3
"""
Test Consolidated BHIV System
Tests all BHIV endpoints on the main server (port 8000)
"""

import asyncio
import json
from datetime import datetime

import httpx


async def test_consolidated_bhiv():
    """Test all BHIV endpoints on main server"""
    print("🧪 Testing Consolidated BHIV System")
    print("=" * 50)

    base_url = "http://localhost:8000"

    # Test data
    test_request = {
        "user_id": "test_user_consolidated",
        "prompt": "Design a modern 2BHK apartment in Mumbai with balcony",
        "city": "Mumbai",
        "project_id": "test_project_001",
        "budget": 75000,
        "area_sqft": 800
    }

    async with httpx.AsyncClient(timeout=60.0) as client:

        # Test 1: Main orchestration endpoint
        print("\n🔍 Test 1: BHIV Orchestration (/bhiv/v1/prompt)")
        try:
            response = await client.post(f"{base_url}/bhiv/v1/prompt", json=test_request)
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Orchestration: SUCCESS")
                print(f"   Request ID: {result.get('request_id')}")
                print(f"   Spec ID: {result.get('spec_id')}")
                print(f"   Status: {result.get('status')}")
                print(f"   Agents: {list(result.get('agents', {}).keys())}")
            else:
                print(f"❌ Orchestration: FAILED ({response.status_code})")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Orchestration: ERROR - {e}")

        # Test 2: Integrated design endpoint
        print("\n🔍 Test 2: BHIV Integrated Design (/bhiv/v1/design)")
        try:
            design_request = {
                "user_id": test_request["user_id"],
                "prompt": test_request["prompt"],
                "city": test_request["city"],
                "project_id": test_request["project_id"],
                "context": {"style": "modern", "dimensions": {"length": 30, "width": 25}}
            }
            response = await client.post(f"{base_url}/bhiv/v1/design", json=design_request)
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Integrated Design: SUCCESS")
                print(f"   Request ID: {result.get('request_id')}")
                print(f"   Spec ID: {result.get('spec_id')}")
                print(f"   Processing Time: {result.get('processing_time_ms')}ms")
                print(f"   Compliance: {result.get('compliance', {}).get('compliant')}")
                print(f"   RL Optimization: {'Yes' if result.get('rl_optimization') else 'No'}")
            else:
                print(f"❌ Integrated Design: FAILED ({response.status_code})")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Integrated Design: ERROR - {e}")

        # Test 3: BHIV Health Check
        print("\n🔍 Test 3: BHIV Health Check (/bhiv/v1/health)")
        try:
            response = await client.get(f"{base_url}/bhiv/v1/health")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Health Check: SUCCESS")
                print(f"   Status: {result.get('status')}")
                print(f"   Service: {result.get('service')}")
                if 'external_services' in result:
                    print(f"   External Services: {list(result['external_services'].keys())}")
            else:
                print(f"❌ Health Check: FAILED ({response.status_code})")
        except Exception as e:
            print(f"❌ Health Check: ERROR - {e}")

        # Test 4: BHIV Feedback
        print("\n🔍 Test 4: BHIV Feedback (/bhiv/v1/feedback)")
        try:
            feedback_request = {
                "request_id": "test_req_123",
                "spec_id": "test_spec_456",
                "user_id": test_request["user_id"],
                "rating": 4.5,
                "feedback_type": "explicit",
                "notes": "Great design with excellent space utilization",
                "aspect_ratings": {
                    "aesthetics": 4.8,
                    "functionality": 4.2,
                    "cost_effectiveness": 4.0
                }
            }
            response = await client.post(f"{base_url}/bhiv/v1/feedback", json=feedback_request)
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Feedback: SUCCESS")
                print(f"   Status: {result.get('status')}")
                print(f"   Feedback ID: {result.get('feedback_id')}")
                print(f"   Queued for Training: {result.get('queued_for_training')}")
            else:
                print(f"❌ Feedback: FAILED ({response.status_code})")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Feedback: ERROR - {e}")

    print("\n" + "=" * 50)
    print("🎯 CONSOLIDATED BHIV TEST COMPLETE")
    print("All BHIV functionality is now available on port 8000!")
    print("No need for separate BHIV server on port 8003.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_consolidated_bhiv())
