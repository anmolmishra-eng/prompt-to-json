"""
Test All Core APIs - Comprehensive Validation
Tests: /history, /reports/{spec}, /bhiv/v1/prompt, /rl/feedback
"""
import asyncio

import httpx

BASE_URL = "http://localhost:8000"
TOKEN = None


async def login():
    """Get authentication token"""
    global TOKEN
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login", json={"username": "admin", "password": "bhiv2024"}
        )
        if response.status_code == 200:
            TOKEN = response.json()["access_token"]
            print("✅ Authentication successful")
            return True
        print(f"❌ Login failed: {response.status_code}")
        return False


async def test_history():
    """Test /api/v1/history endpoint"""
    print("\n" + "=" * 70)
    print("Testing /api/v1/history")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/history", headers={"Authorization": f"Bearer {TOKEN}"}, params={"limit": 10}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - /api/v1/history")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Total Specs: {data.get('total_specs', 0)}")
            if data.get("specs"):
                print(f"   First Spec: {data['specs'][0].get('spec_id')}")
            return True
        else:
            print(f"❌ FAILED - /api/v1/history")
            print(f"   Error: {response.text}")
            return False


async def test_reports(spec_id=None):
    """Test /api/v1/reports/{spec_id} endpoint"""
    print("\n" + "=" * 70)
    print("Testing /api/v1/reports/{spec_id}")
    print("=" * 70)

    # First, get a spec_id from history if not provided
    if not spec_id:
        async with httpx.AsyncClient(timeout=30.0) as client:
            hist_response = await client.get(
                f"{BASE_URL}/api/v1/history", headers={"Authorization": f"Bearer {TOKEN}"}, params={"limit": 1}
            )
            if hist_response.status_code == 200:
                specs = hist_response.json().get("specs", [])
                if specs:
                    spec_id = specs[0]["spec_id"]
                    print(f"Using spec_id from history: {spec_id}")

    if not spec_id:
        print("⚠️  No spec_id available, creating test spec...")
        # Create a test spec
        async with httpx.AsyncClient(timeout=60.0) as client:
            gen_response = await client.post(
                f"{BASE_URL}/api/v1/generate",
                headers={"Authorization": f"Bearer {TOKEN}"},
                json={"prompt": "Design a simple kitchen", "city": "Mumbai"},
            )
            if gen_response.status_code in [200, 201]:
                spec_id = gen_response.json().get("spec_id")
                print(f"Created test spec: {spec_id}")

    if not spec_id:
        print("❌ FAILED - Could not get or create spec_id")
        return False

    # Test the reports endpoint
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/reports/{spec_id}", headers={"Authorization": f"Bearer {TOKEN}"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - /api/v1/reports/{spec_id}")
            print(f"   Report ID: {data.get('report_id')}")
            print(f"   Spec ID: {data.get('data', {}).get('spec_id')}")
            print(f"   Iterations: {len(data.get('iterations', []))}")
            print(f"   Evaluations: {len(data.get('evaluations', []))}")
            return True
        else:
            print(f"❌ FAILED - /api/v1/reports/{spec_id}")
            print(f"   Error: {response.text}")
            return False


async def test_bhiv_prompt():
    """Test /bhiv/v1/prompt endpoint"""
    print("\n" + "=" * 70)
    print("Testing /bhiv/v1/prompt")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/bhiv/v1/prompt",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "user_id": "test_user",
                "prompt": "Design a modern 2-bedroom apartment",
                "city": "Mumbai",
                "budget": 5000000,
                "notify_prefect": False,
            },
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ SUCCESS - /bhiv/v1/prompt")
            print(f"   Request ID: {data.get('request_id')}")
            print(f"   Spec ID: {data.get('spec_id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Total Duration: {data.get('total_duration_ms')}ms")

            agents = data.get("agents", {})
            print(f"   Agents:")
            for agent_name, agent_result in agents.items():
                status = "✅" if agent_result.get("success") else "❌"
                print(f"     {status} {agent_name}: {agent_result.get('duration_ms')}ms")

            return True, data.get("spec_id")
        else:
            print(f"❌ FAILED - /bhiv/v1/prompt")
            print(f"   Error: {response.text}")
            return False, None


async def test_rl_feedback(spec_id=None):
    """Test /api/v1/rl/feedback endpoint"""
    print("\n" + "=" * 70)
    print("Testing /api/v1/rl/feedback")
    print("=" * 70)

    # Get two spec IDs for comparison
    async with httpx.AsyncClient(timeout=30.0) as client:
        hist_response = await client.get(
            f"{BASE_URL}/api/v1/history", headers={"Authorization": f"Bearer {TOKEN}"}, params={"limit": 2}
        )

        spec_ids = []
        if hist_response.status_code == 200:
            specs = hist_response.json().get("specs", [])
            spec_ids = [s["spec_id"] for s in specs[:2]]

        # If we don't have 2 specs, use the same one twice
        if len(spec_ids) < 2:
            if spec_id:
                spec_ids = [spec_id, spec_id]
            else:
                print("⚠️  No specs available for feedback test")
                return False

        print(f"Using specs: {spec_ids[0]}, {spec_ids[1]}")

        # Submit feedback
        response = await client.post(
            f"{BASE_URL}/api/v1/rl/feedback",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "design_a_id": spec_ids[0],
                "design_b_id": spec_ids[1],
                "rating_a": 4.5,
                "rating_b": 3.5,
                "preference": "A",
                "reason": "Better layout and design",
            },
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - /api/v1/rl/feedback")
            print(f"   Status: {data.get('ok')}")
            print(f"   Message: {data.get('message')}")
            if "rl_service_response" in data:
                print(f"   RL Service: Connected")
            elif "rl_service_error" in data:
                print(f"   RL Service: Fallback (local only)")
            return True
        else:
            print(f"❌ FAILED - /api/v1/rl/feedback")
            print(f"   Error: {response.text}")
            return False


async def main():
    print("=" * 70)
    print("CORE API VALIDATION TEST SUITE")
    print("=" * 70)

    # Login
    if not await login():
        print("\n❌ Authentication failed. Cannot proceed with tests.")
        return

    results = {}

    # Test 1: /history
    results["history"] = await test_history()

    # Test 2: /reports/{spec}
    results["reports"] = await test_reports()

    # Test 3: /bhiv/v1/prompt
    bhiv_success, spec_id = await test_bhiv_prompt()
    results["bhiv_prompt"] = bhiv_success

    # Test 4: /rl/feedback
    results["rl_feedback"] = await test_rl_feedback(spec_id)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for endpoint, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {endpoint}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL CORE APIS WORKING - NO 404 OR 500 ERRORS!")
    else:
        print("\n⚠️  Some endpoints need attention")


if __name__ == "__main__":
    asyncio.run(main())
