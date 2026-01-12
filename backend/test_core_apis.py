"""
Test Broken Core APIs - Comprehensive Validation
Tests: /history, /reports/{spec}, /bhiv/v1/prompt, /rl/feedback
"""
import asyncio
import json

import httpx

BASE_URL = "http://localhost:8000"
TOKEN = None


async def login():
    """Get authentication token"""
    global TOKEN
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login", data={"username": "admin", "password": "bhiv2024"}
        )
        if response.status_code == 200:
            TOKEN = response.json()["access_token"]
            print("Authenticated")
            return True
        print(f"Login failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False


async def test_history():
    """Test /api/v1/history endpoint"""
    print("\n[1/4] Testing /api/v1/history...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/api/v1/history", headers={"Authorization": f"Bearer {TOKEN}"})

        if response.status_code == 200:
            result = response.json()
            print(f"  PASS - History endpoint working")
            print(f"  User: {result.get('user_id')}")
            print(f"  Total specs: {result.get('total_specs', 0)}")
            return True
        else:
            print(f"  FAIL - Status {response.status_code}")
            print(f"  Error: {response.text}")
            return False


async def test_reports_spec():
    """Test /api/v1/reports/{spec_id} endpoint"""
    print("\n[2/4] Testing /api/v1/reports/{spec_id}...")

    # First create a spec
    async with httpx.AsyncClient(timeout=60.0) as client:
        gen_response = await client.post(
            f"{BASE_URL}/api/v1/generate",
            json={"prompt": "Design a small room", "city": "Mumbai"},
            headers={"Authorization": f"Bearer {TOKEN}"},
        )

        if gen_response.status_code != 200:
            print(f"  FAIL - Could not create test spec: {gen_response.status_code}")
            return False

        spec_id = gen_response.json().get("spec_id")
        print(f"  Created test spec: {spec_id}")

        # Now test reports endpoint
        response = await client.get(
            f"{BASE_URL}/api/v1/reports/{spec_id}", headers={"Authorization": f"Bearer {TOKEN}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"  PASS - Reports endpoint working")
            print(f"  Report ID: {result.get('report_id')}")
            print(f"  Iterations: {len(result.get('iterations', []))}")
            print(f"  Evaluations: {len(result.get('evaluations', []))}")
            return True
        else:
            print(f"  FAIL - Status {response.status_code}")
            print(f"  Error: {response.text}")
            return False


async def test_bhiv_prompt():
    """Test /bhiv/v1/prompt endpoint"""
    print("\n[3/4] Testing /bhiv/v1/prompt...")

    payload = {
        "user_id": "test_user",
        "prompt": "Design a modern kitchen with island",
        "city": "Mumbai",
        "design_type": "kitchen",
        "budget": 500000,
        "area_sqft": 150,
        "notify_prefect": False,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/bhiv/v1/prompt", json=payload, headers={"Authorization": f"Bearer {TOKEN}"}
        )

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"  PASS - BHIV prompt endpoint working")
            print(f"  Request ID: {result.get('request_id')}")
            print(f"  Spec ID: {result.get('spec_id')}")
            print(f"  Status: {result.get('status')}")

            agents = result.get("agents", {})
            print(f"  Agents executed: {len(agents)}")
            for name, agent_result in agents.items():
                status = "SUCCESS" if agent_result.get("success") else "FAILED"
                print(f"    - {name}: {status}")

            return True
        else:
            print(f"  FAIL - Status {response.status_code}")
            print(f"  Error: {response.text}")
            return False


async def test_rl_feedback():
    """Test /api/v1/rl/feedback endpoint"""
    print("\n[4/4] Testing /api/v1/rl/feedback...")

    # Create two specs for feedback
    async with httpx.AsyncClient(timeout=60.0) as client:
        gen_response = await client.post(
            f"{BASE_URL}/api/v1/generate",
            json={"prompt": "Design option A", "city": "Pune"},
            headers={"Authorization": f"Bearer {TOKEN}"},
        )

        if gen_response.status_code != 200:
            print(f"  FAIL - Could not create test specs")
            return False

        spec_a_id = gen_response.json().get("spec_id")
        spec_b_id = spec_a_id  # Use same for testing

        # Submit feedback
        feedback_payload = {
            "design_a_id": spec_a_id,
            "design_b_id": spec_b_id,
            "preference": "A",
            "rating_a": 4,
            "rating_b": 3,
            "reason": "Better layout and design",
        }

        response = await client.post(
            f"{BASE_URL}/api/v1/rl/feedback", json=feedback_payload, headers={"Authorization": f"Bearer {TOKEN}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"  PASS - RL feedback endpoint working")
            print(f"  Status: {result.get('ok')}")
            print(f"  Message: {result.get('message')}")

            if "rl_service_response" in result:
                print(f"  RL service integration: WORKING")
            elif "rl_service_error" in result:
                print(f"  RL service integration: ERROR (saved locally)")

            return True
        else:
            print(f"  FAIL - Status {response.status_code}")
            print(f"  Error: {response.text}")
            return False


async def main():
    print("=" * 70)
    print("Testing Broken Core APIs")
    print("=" * 70)

    if not await login():
        print("\nERROR: Authentication failed. Cannot proceed with tests.")
        return

    results = []

    # Test all endpoints
    results.append(("History", await test_history()))
    results.append(("Reports", await test_reports_spec()))
    results.append(("BHIV Prompt", await test_bhiv_prompt()))
    results.append(("RL Feedback", await test_rl_feedback()))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status} - {name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("ALL CORE APIs WORKING - No 404 or 500!")
    else:
        print("Some endpoints need fixing")


if __name__ == "__main__":
    asyncio.run(main())
