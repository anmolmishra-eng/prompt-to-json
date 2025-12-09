#!/usr/bin/env python3
"""
Test BHIV AI Assistant API Endpoints
"""

import asyncio
import json
import httpx


async def test_bhiv_api_endpoints():
    """Test all BHIV API endpoints"""
    print("Testing BHIV AI Assistant API Endpoints")
    print("=" * 50)

    base_url = "http://localhost:8000"  # Main server

    async with httpx.AsyncClient(timeout=30.0) as client:

        # Test 1: Get MCP Rules
        print("\n1. Testing GET /bhiv/v1/health")
        try:
            response = await client.get(f"{base_url}/bhiv/v1/health")
            if response.status_code == 200:
                print("✅ BHIV Health: OK")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ BHIV Health: {response.status_code}")
        except Exception as e:
            print(f"❌ BHIV Health: {e}")

        # Test 2: Submit RL Prompt
        print("\n2. Testing POST /bhiv/v1/prompt")
        try:
            prompt_data = {
                "user_id": "test_user",
                "prompt": "Optimize land use for Mumbai residential area",
                "city": "Mumbai",
                "budget": 50000
            }
            response = await client.post(f"{base_url}/bhiv/v1/prompt", json=prompt_data)
            if response.status_code in [200, 201]:
                result = response.json()
                print("✅ BHIV Prompt: OK")
                print(f"   Request ID: {result.get('request_id')}")
                print(f"   Status: {result.get('status')}")
            else:
                print(f"❌ BHIV Prompt: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ BHIV Prompt: {e}")

        # Test 3: Submit Feedback
        print("\n3. Testing POST /bhiv/v1/feedback")
        try:
            feedback_data = {
                "request_id": "test_req_123",
                "spec_id": "test_spec_456",
                "user_id": "test_user",
                "rating": 4.5,
                "notes": "Great optimization results"
            }
            response = await client.post(f"{base_url}/bhiv/v1/feedback", json=feedback_data)
            if response.status_code in [200, 201]:
                result = response.json()
                print("✅ BHIV Feedback: OK")
                print(f"   Status: {result.get('status')}")
                print(f"   Feedback ID: {result.get('feedback_id')}")
            else:
                print(f"❌ BHIV Feedback: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ BHIV Feedback: {e}")

    print("\n" + "=" * 50)
    print("BHIV API Test Complete")
    print("All endpoints are integrated into main server (port 8000)")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_bhiv_api_endpoints())
