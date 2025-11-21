#!/usr/bin/env python3
"""
End-to-end demo of Design Engine:
Generate → Switch → Evaluate → Iterate → Store → Preview
"""

import asyncio
import json
from datetime import datetime
from typing import Optional

import httpx

API_BASE = "http://localhost:8000/api/v1"
USERNAME = "demo"
PASSWORD = "demo123"


class DesignEngineDemo:
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url
        self.token = None
        self.headers = {}

    async def setup(self):
        """Login and get JWT token"""
        print("\n[SETUP] Authenticating...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login", json={"username": USERNAME, "password": PASSWORD}
            )

            if response.status_code != 200:
                print(f"❌ Auth failed: {response.text}")
                return False

            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

            print(f"✅ Authenticated as {USERNAME}")
            return True

    async def run_full_workflow(self):
        """Run complete workflow"""
        print("\n" + "=" * 80)
        print("🎨 DESIGN ENGINE END-TO-END DEMO")
        print("=" * 80)

        if not await self.setup():
            return

        user_id = "demo_user_001"

        # 1. Generate
        print("\n[1/5] 🎨 GENERATE DESIGN SPEC")
        prompt = "Design a modern living room with marble floor, grey fabric sofa, and wooden dining table"
        spec_id, spec_data = await self.generate_spec(user_id, prompt)

        if not spec_id:
            return

        print(f"✅ Generated spec: {spec_id}")
        print(f"   Objects: {len(spec_data['objects'])} items")
        print(f"   Preview: {spec_data.get('preview_url', 'N/A')[:50]}...")

        # 2. Switch Material
        print("\n[2/5] 🔄 SWITCH MATERIAL (floor to marble)")
        floor_obj = next((o for o in spec_data["objects"] if o["type"] == "floor"), None)

        if floor_obj:
            updated_spec = await self.switch_material(user_id, spec_id, floor_obj["id"], "marble_white")
            if updated_spec:
                print(f"✅ Floor material switched to marble_white")
                print(f"   Iteration: {updated_spec.get('iteration_id')}")

        # 3. Evaluate
        print("\n[3/5] ⭐ EVALUATE DESIGN")
        eval_id = await self.evaluate(user_id, spec_id, rating=4.5, notes="Great modern aesthetic")

        if eval_id:
            print(f"✅ Evaluation saved: {eval_id}")
            print(f"   Rating: 4.5/5")

        # 4. Iterate
        print("\n[4/5] 🚀 ITERATE/IMPROVE")
        improved_spec = await self.iterate(user_id, spec_id, strategy="improve_materials")

        if improved_spec:
            print(f"✅ Iteration applied: {improved_spec.get('iteration_id')}")
            print(f"   Feedback: {improved_spec.get('feedback')}")

        # 5. Get History
        print("\n[5/5] 📜 RETRIEVE HISTORY")
        history = await self.get_history(spec_id)

        if history:
            print(f"✅ History retrieved")
            print(f"   Total iterations: {len(history.get('iterations', []))}")

        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETE!")
        print("=" * 80)

    async def generate_spec(self, user_id: str, prompt: str) -> tuple:
        """Generate design spec"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/generate",
                json={
                    "user_id": user_id,
                    "prompt": prompt,
                    "project_id": "demo_project_001",
                    "context": {"style": "modern", "budget": 50000},
                },
                headers=self.headers,
                timeout=30.0,
            )

            if response.status_code != 200:
                print(f"❌ Generate failed: {response.text}")
                return None, None

            data = response.json()
            return data["spec_id"], data["spec_json"]

    async def switch_material(self, user_id: str, spec_id: str, object_id: str, material: str) -> dict:
        """Switch material"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/switch",
                json={
                    "user_id": user_id,
                    "spec_id": spec_id,
                    "target": {"object_id": object_id},
                    "update": {"material": material},
                    "note": f"Changed to {material}",
                },
                headers=self.headers,
                timeout=30.0,
            )

            if response.status_code != 200:
                print(f"❌ Switch failed: {response.text}")
                return None

            return response.json()

    async def evaluate(self, user_id: str, spec_id: str, rating: float, notes: str) -> str:
        """Evaluate spec"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/evaluate",
                json={"user_id": user_id, "spec_id": spec_id, "rating": rating, "notes": notes},
                headers=self.headers,
                timeout=30.0,
            )

            if response.status_code != 200:
                print(f"❌ Evaluate failed: {response.text}")
                return None

            return response.json()["saved_id"]

    async def iterate(self, user_id: str, spec_id: str, strategy: str) -> dict:
        """Iterate spec"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/iterate",
                json={"user_id": user_id, "spec_id": spec_id, "strategy": strategy},
                headers=self.headers,
                timeout=30.0,
            )

            if response.status_code != 200:
                print(f"❌ Iterate failed: {response.text}")
                return None

            return response.json()

    async def get_history(self, spec_id: str) -> dict:
        """Get spec history"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/reports/{spec_id}", headers=self.headers, timeout=30.0)

            if response.status_code != 200:
                print(f"⚠️ History unavailable: {response.status_code}")
                return None

            return response.json()


async def main():
    print(f"\n🚀 Starting Demo at {datetime.now().isoformat()}")

    demo = DesignEngineDemo()
    await demo.run_full_workflow()

    print(f"✨ Demo ended at {datetime.now().isoformat()}\n")


if __name__ == "__main__":
    asyncio.run(main())
