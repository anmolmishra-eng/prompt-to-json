"""
Test All Missing BHIV Features
Comprehensive validation of implemented features
"""

import asyncio
import json
import os
import time
from datetime import datetime
import httpx

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_123"
TEST_CITY = "Mumbai"

class BHIVFeatureTester:
    """Test all BHIV missing features"""

    def __init__(self):
        self.results = {
            "mcp_integration": {"status": "pending", "details": {}},
            "prefect_workflows": {"status": "pending", "details": {}},
            "multi_city_rl": {"status": "pending", "details": {}},
            "geometry_generation": {"status": "pending", "details": {}},
            "deployment_config": {"status": "pending", "details": {}},
            "monitoring_logging": {"status": "pending", "details": {}}
        }
        self.auth_token = None

    async def run_all_tests(self):
        """Run all feature tests"""

        print("🚀 Testing All Missing BHIV Features")
        print("=" * 50)

        # Get auth token first
        await self.get_auth_token()

        # Test each feature
        await self.test_mcp_integration()
        await self.test_prefect_workflows()
        await self.test_multi_city_rl()
        await self.test_geometry_generation()
        await self.test_deployment_config()
        await self.test_monitoring_logging()

        # Print summary
        self.print_test_summary()

    async def get_auth_token(self):
        """Get authentication token"""

        try:
            async with httpx.AsyncClient() as client:
                # Try to login with demo credentials
                login_data = {
                    "username": "admin",
                    "password": "bhiv2024"
                }

                response = await client.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)

                if response.status_code == 200:
                    token_data = response.json()
                    self.auth_token = token_data.get("access_token")
                    print("✅ Authentication successful")
                else:
                    print("⚠️  Using test without authentication")

        except Exception as e:
            print(f"⚠️  Auth failed, continuing without token: {e}")

    def get_headers(self):
        """Get request headers with auth"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def test_mcp_integration(self):
        """Test MCP/BHIV AI assistant integration"""

        print("\n1. Testing MCP Integration...")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test MCP compliance check
                mcp_request = {
                    "city": TEST_CITY,
                    "spec_json": {
                        "rooms": [{"type": "living_room", "length": 4, "width": 4, "height": 3}],
                        "plot_area": 1000,
                        "built_area": 800
                    },
                    "case_type": "full"
                }

                response = await client.post(
                    f"{BASE_URL}/api/v1/mcp/check",
                    json=mcp_request,
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    result = response.json()
                    self.results["mcp_integration"]["status"] = "success"
                    self.results["mcp_integration"]["details"] = {
                        "case_id": result.get("case_id"),
                        "compliant": result.get("compliant"),
                        "confidence_score": result.get("confidence_score")
                    }
                    print("✅ MCP integration working")
                else:
                    self.results["mcp_integration"]["status"] = "failed"
                    self.results["mcp_integration"]["details"] = {"error": response.text}
                    print(f"❌ MCP integration failed: {response.status_code}")

                # Test BHIV prompt endpoint
                bhiv_request = {
                    "user_id": TEST_USER_ID,
                    "prompt": "Create a modern kitchen with island",
                    "city": TEST_CITY,
                    "budget": 50000,
                    "area_sqft": 200
                }

                response = await client.post(
                    f"{BASE_URL}/bhiv/v1/prompt",
                    json=bhiv_request,
                    headers=self.get_headers()
                )

                if response.status_code == 201:
                    result = response.json()
                    print("✅ BHIV prompt endpoint working")
                    self.results["mcp_integration"]["details"]["bhiv_prompt"] = "success"
                    self.results["mcp_integration"]["details"]["spec_id"] = result.get("spec_id")
                else:
                    print(f"❌ BHIV prompt failed: {response.status_code}")
                    self.results["mcp_integration"]["details"]["bhiv_prompt"] = "failed"

        except Exception as e:
            self.results["mcp_integration"]["status"] = "error"
            self.results["mcp_integration"]["details"] = {"exception": str(e)}
            print(f"❌ MCP integration error: {e}")

    async def test_prefect_workflows(self):
        """Test Prefect workflow automation"""

        print("\n2. Testing Prefect Workflows...")

        try:
            # Check if Prefect server is running
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    response = await client.get("http://localhost:4201/api/health")
                    if response.status_code == 200:
                        print("✅ Prefect server is running")
                        self.results["prefect_workflows"]["status"] = "success"
                        self.results["prefect_workflows"]["details"]["server"] = "running"
                    else:
                        print("❌ Prefect server not responding")
                        self.results["prefect_workflows"]["status"] = "failed"
                        self.results["prefect_workflows"]["details"]["server"] = "not_responding"
                except:
                    print("❌ Prefect server not accessible")
                    self.results["prefect_workflows"]["status"] = "failed"
                    self.results["prefect_workflows"]["details"]["server"] = "not_accessible"

            # Check workflow files exist
            workflow_files = [
                "backend/app/bhiv_assistant/workflows/mcp_compliance_flow.py",
                "backend/app/bhiv_assistant/workflows/rl_integration_flows.py",
                "backend/app/bhiv_assistant/workflows/notification_flows.py"
            ]

            existing_workflows = []
            for workflow in workflow_files:
                if os.path.exists(workflow):
                    existing_workflows.append(workflow)

            self.results["prefect_workflows"]["details"]["workflow_files"] = {
                "total": len(workflow_files),
                "existing": len(existing_workflows),
                "files": existing_workflows
            }

            if len(existing_workflows) == len(workflow_files):
                print("✅ All workflow files present")
            else:
                print(f"⚠️  {len(existing_workflows)}/{len(workflow_files)} workflow files found")

        except Exception as e:
            self.results["prefect_workflows"]["status"] = "error"
            self.results["prefect_workflows"]["details"] = {"exception": str(e)}
            print(f"❌ Prefect workflow test error: {e}")

    async def test_multi_city_rl(self):
        """Test multi-city RL feedback loop"""

        print("\n3. Testing Multi-City RL Feedback...")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test city-specific RL feedback
                feedback_request = {
                    "city": TEST_CITY,
                    "design_spec": {
                        "rooms": [{"type": "kitchen", "length": 3, "width": 4}],
                        "plot_area": 800,
                        "built_area": 600
                    },
                    "user_rating": 4.5,
                    "compliance_result": {
                        "compliant": True,
                        "confidence_score": 0.85,
                        "violations": []
                    }
                }

                response = await client.post(
                    f"{BASE_URL}/api/v1/rl/feedback/city",
                    params=feedback_request,
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    result = response.json()
                    print("✅ Multi-city RL feedback working")
                    self.results["multi_city_rl"]["status"] = "success"
                    self.results["multi_city_rl"]["details"] = {
                        "feedback_id": result.get("feedback_id"),
                        "city": result.get("city")
                    }
                else:
                    print(f"❌ Multi-city RL feedback failed: {response.status_code}")
                    self.results["multi_city_rl"]["status"] = "failed"
                    self.results["multi_city_rl"]["details"] = {"error": response.text}

                # Test city feedback summary
                response = await client.get(
                    f"{BASE_URL}/api/v1/rl/feedback/city/{TEST_CITY}/summary",
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    summary = response.json()
                    print("✅ City feedback summary working")
                    self.results["multi_city_rl"]["details"]["summary"] = summary
                else:
                    print(f"⚠️  City feedback summary failed: {response.status_code}")

        except Exception as e:
            self.results["multi_city_rl"]["status"] = "error"
            self.results["multi_city_rl"]["details"] = {"exception": str(e)}
            print(f"❌ Multi-city RL test error: {e}")

    async def test_geometry_generation(self):
        """Test geometry (.GLB) output generation"""

        print("\n4. Testing Geometry Generation...")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Test GLB generation
                geometry_request = {
                    "spec_json": {
                        "rooms": [
                            {"type": "living_room", "length": 5, "width": 4, "height": 3},
                            {"type": "kitchen", "length": 3, "width": 3, "height": 3}
                        ],
                        "objects": [
                            {"type": "sofa", "dimensions": {"length": 2, "width": 1, "height": 0.8}}
                        ]
                    },
                    "request_id": f"test_{int(time.time())}",
                    "format": "glb"
                }

                response = await client.post(
                    f"{BASE_URL}/api/v1/geometry/generate",
                    json=geometry_request,
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    result = response.json()
                    print("✅ Geometry generation working")
                    self.results["geometry_generation"]["status"] = "success"
                    self.results["geometry_generation"]["details"] = {
                        "geometry_url": result.get("geometry_url"),
                        "file_size_bytes": result.get("file_size_bytes"),
                        "generation_time_ms": result.get("generation_time_ms")
                    }
                else:
                    print(f"❌ Geometry generation failed: {response.status_code}")
                    self.results["geometry_generation"]["status"] = "failed"
                    self.results["geometry_generation"]["details"] = {"error": response.text}

                # Test geometry file listing
                response = await client.get(
                    f"{BASE_URL}/api/v1/geometry/list",
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    file_list = response.json()
                    print(f"✅ Geometry file listing working ({file_list.get('total_count', 0)} files)")
                    self.results["geometry_generation"]["details"]["file_list"] = file_list
                else:
                    print(f"⚠️  Geometry file listing failed: {response.status_code}")

        except Exception as e:
            self.results["geometry_generation"]["status"] = "error"
            self.results["geometry_generation"]["details"] = {"exception": str(e)}
            print(f"❌ Geometry generation test error: {e}")

    async def test_deployment_config(self):
        """Test deployment scripts & .env configuration"""

        print("\n5. Testing Deployment & Configuration...")

        try:
            # Check deployment script exists
            deployment_script = "deploy_complete_bhiv.bat"
            if os.path.exists(deployment_script):
                print("✅ Deployment script exists")
                self.results["deployment_config"]["status"] = "success"
                self.results["deployment_config"]["details"]["deployment_script"] = "exists"
            else:
                print("❌ Deployment script missing")
                self.results["deployment_config"]["status"] = "failed"
                self.results["deployment_config"]["details"]["deployment_script"] = "missing"

            # Check .env configuration
            env_file = "backend/.env.example"
            if os.path.exists(env_file):
                with open(env_file, "r") as f:
                    env_content = f.read()

                # Check for BHIV-specific configurations
                bhiv_configs = [
                    "BHIV_MCP_ENDPOINT",
                    "BHIV_RL_ENDPOINT",
                    "BHIV_GEOMETRY_ENDPOINT"
                ]

                found_configs = []
                for config in bhiv_configs:
                    if config in env_content:
                        found_configs.append(config)

                print(f"✅ Environment configuration updated ({len(found_configs)}/{len(bhiv_configs)} BHIV configs)")
                self.results["deployment_config"]["details"]["env_config"] = {
                    "total_bhiv_configs": len(bhiv_configs),
                    "found_configs": len(found_configs),
                    "configs": found_configs
                }
            else:
                print("❌ .env.example file missing")
                self.results["deployment_config"]["details"]["env_config"] = "missing"

            # Check required directories
            required_dirs = [
                "backend/data/geometry_outputs",
                "backend/data/rl_feedback",
                "backend/data/alerts",
                "backend/data/reports",
                "backend/data/logs"
            ]

            existing_dirs = []
            for dir_path in required_dirs:
                if os.path.exists(dir_path):
                    existing_dirs.append(dir_path)

            self.results["deployment_config"]["details"]["directories"] = {
                "total": len(required_dirs),
                "existing": len(existing_dirs),
                "dirs": existing_dirs
            }

            if len(existing_dirs) > 0:
                print(f"✅ Data directories created ({len(existing_dirs)}/{len(required_dirs)})")
            else:
                print("⚠️  Data directories need to be created")

        except Exception as e:
            self.results["deployment_config"]["status"] = "error"
            self.results["deployment_config"]["details"] = {"exception": str(e)}
            print(f"❌ Deployment config test error: {e}")

    async def test_monitoring_logging(self):
        """Test structured logging & monitoring/alerts"""

        print("\n6. Testing Monitoring & Logging...")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test monitoring metrics endpoint
                response = await client.get(
                    f"{BASE_URL}/api/v1/monitoring/metrics",
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    metrics = response.json()
                    print("✅ Monitoring metrics endpoint working")
                    self.results["monitoring_logging"]["status"] = "success"
                    self.results["monitoring_logging"]["details"] = {
                        "metrics_status": metrics.get("status"),
                        "total_operations": metrics.get("metrics", {}).get("total_operations", 0),
                        "alerts_count": len(metrics.get("alerts", []))
                    }
                else:
                    print(f"❌ Monitoring metrics failed: {response.status_code}")
                    self.results["monitoring_logging"]["status"] = "failed"
                    self.results["monitoring_logging"]["details"] = {"error": response.text}

                # Test alert system
                response = await client.post(
                    f"{BASE_URL}/api/v1/monitoring/alert/test",
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    print("✅ Alert system working")
                    self.results["monitoring_logging"]["details"]["alert_system"] = "working"
                else:
                    print(f"⚠️  Alert system test failed: {response.status_code}")
                    self.results["monitoring_logging"]["details"]["alert_system"] = "failed"

            # Check log files
            log_dir = "backend/data/logs"
            if os.path.exists(log_dir):
                log_files = [f for f in os.listdir(log_dir) if f.endswith(('.log', '.jsonl'))]
                print(f"✅ Log directory exists with {len(log_files)} log files")
                self.results["monitoring_logging"]["details"]["log_files"] = len(log_files)
            else:
                print("⚠️  Log directory not found")
                self.results["monitoring_logging"]["details"]["log_files"] = 0

        except Exception as e:
            self.results["monitoring_logging"]["status"] = "error"
            self.results["monitoring_logging"]["details"] = {"exception": str(e)}
            print(f"❌ Monitoring & logging test error: {e}")

    def print_test_summary(self):
        """Print comprehensive test summary"""

        print("\n" + "=" * 60)
        print("🎯 BHIV MISSING FEATURES - TEST SUMMARY")
        print("=" * 60)

        total_features = len(self.results)
        successful_features = sum(1 for r in self.results.values() if r["status"] == "success")

        print(f"\n📊 Overall Status: {successful_features}/{total_features} features working")
        print(f"Success Rate: {(successful_features/total_features)*100:.1f}%")

        print("\n📋 Feature Status:")

        status_icons = {
            "success": "✅",
            "failed": "❌",
            "error": "💥",
            "pending": "⏳"
        }

        for feature, result in self.results.items():
            icon = status_icons.get(result["status"], "❓")
            print(f"{icon} {feature.replace('_', ' ').title()}: {result['status'].upper()}")

            # Show key details
            if result["details"]:
                for key, value in result["details"].items():
                    if isinstance(value, dict):
                        print(f"    {key}: {json.dumps(value, indent=6)}")
                    else:
                        print(f"    {key}: {value}")

        print("\n" + "=" * 60)

        if successful_features == total_features:
            print("🎉 ALL MISSING FEATURES IMPLEMENTED SUCCESSFULLY!")
        elif successful_features >= total_features * 0.8:
            print("🎯 MOST FEATURES WORKING - Minor issues to resolve")
        else:
            print("⚠️  SEVERAL FEATURES NEED ATTENTION")

        print("=" * 60)

        # Save results to file
        results_file = f"bhiv_feature_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_features": total_features,
                    "successful_features": successful_features,
                    "success_rate": (successful_features/total_features)*100
                },
                "results": self.results
            }, f, indent=2)

        print(f"📄 Detailed results saved to: {results_file}")


async def main():
    """Run all tests"""
    tester = BHIVFeatureTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
