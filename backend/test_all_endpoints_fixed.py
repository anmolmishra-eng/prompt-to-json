#!/usr/bin/env python3
"""
Comprehensive API Test Script
Tests all 58 endpoints of the Design Engine API
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

import httpx

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {"username": "admin", "password": "bhiv2024"}
TIMEOUT = 30.0


class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        self.results = []
        self.spec_id = None

    async def authenticate(self):
        """Get JWT token for authenticated endpoints"""
        try:
            # Try JSON format first
            response = await self.client.post(f"{self.base_url}/api/v1/auth/login", json=TEST_USER)

            if response.status_code != 200:
                # Try form data format
                response = await self.client.post(f"{self.base_url}/api/v1/auth/login", data=TEST_USER)

            if response.status_code == 200:
                result = response.json()
                self.token = result.get("access_token") or result.get("token")
                print("Authentication successful")
                return True
            else:
                print(f"Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def get_headers(self, auth_required=True):
        """Get headers with optional authentication"""
        headers = {"Content-Type": "application/json"}
        if auth_required and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def test_endpoint(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        auth_required: bool = True,
        expected_codes: List[int] = [200, 201],
    ):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers(auth_required)

        try:
            start_time = time.time()

            if method.upper() == "GET":
                response = await self.client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await self.client.post(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            duration = round((time.time() - start_time) * 1000, 2)

            # Determine result
            success = response.status_code in expected_codes
            status_icon = "PASS" if success else "FAIL"

            result = {
                "endpoint": endpoint,
                "method": method.upper(),
                "status_code": response.status_code,
                "success": success,
                "duration_ms": duration,
                "response_size": len(response.content),
                "timestamp": datetime.now().isoformat(),
            }

            # Store spec_id from generate endpoint for later use
            if endpoint == "/api/v1/generate" and success:
                try:
                    resp_data = response.json()
                    self.spec_id = resp_data.get("spec_id")
                except:
                    pass

            self.results.append(result)

            print(f"{status_icon} {method.upper()} {endpoint} -> {response.status_code} ({duration}ms)")

            return result

        except Exception as e:
            error_result = {
                "endpoint": endpoint,
                "method": method.upper(),
                "status_code": 0,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            self.results.append(error_result)
            print(f"FAIL {method.upper()} {endpoint} -> ERROR: {e}")
            return error_result

    async def run_all_tests(self):
        """Run all 58 endpoint tests"""
        print("Starting comprehensive API test suite...")
        print("=" * 60)

        # Authenticate first
        if not await self.authenticate():
            print("Cannot proceed without authentication")
            return

        print("\nTesting Public Endpoints (No Auth Required)")
        print("-" * 40)

        # 1. Public Health Endpoints (2 endpoints)
        await self.test_endpoint("GET", "/metrics", auth_required=False)
        await self.test_endpoint("GET", "/health", auth_required=False)

        print("\nTesting Authentication Endpoints")
        print("-" * 40)

        # 2. Authentication Endpoints (2 endpoints)
        await self.test_endpoint("POST", "/api/v1/auth/login", data=TEST_USER, auth_required=False)
        await self.test_endpoint("POST", "/api/v1/auth/refresh")

        print("\nTesting Data Privacy Endpoints")
        print("-" * 40)

        # 3. Data Privacy Endpoints (2 endpoints)
        await self.test_endpoint("GET", "/api/v1/data/user123/export")
        await self.test_endpoint("DELETE", "/api/v1/data/user123")

        print("\nTesting System Health Endpoints")
        print("-" * 40)

        # 4. System Health Endpoints (5 endpoints)
        await self.test_endpoint("GET", "/api/v1/")
        await self.test_endpoint("GET", "/api/v1/health")
        await self.test_endpoint("GET", "/api/v1/health/detailed")
        await self.test_endpoint("GET", "/api/v1/metrics")
        await self.test_endpoint("GET", "/api/v1/test-error")

        print("\nTesting Monitoring & Alerts")
        print("-" * 40)

        # 5. Monitoring Endpoints (2 endpoints)
        await self.test_endpoint("GET", "/api/v1/monitoring/metrics")
        await self.test_endpoint("POST", "/api/v1/monitoring/alert/test")

        print("\nTesting Design Generation")
        print("-" * 40)

        # 6. Design Generation Endpoints (2 endpoints)
        generate_data = {
            "user_id": "test_user",
            "prompt": "Design a modern kitchen with island",
            "city": "Mumbai",
            "style": "modern",
        }
        await self.test_endpoint("POST", "/api/v1/generate", data=generate_data)
        await self.test_endpoint("GET", "/api/v1/specs/test_spec_123")

        print("\nTesting Design Evaluation")
        print("-" * 40)

        # 7. Design Evaluation (1 endpoint)
        evaluate_data = {
            "spec_id": self.spec_id or "test_spec",
            "user_id": "test_user",
            "rating": 5,
            "notes": "Great design",
        }
        await self.test_endpoint("POST", "/api/v1/evaluate", data=evaluate_data)

        print("\nTesting Design Iteration")
        print("-" * 40)

        # 8. Design Iteration (1 endpoint)
        iterate_data = {"spec_id": self.spec_id or "test_spec", "strategy": "improve_materials", "user_id": "test_user"}
        await self.test_endpoint("POST", "/api/v1/iterate", data=iterate_data)

        print("\nTesting Material Switch")
        print("-" * 40)

        # 9. Material Switch (1 endpoint)
        switch_data = {"spec_id": self.spec_id or "test_spec", "query": "change floor to marble"}
        await self.test_endpoint("POST", "/api/v1/switch", data=switch_data)

        print("\nTesting Design History")
        print("-" * 40)

        # 10. Design History (2 endpoints)
        await self.test_endpoint("GET", f"/api/v1/history/{self.spec_id or 'test_spec'}")
        await self.test_endpoint("GET", "/api/v1/history")

        print("\nTesting Compliance & Validation")
        print("-" * 40)

        # 11. Compliance Endpoints (7 endpoints)
        await self.test_endpoint("GET", "/api/v1/compliance/test")

        compliance_case = {
            "city": "Mumbai",
            "project_id": "test_project",
            "parameters": {"plot_size": 1000, "location": "urban"},
        }
        await self.test_endpoint("POST", "/api/v1/compliance/run_case", data=compliance_case)

        feedback_data = {"project_id": "test_project", "case_id": "test_case", "user_feedback": "up"}
        await self.test_endpoint("POST", "/api/v1/compliance/feedback", data=feedback_data)

        pdf_data = {"pdf_url": "https://example.com/rules.pdf", "city": "Mumbai"}
        await self.test_endpoint("POST", "/api/v1/compliance/ingest_pdf", data=pdf_data)

        await self.test_endpoint("GET", "/api/v1/compliance/workflow_status")
        await self.test_endpoint("GET", "/api/v1/compliance/regulations")

        compliance_check = {"spec_id": self.spec_id or "test_spec", "user_id": "test_user"}
        await self.test_endpoint("POST", "/api/v1/compliance/check", data=compliance_check)

        print("\nTesting MCP Integration")
        print("-" * 40)

        # 12. MCP Integration (3 endpoints)
        mcp_data = {"city": "Mumbai", "spec_json": {"design_type": "kitchen"}, "case_type": "full"}
        await self.test_endpoint("POST", "/api/v1/mcp/check", data=mcp_data)
        await self.test_endpoint("GET", "/api/v1/mcp/cities")

        mcp_feedback = {"case_id": "test_case", "feedback": "Good analysis", "rating": 4.5}
        await self.test_endpoint("POST", "/api/v1/mcp/feedback", data=mcp_feedback)

        print("\nTesting Multi-City Support")
        print("-" * 40)

        # 13. Multi-City Endpoints (4 endpoints)
        await self.test_endpoint("GET", "/api/v1/cities/")
        await self.test_endpoint("GET", "/api/v1/cities/Mumbai/rules")
        await self.test_endpoint("GET", "/api/v1/cities/Mumbai/context")

        # City RL feedback expects query parameters, not JSON body
        await self.test_endpoint(
            "POST",
            "/api/v1/rl/feedback/city?city=Mumbai&design_spec={}&user_rating=4.5&compliance_result={}",
            expected_codes=[422, 400],
        )

        print("\nTesting BHIV AI Assistant")
        print("-" * 40)

        # 14. BHIV AI Assistant (5 endpoints)
        bhiv_prompt_data = {"user_id": "test_user", "prompt": "Design a modern office space", "city": "Mumbai"}
        await self.test_endpoint("POST", "/bhiv/v1/prompt", data=bhiv_prompt_data)

        bhiv_feedback_data = {
            "request_id": "test_req",
            "spec_id": self.spec_id or "test_spec",
            "user_id": "test_user",
            "rating": 4.5,
        }
        await self.test_endpoint("POST", "/bhiv/v1/feedback", data=bhiv_feedback_data)
        await self.test_endpoint("GET", "/bhiv/v1/health")

        bhiv_design_data = {"user_id": "test_user", "prompt": "Create a modern living room", "city": "Mumbai"}
        await self.test_endpoint("POST", "/bhiv/v1/design", data=bhiv_design_data)
        await self.test_endpoint("POST", "/bhiv/v1/process_with_workflow", data=bhiv_design_data)

        print("\nTesting BHIV Automations")
        print("-" * 40)

        # 15. BHIV Automations (4 endpoints)
        await self.test_endpoint("GET", "/api/v1/automation/status")

        pdf_compliance_data = {"pdf_url": "https://example.com/compliance.pdf", "city": "Mumbai"}
        await self.test_endpoint("POST", "/api/v1/automation/pdf-compliance", data=pdf_compliance_data)

        workflow_data = {"workflow_type": "compliance_check", "parameters": {"city": "Mumbai"}}
        await self.test_endpoint("POST", "/api/v1/automation/workflow", data=workflow_data)
        await self.test_endpoint("GET", "/api/v1/automation/workflow/test_flow_123/status")

        print("\nTesting File Management")
        print("-" * 40)

        # 16. File Management (6 endpoints)
        await self.test_endpoint("GET", f"/api/v1/reports/{self.spec_id or 'test_spec'}")

        report_data = {"spec_id": self.spec_id or "test_spec", "report_type": "compliance"}
        await self.test_endpoint("POST", "/api/v1/reports", data=report_data)

        # File upload endpoints (expecting multipart/form-data, will get 422)
        await self.test_endpoint("POST", "/api/v1/upload", expected_codes=[422, 400])
        await self.test_endpoint("POST", "/api/v1/upload-preview", expected_codes=[422, 400])
        await self.test_endpoint("POST", "/api/v1/upload-geometry", expected_codes=[422, 400])
        await self.test_endpoint("POST", "/api/v1/upload-compliance", expected_codes=[422, 400])

        print("\nTesting RL Training")
        print("-" * 40)

        # 17. RL Training (6 endpoints)
        rl_feedback_data = {
            "design_a_id": "design_a",
            "design_b_id": "design_b",
            "preference": "A",
            "reason": "Better layout",
        }
        await self.test_endpoint("POST", "/api/v1/rl/feedback", data=rl_feedback_data)
        await self.test_endpoint("GET", "/api/v1/rl/feedback/city/Mumbai/summary")

        rlhf_data = {"dataset_id": "test_dataset", "model_config": {"learning_rate": 0.001}}
        await self.test_endpoint("POST", "/api/v1/rl/train/rlhf", data=rlhf_data)
        await self.test_endpoint("POST", "/api/v1/rl/train/opt", data=rlhf_data)

        rl_optimize_data = {"spec_json": {"design_type": "kitchen"}, "optimization_target": "cost"}
        await self.test_endpoint("POST", "/api/v1/rl/optimize", data=rl_optimize_data)

        suggest_data = {"spec_id": self.spec_id or "test_spec", "current_iteration": 1}
        await self.test_endpoint("POST", "/api/v1/rl/suggest/iterate", data=suggest_data)

        print("\nTesting Geometry Generation")
        print("-" * 40)

        # 18. Geometry Generation (3 endpoints)
        geometry_data = {
            "spec_json": {"design_type": "kitchen", "objects": []},
            "request_id": "test_geo_123",
            "format": "glb",
        }
        await self.test_endpoint("POST", "/api/v1/geometry/generate", data=geometry_data)
        await self.test_endpoint("GET", "/api/v1/geometry/download/test_file.glb")
        await self.test_endpoint("GET", "/api/v1/geometry/list")

        print("\n" + "=" * 60)
        await self.generate_report()

    async def generate_report(self):
        """Generate test summary report"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - successful_tests

        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"\nTEST SUMMARY REPORT")
        print("=" * 60)
        print(f"Total Endpoints Tested: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")

        if failed_tests > 0:
            print(f"\nFailed Endpoints:")
            for result in self.results:
                if not result["success"]:
                    error_info = result.get("error", f"Status {result['status_code']}")
                    print(f"   • {result['method']} {result['endpoint']} - {error_info}")

        # Save detailed report
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "test_timestamp": datetime.now().isoformat(),
            },
            "results": self.results,
        }

        with open("api_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\nDetailed report saved to: api_test_report.json")
        print("=" * 60)

    async def cleanup(self):
        """Cleanup resources"""
        await self.client.aclose()


async def main():
    """Main test runner"""
    tester = APITester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    print("Design Engine API - Comprehensive Test Suite")
    print("Testing all 58 endpoints...")
    print()

    asyncio.run(main())
