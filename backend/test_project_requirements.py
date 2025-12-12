#!/usr/bin/env python3
"""
Test Project Requirements Implementation
Tests the specific requirements mentioned in the project brief
"""
import asyncio
import json
import sys
from datetime import datetime

import httpx

BASE_URL = "http://localhost:8000"
TEST_USER = {"username": "admin", "password": "bhiv2024"}


class ProjectRequirementsTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.client = httpx.AsyncClient(timeout=30.0)

    async def authenticate(self):
        """Get JWT token"""
        try:
            response = await self.client.post(f"{self.base_url}/api/v1/auth/login", data=TEST_USER)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("access_token")
                return True
            else:
                print(f"Auth failed with status {response.status_code}: {response.text}")
            return False
        except Exception as e:
            print(f"Auth failed: {e}")
            return False

    def get_headers(self):
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}" if self.token else ""}

    async def test_dependency_mapping(self):
        """Test: Map dependencies between MCP rules, RL weights, and geometry outputs"""
        print("1. Testing Dependency Mapping...")
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/integration/dependencies/map", headers=self.get_headers()
            )

            if response.status_code == 200:
                result = response.json()
                print("   SUCCESS: Dependency mapping successful")
                print(f"   - MCP Rules: {len(result.get('mcp_rules', {}))} cities")
                print(f"   - RL Weights: {len(result.get('rl_weights', {}))} parameters")
                print(f"   - Feedback Loops: {len(result.get('feedback_loops', []))} loops")
                return True
            else:
                print(f"   FAILED: Dependency mapping failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ERROR: Dependency mapping error: {e}")
            return False

    async def test_modular_separation(self):
        """Test: Ensure modular separation between core compliance, RL, and BHIV layers"""
        print("2. Testing Modular Separation...")
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/integration/separation/validate", headers=self.get_headers()
            )

            if response.status_code == 200:
                result = response.json()
                print("   SUCCESS: Modular separation validated")
                print(
                    f"   - Core Compliance: {'Isolated' if result.get('core_compliance', {}).get('isolated') else 'Not Isolated'}"
                )
                print(
                    f"   - RL Calculations: {'Isolated' if result.get('rl_calculations', {}).get('isolated') else 'Not Isolated'}"
                )
                print(
                    f"   - BHIV Assistant: {'Isolated' if result.get('bhiv_assistant', {}).get('isolated') else 'Not Isolated'}"
                )
                return True
            else:
                print(f"   FAILED: Modular separation validation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ERROR: Modular separation error: {e}")
            return False

    async def test_bhiv_activation(self):
        """Test: Activate BHIV AI Assistant layer through central bucket/core"""
        print("3. Testing BHIV AI Assistant Activation...")
        try:
            activation_data = {
                "user_id": "test_user",
                "prompt": "Design a modern kitchen with island",
                "city": "Mumbai",
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/integration/bhiv/activate", headers=self.get_headers(), json=activation_data
            )

            if response.status_code == 200:
                result = response.json()
                print("   SUCCESS: BHIV Assistant activated successfully")
                print(f"   - Activation ID: {result.get('activation_id')}")
                print(f"   - MCP Rules Fetched: {len(result.get('mcp_rules', {}).get('rules', []))} rules")
                print(f"   - RL Optimization: {result.get('rl_optimization', {}).get('source', 'N/A')}")
                print(f"   - Feedback Logged: {result.get('feedback_logged', 'N/A')}")
                return True
            else:
                print(f"   FAILED: BHIV activation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ERROR: BHIV activation error: {e}")
            return False

    async def test_live_rl_feedback(self):
        """Test: RL agent can accept live feedback and update weights dynamically"""
        print("4. Testing Live RL Feedback...")
        try:
            feedback_data = {
                "user_id": "test_user",
                "rating": 4.5,
                "city": "Mumbai",
                "design_aspects": {"land_utilization": 4.0, "density_optimization": 5.0},
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/integration/rl/feedback/live", headers=self.get_headers(), json=feedback_data
            )

            if response.status_code == 200:
                result = response.json()
                print("   SUCCESS: Live RL feedback processed successfully")
                print(f"   - Feedback ID: {result.get('feedback_processed', {}).get('feedback_id')}")
                print(f"   - Weights Updated: {result.get('weights_updated', {}).get('land_utilization', 'N/A')}")
                print(f"   - Training Triggered: {result.get('training_triggered', False)}")
                return True
            else:
                print(f"   FAILED: Live RL feedback failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ERROR: Live RL feedback error: {e}")
            return False

    async def test_prefect_workflows(self):
        """Test: Prefect workflow consolidation (replaces N8N)"""
        print("5. Testing Prefect Workflow Consolidation...")
        try:
            pdf_workflow_data = {
                "workflow_type": "pdf_ingestion",
                "input_data": {"pdf_url": "https://example.com/mumbai_dcr.pdf"},
                "city": "Mumbai",
                "async_mode": True,
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/workflows/consolidate/pdf-ingestion",
                headers=self.get_headers(),
                json=pdf_workflow_data,
            )

            if response.status_code == 200:
                result = response.json()
                print("   SUCCESS: PDF ingestion workflow started")
                print(f"   - Workflow ID: {result.get('workflow_id')}")
                print(f"   - Status: {result.get('status')}")
                print(f"   - Estimated Duration: {result.get('estimated_duration_minutes')} minutes")
                return True
            else:
                print(f"   FAILED: Prefect workflow failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ERROR: Prefect workflow error: {e}")
            return False

    async def test_multi_city_integration(self):
        """Test: Multi-city integration for Mumbai, Pune, Ahmedabad, Nashik"""
        print("6. Testing Multi-City Integration...")
        cities = ["Mumbai", "Pune", "Ahmedabad", "Nashik"]

        for city in cities:
            try:
                city_data = {"city": city, "plot_size": 1000, "location": "urban", "road_width": 12}

                response = await self.client.post(
                    f"{self.base_url}/api/v1/integration/cities/{city.lower()}/validate",
                    headers=self.get_headers(),
                    json=city_data,
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"   SUCCESS: {city} integration working")
                    print(f"   - Rules Applied: {len(result.get('rules_applied', []))}")
                else:
                    print(f"   FAILED: {city} integration failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"   ERROR: {city} integration error: {e}")
                return False

        return True

    async def run_all_tests(self):
        """Run all project requirement tests"""
        print("\n=== PROJECT REQUIREMENTS TEST SUITE ===")
        print(f"Testing against: {self.base_url}")
        print(f"Timestamp: {datetime.now()}\n")

        # Authenticate first
        if not await self.authenticate():
            print("CRITICAL: Authentication failed. Cannot proceed with tests.")
            return False

        print("Authentication successful!\n")

        # Run all tests
        tests = [
            self.test_dependency_mapping,
            self.test_modular_separation,
            self.test_bhiv_activation,
            self.test_live_rl_feedback,
            self.test_prefect_workflows,
            self.test_multi_city_integration,
        ]

        passed = 0
        total = len(tests)

        for test in tests:
            try:
                if await test():
                    passed += 1
                print()  # Add spacing between tests
            except Exception as e:
                print(f"   CRITICAL ERROR: {e}\n")

        # Summary
        print("=== TEST SUMMARY ===")
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")

        if passed == total:
            print("\nSUCCESS: ALL TESTS PASSED! Project requirements are working correctly.")
        else:
            print(f"\nWARNING: {total-passed} tests failed. Check the endpoints and try again.")

        await self.client.aclose()
        return passed == total


async def main():
    """Main test execution"""
    tester = ProjectRequirementsTest()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
