"""
Final Integration Test - Complete BHIV System
Test all components working together
"""

import asyncio
import json
import os
import time
from datetime import datetime
import httpx

class FinalIntegrationTest:
    """Complete integration test for BHIV system"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.auth_token = None
        self.test_results = {}

    async def run_complete_test(self):
        """Run complete integration test"""

        print("🚀 BHIV FINAL INTEGRATION TEST")
        print("=" * 50)

        # Step 1: Authentication
        await self.test_authentication()

        # Step 2: Test complete BHIV workflow
        await self.test_complete_bhiv_workflow()

        # Step 3: Test all new APIs
        await self.test_all_new_apis()

        # Step 4: Test monitoring and logging
        await self.test_monitoring_system()

        # Step 5: Generate final report
        self.generate_final_report()

    async def test_authentication(self):
        """Test authentication system"""

        print("\n1. Testing Authentication...")

        try:
            async with httpx.AsyncClient() as client:
                login_data = {
                    "username": "admin",
                    "password": "bhiv2024"
                }

                response = await client.post(f"{self.base_url}/api/v1/auth/login", data=login_data)

                if response.status_code == 200:
                    token_data = response.json()
                    self.auth_token = token_data.get("access_token")
                    print("✅ Authentication successful")
                    self.test_results["authentication"] = {"status": "success", "token": "obtained"}
                else:
                    print("❌ Authentication failed")
                    self.test_results["authentication"] = {"status": "failed", "error": response.text}

        except Exception as e:
            print(f"❌ Authentication error: {e}")
            self.test_results["authentication"] = {"status": "error", "error": str(e)}

    def get_headers(self):
        """Get request headers with auth"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def test_complete_bhiv_workflow(self):
        """Test complete BHIV workflow end-to-end"""

        print("\n2. Testing Complete BHIV Workflow...")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Test BHIV prompt with all features
                bhiv_request = {
                    "user_id": "test_user_final",
                    "prompt": "Create a modern 3-bedroom house with kitchen island and living room",
                    "city": "Mumbai",
                    "budget": 75000,
                    "area_sqft": 1200,
                    "design_type": "house",
                    "notify_prefect": True
                }

                print("   Submitting BHIV prompt...")
                response = await client.post(
                    f"{self.base_url}/bhiv/v1/prompt",
                    json=bhiv_request,
                    headers=self.get_headers()
                )

                if response.status_code == 201:
                    result = response.json()
                    spec_id = result.get("spec_id")
                    agents = result.get("agents", {})

                    print(f"✅ BHIV prompt successful - Spec ID: {spec_id}")
                    print(f"   Agents executed: {len(agents)}")

                    # Check agent results
                    for agent_name, agent_result in agents.items():
                        status = "✅" if agent_result.get("success") else "❌"
                        duration = agent_result.get("duration_ms", 0)
                        print(f"   {status} {agent_name}: {duration}ms")

                    self.test_results["bhiv_workflow"] = {
                        "status": "success",
                        "spec_id": spec_id,
                        "agents": {name: result.get("success", False) for name, result in agents.items()},
                        "total_duration_ms": result.get("total_duration_ms", 0)
                    }

                    # Test feedback submission
                    feedback_request = {
                        "request_id": result.get("request_id"),
                        "spec_id": spec_id,
                        "user_id": "test_user_final",
                        "rating": 4.5,
                        "feedback_type": "explicit",
                        "notes": "Great design, love the layout",
                        "aspect_ratings": {
                            "aesthetics": 4.5,
                            "functionality": 4.0,
                            "cost_effectiveness": 4.2
                        }
                    }

                    print("   Submitting feedback...")
                    feedback_response = await client.post(
                        f"{self.base_url}/bhiv/v1/feedback",
                        json=feedback_request,
                        headers=self.get_headers()
                    )

                    if feedback_response.status_code == 201:
                        feedback_result = feedback_response.json()
                        print(f"✅ Feedback submitted - ID: {feedback_result.get('feedback_id')}")
                        self.test_results["bhiv_workflow"]["feedback"] = "success"
                    else:
                        print("❌ Feedback submission failed")
                        self.test_results["bhiv_workflow"]["feedback"] = "failed"

                else:
                    print(f"❌ BHIV prompt failed: {response.status_code}")
                    self.test_results["bhiv_workflow"] = {"status": "failed", "error": response.text}

        except Exception as e:
            print(f"❌ BHIV workflow error: {e}")
            self.test_results["bhiv_workflow"] = {"status": "error", "error": str(e)}

    async def test_all_new_apis(self):
        """Test all new API endpoints"""

        print("\n3. Testing All New APIs...")

        # Test MCP Integration API
        await self.test_mcp_api()

        # Test Geometry Generator API
        await self.test_geometry_api()

        # Test Multi-city RL API
        await self.test_multi_city_rl_api()

    async def test_mcp_api(self):
        """Test MCP integration API"""

        print("   Testing MCP Integration API...")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Test MCP compliance check
                mcp_request = {
                    "city": "Mumbai",
                    "spec_json": {
                        "rooms": [{"type": "living_room", "length": 5, "width": 4, "height": 3}],
                        "plot_area": 1000,
                        "built_area": 750
                    },
                    "case_type": "full"
                }

                response = await client.post(
                    f"{self.base_url}/api/v1/mcp/check",
                    json=mcp_request,
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ MCP check successful - Case ID: {result.get('case_id')}")
                    self.test_results["mcp_api"] = {"status": "success", "case_id": result.get("case_id")}
                else:
                    print(f"   ❌ MCP check failed: {response.status_code}")
                    self.test_results["mcp_api"] = {"status": "failed", "error": response.text}

                # Test supported cities
                response = await client.get(
                    f"{self.base_url}/api/v1/mcp/cities",
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    cities = response.json()
                    print(f"   ✅ MCP cities: {len(cities.get('cities', []))} supported")
                else:
                    print("   ❌ MCP cities failed")

        except Exception as e:
            print(f"   ❌ MCP API error: {e}")
            self.test_results["mcp_api"] = {"status": "error", "error": str(e)}

    async def test_geometry_api(self):
        """Test geometry generator API"""

        print("   Testing Geometry Generator API...")

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                # Test GLB generation
                geometry_request = {
                    "spec_json": {
                        "rooms": [
                            {"type": "bedroom", "length": 4, "width": 3, "height": 3},
                            {"type": "kitchen", "length": 3, "width": 3, "height": 3}
                        ],
                        "objects": [
                            {"type": "bed", "dimensions": {"length": 2, "width": 1.5, "height": 0.5}}
                        ]
                    },
                    "request_id": f"final_test_{int(time.time())}",
                    "format": "glb"
                }

                response = await client.post(
                    f"{self.base_url}/api/v1/geometry/generate",
                    json=geometry_request,
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    result = response.json()
                    file_size = result.get("file_size_bytes", 0)
                    print(f"   ✅ Geometry generated - Size: {file_size} bytes")
                    self.test_results["geometry_api"] = {
                        "status": "success",
                        "file_size": file_size,
                        "geometry_url": result.get("geometry_url")
                    }
                else:
                    print(f"   ❌ Geometry generation failed: {response.status_code}")
                    self.test_results["geometry_api"] = {"status": "failed", "error": response.text}

                # Test file listing
                response = await client.get(
                    f"{self.base_url}/api/v1/geometry/list",
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    file_list = response.json()
                    print(f"   ✅ Geometry files: {file_list.get('total_count', 0)} available")
                else:
                    print("   ❌ Geometry file listing failed")

        except Exception as e:
            print(f"   ❌ Geometry API error: {e}")
            self.test_results["geometry_api"] = {"status": "error", "error": str(e)}

    async def test_multi_city_rl_api(self):
        """Test multi-city RL API"""

        print("   Testing Multi-city RL API...")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Test city-specific RL feedback
                feedback_params = {
                    "city": "Mumbai",
                    "design_spec": {
                        "rooms": [{"type": "office", "length": 4, "width": 3}],
                        "plot_area": 500,
                        "built_area": 400
                    },
                    "user_rating": 4.2,
                    "compliance_result": {
                        "compliant": True,
                        "confidence_score": 0.88,
                        "violations": []
                    }
                }

                response = await client.post(
                    f"{self.base_url}/api/v1/rl/feedback/city",
                    params=feedback_params,
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Multi-city RL feedback - ID: {result.get('feedback_id')}")
                    self.test_results["multi_city_rl"] = {
                        "status": "success",
                        "feedback_id": result.get("feedback_id")
                    }
                else:
                    print(f"   ❌ Multi-city RL feedback failed: {response.status_code}")
                    self.test_results["multi_city_rl"] = {"status": "failed", "error": response.text}

                # Test city feedback summary
                response = await client.get(
                    f"{self.base_url}/api/v1/rl/feedback/city/Mumbai/summary",
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    summary = response.json()
                    print(f"   ✅ City feedback summary - Count: {summary.get('feedback_count', 0)}")
                else:
                    print("   ❌ City feedback summary failed")

        except Exception as e:
            print(f"   ❌ Multi-city RL API error: {e}")
            self.test_results["multi_city_rl"] = {"status": "error", "error": str(e)}

    async def test_monitoring_system(self):
        """Test monitoring and logging system"""

        print("\n4. Testing Monitoring System...")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test monitoring metrics
                response = await client.get(
                    f"{self.base_url}/api/v1/monitoring/metrics",
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    metrics = response.json()
                    status = metrics.get("status", "unknown")
                    operations = metrics.get("metrics", {}).get("total_operations", 0)
                    print(f"   ✅ Monitoring metrics - Status: {status}, Operations: {operations}")
                    self.test_results["monitoring"] = {
                        "status": "success",
                        "system_status": status,
                        "total_operations": operations
                    }
                else:
                    print(f"   ❌ Monitoring metrics failed: {response.status_code}")
                    self.test_results["monitoring"] = {"status": "failed", "error": response.text}

                # Test alert system
                response = await client.post(
                    f"{self.base_url}/api/v1/monitoring/alert/test",
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    print("   ✅ Alert system test successful")
                    self.test_results["monitoring"]["alert_system"] = "working"
                else:
                    print("   ❌ Alert system test failed")
                    self.test_results["monitoring"]["alert_system"] = "failed"

        except Exception as e:
            print(f"   ❌ Monitoring system error: {e}")
            self.test_results["monitoring"] = {"status": "error", "error": str(e)}

    def generate_final_report(self):
        """Generate final integration test report"""

        print("\n" + "=" * 60)
        print("📊 FINAL INTEGRATION TEST REPORT")
        print("=" * 60)

        # Calculate success metrics
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values()
                             if isinstance(result, dict) and result.get("status") == "success")

        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
        print(f"📈 Tests Passed: {successful_tests}/{total_tests}")

        # Detailed results
        print(f"\n📋 Test Results:")

        status_icons = {"success": "✅", "failed": "❌", "error": "💥"}

        for test_name, result in self.test_results.items():
            if isinstance(result, dict):
                status = result.get("status", "unknown")
                icon = status_icons.get(status, "❓")
                print(f"{icon} {test_name.replace('_', ' ').title()}: {status.upper()}")

                # Show key metrics
                if status == "success":
                    if test_name == "bhiv_workflow":
                        agents = result.get("agents", {})
                        successful_agents = sum(1 for success in agents.values() if success)
                        print(f"    Agents: {successful_agents}/{len(agents)} successful")
                        print(f"    Duration: {result.get('total_duration_ms', 0)}ms")
                    elif test_name == "geometry_api":
                        print(f"    File size: {result.get('file_size', 0)} bytes")
                    elif test_name == "monitoring":
                        print(f"    System status: {result.get('system_status', 'unknown')}")
                        print(f"    Operations tracked: {result.get('total_operations', 0)}")

        # Final verdict
        print(f"\n🏆 FINAL VERDICT:")

        if success_rate >= 95:
            print("🎉 EXCELLENT: All BHIV features working perfectly!")
            print("   System is production-ready with all integrations functional.")
        elif success_rate >= 80:
            print("✅ GOOD: Most features working, minor issues present")
            print("   System is mostly functional with some areas needing attention.")
        elif success_rate >= 60:
            print("⚠️  FAIR: Several features need fixing")
            print("   System has significant issues that should be resolved.")
        else:
            print("❌ POOR: Major system issues detected")
            print("   System requires substantial fixes before production use.")

        print("=" * 60)

        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "success_rate": success_rate,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "test_results": self.test_results,
            "summary": {
                "authentication": self.test_results.get("authentication", {}).get("status"),
                "bhiv_workflow": self.test_results.get("bhiv_workflow", {}).get("status"),
                "mcp_api": self.test_results.get("mcp_api", {}).get("status"),
                "geometry_api": self.test_results.get("geometry_api", {}).get("status"),
                "multi_city_rl": self.test_results.get("multi_city_rl", {}).get("status"),
                "monitoring": self.test_results.get("monitoring", {}).get("status")
            }
        }

        report_file = f"bhiv_final_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Detailed report saved: {report_file}")


async def main():
    """Run final integration test"""
    tester = FinalIntegrationTest()
    await tester.run_complete_test()


if __name__ == "__main__":
    asyncio.run(main())
