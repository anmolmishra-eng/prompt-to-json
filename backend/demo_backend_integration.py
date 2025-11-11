import json
import time
from typing import Any, Dict

import requests


class BackendDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {}

    def login(self, username: str = "user", password: str = "pass") -> str:
        """Login and get JWT token"""
        print(f"\n1. Logging in as {username}...")

        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": username, "password": password},
        )

        if response.status_code != 200:
            raise Exception(f"Login failed: {response.text}")

        data = response.json()
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        print(f"✓ Login successful, token: {self.token[:20]}...")
        return self.token

    def generate_spec(self, prompt: str, user_id: str = "demo_user") -> Dict[str, Any]:
        """Generate a new design spec"""
        print(f"\n2. Generating spec with prompt: '{prompt}'...")

        gen_req = {
            "user_id": user_id,
            "prompt": prompt,
            "context": {"style": "modern", "budget": "medium"},
            "project_id": "demo_project_001",
        }

        response = requests.post(
            f"{self.base_url}/api/v1/generate", json=gen_req, headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(f"Generate failed: {response.text}")

        result = response.json()
        print(f"✓ Generated spec_id: {result['spec_id']}")
        print(f"  Preview URL: {result['preview_url'][:50]}...")

        return result

    def switch_material(
        self, spec_id: str, target: str = "floor_1", material: str = "marble_white"
    ) -> Dict[str, Any]:
        """Switch material of an object in the spec"""
        print(f"\n3. Switching material of {target} to {material}...")

        switch_req = {"spec_id": spec_id, "target": target, "material": material}

        response = requests.post(
            f"{self.base_url}/api/v1/switch", json=switch_req, headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(f"Switch failed: {response.text}")

        result = response.json()
        print(f"✓ Material switched, iteration_id: {result['iteration_id']}")
        print(f"  Changed: {result['changed']}")

        return result

    def evaluate_spec(
        self,
        spec_id: str,
        rating: int = 4,
        notes: str = "Looks good",
        user_id: str = "demo_user",
    ) -> Dict[str, Any]:
        """Evaluate the spec with rating and notes"""
        print(f"\n4. Evaluating spec with rating {rating}...")

        eval_req = {
            "spec_id": spec_id,
            "user_id": user_id,
            "rating": rating,
            "notes": notes,
        }

        response = requests.post(
            f"{self.base_url}/api/v1/evaluate", json=eval_req, headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(f"Evaluate failed: {response.text}")

        result = response.json()
        print(f"✓ Evaluation saved, eval_id: {result['saved_id']}")

        return result

    def iterate_spec(
        self,
        spec_id: str,
        strategy: str = "improve_materials",
        user_id: str = "demo_user",
    ) -> Dict[str, Any]:
        """Iterate on the spec with improvement strategy"""
        print(f"\n5. Iterating spec with strategy: {strategy}...")

        iter_req = {"spec_id": spec_id, "strategy": strategy, "user_id": user_id}

        response = requests.post(
            f"{self.base_url}/api/v1/iterate", json=iter_req, headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(f"Iterate failed: {response.text}")

        result = response.json()
        print(f"✓ Iteration completed")
        print(f"  Feedback: {result['feedback'][:50]}...")

        return result

    def run_compliance(self) -> Dict[str, Any]:
        """Run compliance check (simulated)"""
        print(f"\n6. Running compliance check...")

        comp_req = {
            "case_params": {
                "design_type": "interior",
                "safety_level": "standard",
                "materials": ["marble", "wood"],
            },
            "geometry_data": "base64_encoded_geometry_placeholder",
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/compliance/run_case",
                json=comp_req,
                headers=self.headers,
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✓ Compliance check completed")
                return result
            else:
                print(f"⚠ Compliance service unavailable (expected in demo)")
                return {"status": "simulated", "case_id": "demo_case_001"}
        except:
            print(f"⚠ Compliance service unavailable (expected in demo)")
            return {"status": "simulated", "case_id": "demo_case_001"}

    def get_report(self, spec_id: str) -> Dict[str, Any]:
        """Get full spec history report"""
        print(f"\n7. Getting full report for spec {spec_id}...")

        response = requests.get(
            f"{self.base_url}/api/v1/reports/{spec_id}", headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(f"Get report failed: {response.text}")

        result = response.json()
        print(f"✓ Report retrieved")
        print(f"  Iterations: {len(result['iterations'])}")
        print(f"  Evaluations: {len(result['evaluations'])}")
        print(f"  Preview URLs: {len(result['preview_urls'])}")

        return result

    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        response = requests.get(f"{self.base_url}/api/v1/health")
        return response.json()


def main():
    """Run complete end-to-end demo workflow"""
    print("=== Backend Integration Demo ===")
    print(
        "Testing complete generate → switch → evaluate → iterate → compliance → report flow"
    )

    demo = BackendDemo()

    try:
        # 0. Health check
        print("\n0. Checking service health...")
        health = demo.health_check()
        print(f"✓ Service status: {health['status']}, uptime: {health['uptime']:.1f}s")

        # 1. Login
        demo.login()

        # 2. Generate spec
        gen_result = demo.generate_spec(
            "A modern living room with comfortable seating and natural lighting"
        )
        spec_id = gen_result["spec_id"]

        # 3. Switch material
        switch_result = demo.switch_material(spec_id, "sofa_1", "leather_brown")

        # 4. Evaluate
        eval_result = demo.evaluate_spec(
            spec_id, 5, "Excellent design after material change"
        )

        # 5. Iterate
        iter_result = demo.iterate_spec(spec_id, "optimize_lighting")

        # 6. Compliance (simulated)
        comp_result = demo.run_compliance()

        # 7. Get final report
        report = demo.get_report(spec_id)

        print("\n=== Demo Completed Successfully ===")
        print(
            f"Final spec has {len(report['iterations'])} iterations and {len(report['evaluations'])} evaluations"
        )
        print(f"Spec ID: {spec_id}")

        # Save demo results
        with open("demo_results.json", "w") as f:
            json.dump(
                {
                    "spec_id": spec_id,
                    "generate": gen_result,
                    "switch": switch_result,
                    "evaluate": eval_result,
                    "iterate": iter_result,
                    "compliance": comp_result,
                    "report": report,
                },
                f,
                indent=2,
                default=str,
            )

        print("Demo results saved to demo_results.json")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        return False

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
