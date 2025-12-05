#!/usr/bin/env python3
"""
Complete System Integration Test
Tests all components of the BHIV AI Assistant system
"""

import asyncio
import json
import time
from datetime import datetime

import httpx


class SystemTester:
    def __init__(self):
        self.main_api = "http://localhost:8000"
        self.bhiv_api = "http://localhost:8003"
        self.prefect_api = "http://localhost:4200"
        self.results = []

    async def test_service_health(self, name: str, url: str, endpoint: str = "/health"):
        """Test if a service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{url}{endpoint}")
                if response.status_code == 200:
                    self.log_success(f"✅ {name} is healthy")
                    return True
                else:
                    self.log_error(f"❌ {name} returned {response.status_code}")
                    return False
        except Exception as e:
            self.log_error(f"❌ {name} connection failed: {e}")
            return False

    async def test_main_api_endpoints(self):
        """Test main API endpoints"""
        print("\n🔍 Testing Main API Endpoints...")

        endpoints = [
            ("/api/v1/health", "Health Check"),
            ("/api/v1/generate", "Design Generation"),
            ("/api/v1/compliance/regulations", "Compliance Regulations"),
            ("/api/v1/cities", "Multi-City Support"),
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint, name in endpoints:
                try:
                    if endpoint == "/api/v1/generate":
                        # POST request for generate
                        payload = {
                            "prompt": "Design a modern 2BHK apartment in Mumbai",
                            "city": "Mumbai",
                            "budget": 50000
                        }
                        response = await client.post(f"{self.main_api}{endpoint}", json=payload)
                    else:
                        # GET request for others
                        response = await client.get(f"{self.main_api}{endpoint}")

                    if response.status_code in [200, 201]:
                        self.log_success(f"✅ {name}: {response.status_code}")
                    else:
                        self.log_warning(f"⚠️ {name}: {response.status_code}")

                except Exception as e:
                    self.log_error(f"❌ {name}: {e}")

    async def test_bhiv_assistant(self):
        """Test BHIV AI Assistant endpoints"""
        print("\n🧠 Testing BHIV AI Assistant...")

        endpoints = [
            ("/health", "BHIV Health"),
            ("/bhiv/v1/health", "BHIV Assistant Health"),
            ("/mcp/metadata/Mumbai", "MCP Integration"),
            ("/rl/feedback", "RL Integration"),
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint, name in endpoints:
                try:
                    if endpoint == "/rl/feedback":
                        # POST request for RL feedback
                        payload = {
                            "user_id": "test_user",
                            "spec_id": "test_spec",
                            "rating": 4.5,
                            "design_accepted": True
                        }
                        response = await client.post(f"{self.bhiv_api}{endpoint}", json=payload)
                    else:
                        # GET request for others
                        response = await client.get(f"{self.bhiv_api}{endpoint}")

                    if response.status_code in [200, 201]:
                        self.log_success(f"✅ {name}: {response.status_code}")
                    else:
                        self.log_warning(f"⚠️ {name}: {response.status_code}")

                except Exception as e:
                    self.log_error(f"❌ {name}: {e}")

    async def test_external_services(self):
        """Test external service connectivity"""
        print("\n🌐 Testing External Services...")

        # Test Sohum's MCP service
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get("https://ai-rule-api-w7z5.onrender.com/health")
                if response.status_code == 200:
                    self.log_success("✅ Sohum MCP Service: Connected")
                else:
                    self.log_warning(f"⚠️ Sohum MCP Service: {response.status_code}")
        except Exception as e:
            self.log_error(f"❌ Sohum MCP Service: {e}")

    async def test_prefect_workflows(self):
        """Test Prefect workflow system"""
        print("\n⚙️ Testing Prefect Workflows...")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test Prefect API
                response = await client.get(f"{self.prefect_api}/api/health")
                if response.status_code == 200:
                    self.log_success("✅ Prefect Server: Connected")
                else:
                    self.log_warning(f"⚠️ Prefect Server: {response.status_code}")

                # Test deployments
                response = await client.get(f"{self.prefect_api}/api/deployments")
                if response.status_code == 200:
                    deployments = response.json()
                    self.log_success(f"✅ Prefect Deployments: {len(deployments)} found")
                else:
                    self.log_warning("⚠️ Prefect Deployments: Not accessible")

        except Exception as e:
            self.log_error(f"❌ Prefect System: {e}")

    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        print("\n🔄 Testing End-to-End Workflow...")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 1. Generate design
                design_payload = {
                    "prompt": "Design a modern 2BHK apartment in Mumbai with balcony",
                    "city": "Mumbai",
                    "budget": 75000,
                    "user_id": "test_user_e2e"
                }

                response = await client.post(f"{self.main_api}/api/v1/generate", json=design_payload)
                if response.status_code in [200, 201]:
                    design_data = response.json()
                    spec_id = design_data.get("spec_id", "test_spec")
                    self.log_success("✅ Design Generation: Success")

                    # 2. Test BHIV orchestration
                    bhiv_payload = {
                        "user_id": "test_user_e2e",
                        "prompt": "Optimize this design for better lighting",
                        "city": "Mumbai",
                        "spec_id": spec_id
                    }

                    response = await client.post(f"{self.bhiv_api}/bhiv/v1/design", json=bhiv_payload)
                    if response.status_code in [200, 201]:
                        self.log_success("✅ BHIV Orchestration: Success")
                    else:
                        self.log_warning(f"⚠️ BHIV Orchestration: {response.status_code}")

                    # 3. Submit RL feedback
                    feedback_payload = {
                        "user_id": "test_user_e2e",
                        "spec_id": spec_id,
                        "rating": 4.8,
                        "design_accepted": True,
                        "feedback_text": "Great design with excellent lighting"
                    }

                    response = await client.post(f"{self.bhiv_api}/rl/feedback", json=feedback_payload)
                    if response.status_code in [200, 201]:
                        self.log_success("✅ RL Feedback: Success")
                    else:
                        self.log_warning(f"⚠️ RL Feedback: {response.status_code}")

                else:
                    self.log_error(f"❌ Design Generation failed: {response.status_code}")

        except Exception as e:
            self.log_error(f"❌ End-to-End Workflow: {e}")

    def log_success(self, message: str):
        print(message)
        self.results.append({"status": "success", "message": message, "timestamp": datetime.now().isoformat()})

    def log_warning(self, message: str):
        print(message)
        self.results.append({"status": "warning", "message": message, "timestamp": datetime.now().isoformat()})

    def log_error(self, message: str):
        print(message)
        self.results.append({"status": "error", "message": message, "timestamp": datetime.now().isoformat()})

    async def run_all_tests(self):
        """Run all system tests"""
        print("=" * 70)
        print("🚀 BHIV AI Assistant - Complete System Test")
        print("=" * 70)

        start_time = time.time()

        # Test service health
        print("\n🏥 Testing Service Health...")
        await self.test_service_health("Main API", self.main_api, "/api/v1/health")
        await self.test_service_health("BHIV Assistant", self.bhiv_api, "/health")
        await self.test_service_health("Prefect Server", self.prefect_api, "/api/health")

        # Test individual components
        await self.test_main_api_endpoints()
        await self.test_bhiv_assistant()
        await self.test_external_services()
        await self.test_prefect_workflows()

        # Test end-to-end workflow
        await self.test_end_to_end_workflow()

        # Generate summary
        end_time = time.time()
        duration = end_time - start_time

        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)

        success_count = len([r for r in self.results if r["status"] == "success"])
        warning_count = len([r for r in self.results if r["status"] == "warning"])
        error_count = len([r for r in self.results if r["status"] == "error"])

        print(f"✅ Successful: {success_count}")
        print(f"⚠️ Warnings: {warning_count}")
        print(f"❌ Errors: {error_count}")
        print(f"⏱️ Duration: {duration:.2f} seconds")

        # Save detailed results
        with open("test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "success": success_count,
                    "warnings": warning_count,
                    "errors": error_count,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat()
                },
                "details": self.results
            }, f, indent=2)

        print(f"\n📄 Detailed results saved to: test_results.json")

        if error_count == 0:
            print("\n🎉 All critical tests passed! System is ready for use.")
        elif error_count < 3:
            print("\n⚠️ System mostly functional with minor issues.")
        else:
            print("\n❌ Multiple critical issues detected. Check service status.")

        print("=" * 70)


async def main():
    """Main test runner"""
    tester = SystemTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
