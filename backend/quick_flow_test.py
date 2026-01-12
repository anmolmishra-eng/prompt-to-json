"""Quick test - single flow"""
import asyncio

import httpx

BASE_URL = "http://localhost:8000"


async def test():
    # Login
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{BASE_URL}/api/v1/auth/login", data={"username": "admin", "password": "bhiv2024"})
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Generate
        print("[1/6] Generate...")
        r = await client.post(
            f"{BASE_URL}/api/v1/generate",
            json={"prompt": "Design a modern test room with furniture", "city": "Mumbai", "user_id": "admin"},
            headers=headers,
        )
        print(f"  {r.status_code}")
        if r.status_code not in [200, 201]:
            print(f"  ERROR: {r.text}")
            return
        data = r.json()
        spec_id = data["spec_id"]
        spec_json = data.get("spec_json", {})

        # MCP
        print("[2/6] MCP...")
        r = await client.post(
            f"{BASE_URL}/api/v1/mcp/check",
            json={
                "project_id": "test",
                "case_id": "test",
                "city": "Mumbai",
                "document": "Mumbai_DCR.pdf",
                "spec_json": spec_json,
                "parameters": {"plot_size": 1000, "location": "urban", "road_width": 15},
            },
            headers=headers,
        )
        print(f"  {r.status_code}")
        if r.status_code != 200:
            print(f"  ERROR: {r.text[:200]}")

        # RL
        print("[3/6] RL...")
        r = await client.post(
            f"{BASE_URL}/api/v1/rl/optimize",
            json={"spec_id": spec_id, "spec_json": spec_json, "city": "Mumbai", "optimization_goals": ["cost"]},
            headers=headers,
        )
        print(f"  {r.status_code}")
        if r.status_code != 200:
            print(f"  ERROR: {r.text[:200]}")

        # Geometry
        print("[4/6] Geometry...")
        r = await client.post(
            f"{BASE_URL}/api/v1/geometry/generate",
            json={"spec_id": spec_id, "spec_json": spec_json, "request_id": "test123"},
            headers=headers,
        )
        print(f"  {r.status_code}")
        if r.status_code != 200:
            print(f"  ERROR: {r.text[:200]}")

        # Feedback
        print("[5/6] Feedback...")
        r = await client.post(
            f"{BASE_URL}/api/v1/rl/feedback",
            json={
                "design_a_id": spec_id,
                "design_b_id": spec_id,
                "preference": "A",
                "rating_a": 4,
                "rating_b": 3,
                "reason": "test",
            },
            headers=headers,
        )
        print(f"  {r.status_code}")

        # Training
        print("[6/6] Training...")
        r = await client.post(f"{BASE_URL}/api/v1/rl/train/rlhf", json={"batch_size": 1, "epochs": 1}, headers=headers)
        print(f"  {r.status_code}")

        print("\nDONE")


asyncio.run(test())
