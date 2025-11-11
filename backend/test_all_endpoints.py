import asyncio
import json
from datetime import datetime

import httpx

BASE_URL = "http://localhost:8000"
TOKEN = None


async def get_auth_token():
    """Get JWT token for authenticated requests"""
    global TOKEN
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            data={
                "username": "admin",
                "password": "bhiv2024",
                "grant_type": "password",
            },
        )
        if response.status_code == 200:
            TOKEN = response.json()["access_token"]
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False


def get_headers():
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}


async def test_endpoint(client, method, url, data=None, auth_required=True):
    """Test a single endpoint"""
    try:
        headers = get_headers() if auth_required else {}

        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            response = await client.post(url, json=data, headers=headers)

        status = "✅" if response.status_code < 400 else "❌"
        print(f"{status} {method} {url} → {response.status_code}")

        return response.status_code < 400
    except Exception as e:
        print(f"❌ {method} {url} → ERROR: {e}")
        return False


async def run_all_tests():
    """Test all endpoints"""
    print("🚀 Starting Endpoint Testing...")
    print("=" * 50)

    # Get auth token first
    if not await get_auth_token():
        print("❌ Cannot proceed without authentication")
        return

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test data
        generate_data = {
            "user_id": "test_user",
            "prompt": "Design a 20x15 meter modern living room",
            "context": {"style": "modern"},
            "project_id": "test_project",
        }

        evaluate_data = {
            "spec_id": "test_spec",
            "user_id": "test_user",
            "rating": 5,
            "notes": "Great design",
        }

        iterate_data = {
            "spec_id": "test_spec",
            "strategy": "improve_materials",
            "user_id": "test_user",
        }

        switch_data = {
            "spec_id": "test_spec",
            "target": "sofa_1",
            "material": "leather_brown",
        }

        rl_train_data = {"steps": 100, "rm_epochs": 2}

        # Test endpoints
        tests = [
            # Health & Monitoring (no auth)
            ("GET", f"{BASE_URL}/api/v1/", None, False),
            ("GET", f"{BASE_URL}/api/v1/health", None, False),
            ("GET", f"{BASE_URL}/api/v1/metrics", None, False),
            ("GET", f"{BASE_URL}/api/v1/test-error", None, False),
            # Core Design Engine (auth required)
            ("POST", f"{BASE_URL}/api/v1/generate", generate_data, True),
            ("POST", f"{BASE_URL}/api/v1/evaluate", evaluate_data, True),
            ("POST", f"{BASE_URL}/api/v1/iterate", iterate_data, True),
            ("POST", f"{BASE_URL}/api/v1/switch", switch_data, True),
            # Core Operations
            ("GET", f"{BASE_URL}/api/v1/status", None, True),
            # RL/RLHF Training
            ("POST", f"{BASE_URL}/api/v1/rl/train/rlhf", rl_train_data, True),
            ("POST", f"{BASE_URL}/api/v1/rl/train/opt", {"steps": 100}, True),
            (
                "POST",
                f"{BASE_URL}/api/v1/rl/suggest/iterate",
                {"spec": {"components": ["test"]}, "strategy": "auto_optimize"},
                True,
            ),
        ]

        # Run tests
        passed = 0
        total = len(tests)

        for method, url, data, auth_required in tests:
            success = await test_endpoint(client, method, url, data, auth_required)
            if success:
                passed += 1

        # Results
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} endpoints passed")
        print(f"✅ Success Rate: {(passed/total)*100:.1f}%")

        if passed == total:
            print("🎉 All endpoints are working correctly!")
        else:
            print(f"⚠️  {total-passed} endpoints need attention")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
