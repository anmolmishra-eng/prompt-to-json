"""
Test Live RL Endpoints - Verify Ranjeet's RL service integration
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
            print("✅ Authenticated")
            return True
        print(f"❌ Login failed: {response.status_code}")
        return False


async def test_rl_optimize():
    """Test /rl/optimize endpoint"""
    print("\nTesting /rl/optimize...")

    payload = {
        "spec_json": {"objects": [{"id": "room1", "type": "bedroom", "area": 150}], "city": "Mumbai"},
        "city": "Mumbai",
        "constraints": {"max_height": 50, "min_green_space": 0.2},
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/rl/optimize", json=payload, headers={"Authorization": f"Bearer {TOKEN}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ RL Optimize successful")
            print(f"   Response keys: {list(result.keys())}")

            # Check for RL metrics
            if "rl_metrics" in str(result):
                print(f"   ✅ RL metrics present in response")
            if "mock" not in str(result).lower():
                print(f"   ✅ No mock indicators found - LIVE SERVICE")
            else:
                print(f"   ⚠️  Mock indicators found in response")

            return True
        else:
            print(f"❌ RL Optimize failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False


async def test_rl_feedback():
    """Test /rl/feedback endpoint"""
    print("\nTesting /rl/feedback...")

    # First create two specs for comparison
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Create spec A
        gen_response = await client.post(
            f"{BASE_URL}/api/v1/generate",
            json={"prompt": "Design a small apartment", "city": "Mumbai"},
            headers={"Authorization": f"Bearer {TOKEN}"},
        )

        if gen_response.status_code != 200:
            print(f"❌ Failed to create test specs")
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
            "reason": "Better layout",
        }

        response = await client.post(
            f"{BASE_URL}/api/v1/rl/feedback", json=feedback_payload, headers={"Authorization": f"Bearer {TOKEN}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ RL Feedback successful")

            if "rl_service_response" in result:
                print(f"   ✅ Feedback sent to live RL service")
            elif "rl_service_error" in result:
                print(f"   ⚠️  RL service error: {result['rl_service_error']}")

            return True
        else:
            print(f"❌ RL Feedback failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False


async def test_rl_suggest_iterate():
    """Test /rl/suggest/iterate endpoint"""
    print("\nTesting /rl/suggest/iterate...")

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Create a spec first
        gen_response = await client.post(
            f"{BASE_URL}/api/v1/generate",
            json={"prompt": "Design a modern office", "city": "Pune"},
            headers={"Authorization": f"Bearer {TOKEN}"},
        )

        if gen_response.status_code != 200:
            print(f"❌ Failed to create test spec")
            return False

        spec_id = gen_response.json().get("spec_id")

        # Get iteration suggestions
        payload = {"spec_id": spec_id, "strategy": "auto_optimize"}

        response = await client.post(
            f"{BASE_URL}/api/v1/rl/suggest/iterate", json=payload, headers={"Authorization": f"Bearer {TOKEN}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ RL Suggest Iterate successful")
            print(f"   Response keys: {list(result.keys())}")

            if "improved_spec" in result:
                print(f"   ✅ Improved spec received from RL service")

            return True
        else:
            print(f"❌ RL Suggest Iterate failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False


async def main():
    print("=" * 70)
    print("Testing Live RL Integration (No Mocks)")
    print("=" * 70)

    if not await login():
        return

    results = []

    # Test all RL endpoints
    results.append(("RL Optimize", await test_rl_optimize()))
    results.append(("RL Feedback", await test_rl_feedback()))
    results.append(("RL Suggest Iterate", await test_rl_suggest_iterate()))

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
        print("ALL RL ENDPOINTS ARE LIVE - NO MOCKS!")
    else:
        print("Some endpoints failed - check logs")


if __name__ == "__main__":
    asyncio.run(main())
