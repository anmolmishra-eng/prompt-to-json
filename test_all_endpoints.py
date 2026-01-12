"""
Comprehensive API Endpoint Testing Script
Tests all endpoints in the Design Engine API Backend
"""
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:8000"
TOKEN = None

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}{text.center(80)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_result(name: str, passed: bool, response_time: float = 0):
    status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
    print(f"{status} | {name:<60} | {response_time:.0f}ms")

def login() -> str:
    """Login and get JWT token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data={"username": "admin", "password": "bhiv2024"}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
    except:
        pass
    return None

def test_endpoint(method: str, endpoint: str, data: Dict = None, auth: bool = True) -> Tuple[bool, float, int]:
    """Test a single endpoint"""
    headers = {"Authorization": f"Bearer {TOKEN}"} if auth and TOKEN else {}
    headers["Content-Type"] = "application/json"

    start = time.time()
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=120)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers, timeout=120)
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}", headers=headers, timeout=120)

        elapsed = (time.time() - start) * 1000
        return response.status_code in [200, 201], elapsed, response.status_code
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return False, elapsed, 0

def main():
    global TOKEN

    print_header("DESIGN ENGINE API - COMPREHENSIVE ENDPOINT TEST")
    print(f"Base URL: {BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Login first
    print("Authenticating...")
    TOKEN = login()
    if TOKEN:
        print(f"{Colors.GREEN}Authentication successful{Colors.END}\n")
    else:
        print(f"{Colors.RED}Authentication failed - some tests may fail{Colors.END}\n")

    results = []

    # METRICS & HEALTH
    print_header("METRICS & HEALTH")
    tests = [
        ("GET", "/metrics", None, False),
        ("GET", "/health", None, False),
        ("GET", "/api/v1/", None, False),
        ("GET", "/api/v1/health", None, False),
        ("GET", "/api/v1/health/detailed", None, True),
        ("GET", "/api/v1/metrics", None, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # AUTHENTICATION & DATA PRIVACY
    print_header("AUTHENTICATION & DATA PRIVACY")
    tests = [
        ("POST", "/api/v1/auth/login", {"username": "admin", "password": "bhiv2024"}, False),
        ("GET", "/api/v1/data/test_user/export", None, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # MONITORING & ALERTS
    print_header("MONITORING & ALERTS")
    tests = [
        ("GET", "/api/v1/monitoring/metrics", None, True),
        ("POST", "/api/v1/monitoring/alert/test", {"message": "test"}, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # DESIGN GENERATION
    print_header("DESIGN GENERATION")
    design_data = {
        "user_id": "test_user",
        "prompt": "Modern 3BHK apartment with kitchen and living room",
        "project_id": "test_project_001"
    }
    tests = [
        ("POST", "/api/v1/generate", design_data, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # DESIGN EVALUATION
    print_header("DESIGN EVALUATION")
    eval_data = {
        "user_id": "test_user",
        "spec_id": "spec_test_001",
        "criteria": ["aesthetics", "functionality", "cost"]
    }
    tests = [
        ("POST", "/api/v1/evaluate", eval_data, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # DESIGN ITERATION & SWITCH
    print_header("DESIGN ITERATION & SWITCH")
    iterate_data = {
        "user_id": "test_user",
        "spec_id": "spec_test_001",
        "strategy": "auto_optimize"
    }
    switch_data = {
        "user_id": "test_user",
        "spec_id": "spec_test_001",
        "target": {"object_id": "cabinet_01"},
        "update": {"material": "oak"}
    }
    tests = [
        ("POST", "/api/v1/iterate", iterate_data, True),
        ("POST", "/api/v1/switch", switch_data, True),
        ("GET", "/api/v1/history", None, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # COMPLIANCE & VALIDATION
    print_header("COMPLIANCE & VALIDATION")
    compliance_data = {
        "project_id": "test_proj",
        "case_id": "test_case",
        "city": "Mumbai",
        "document": "DCPR_2034.pdf",
        "parameters": {"plot_size": 1000}
    }
    tests = [
        ("GET", "/api/v1/compliance/test", None, True),
        ("GET", "/api/v1/compliance/regulations", None, True),
        ("POST", "/api/v1/compliance/run_case", compliance_data, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # MCP INTEGRATION
    print_header("MCP INTEGRATION")
    mcp_data = {
        "design_id": "test_design",
        "city": "Mumbai",
        "regulations": ["IBC"]
    }
    tests = [
        ("GET", "/api/v1/mcp/cities", None, True),
        ("POST", "/api/v1/mcp/check", mcp_data, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # MULTI-CITY
    print_header("MULTI-CITY")
    tests = [
        ("GET", "/api/v1/cities/", None, True),
        ("GET", "/api/v1/cities/Mumbai/rules", None, True),
        ("GET", "/api/v1/cities/Mumbai/context", None, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # RL TRAINING
    print_header("RL TRAINING")
    rl_feedback = {
        "design_a_id": "design_a",
        "design_b_id": "design_b",
        "preference": "A"
    }
    rl_optimize = {
        "spec_json": {"design_id": "test"},
        "city": "Mumbai"
    }
    tests = [
        ("POST", "/api/v1/rl/feedback", rl_feedback, True),
        ("POST", "/api/v1/rl/optimize", rl_optimize, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # BHIV AI ASSISTANT
    print_header("BHIV AI ASSISTANT")
    bhiv_data = {
        "prompt": "Design a modern kitchen",
        "context": {}
    }
    tests = [
        ("GET", "/bhiv/v1/health", None, False),
        ("POST", "/bhiv/v1/prompt", bhiv_data, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # BHIV AUTOMATIONS
    print_header("BHIV AUTOMATIONS")
    tests = [
        ("GET", "/api/v1/automation/status", None, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # MOBILE API
    print_header("MOBILE API")
    mobile_data = {
        "user_id": "test_user",
        "prompt": "Modern bedroom with wardrobe",
        "device_id": "test_device",
        "project_id": "mobile_test_001"
    }
    tests = [
        ("GET", "/api/v1/mobile/health", None, True),
        ("POST", "/api/v1/mobile/generate", mobile_data, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # VR API
    print_header("VR API")
    tests = [
        ("GET", "/api/v1/vr/preview/test_spec", None, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # INTEGRATION LAYER
    print_header("INTEGRATION LAYER")
    tests = [
        ("GET", "/api/v1/integration/dependencies/map", None, True),
        ("GET", "/api/v1/integration/separation/validate", None, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # WORKFLOW CONSOLIDATION
    print_header("WORKFLOW CONSOLIDATION")
    tests = [
        ("GET", "/api/v1/workflows/monitoring/health", None, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # MULTI-CITY TESTING
    print_header("MULTI-CITY TESTING")
    tests = [
        ("GET", "/api/v1/multi-city/datasets/validate", None, True),
        ("POST", "/api/v1/multi-city/test/case/pune_001_dcr", None, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # GEOMETRY GENERATION
    print_header("GEOMETRY GENERATION")
    geom_data = {
        "spec_json": {"design_id": "test", "floors": 3},
        "request_id": "test_geom_001",
        "format": "glb"
    }
    tests = [
        ("GET", "/api/v1/geometry/list", None, True),
        ("POST", "/api/v1/geometry/generate", geom_data, True),
    ]
    for method, endpoint, data, auth in tests:
        passed, elapsed, status = test_endpoint(method, endpoint, data, auth)
        results.append((endpoint, passed))
        print_result(f"{method} {endpoint}", passed, elapsed)

    # Summary
    print_header("TEST SUMMARY")
    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"Total Endpoints Tested: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}")
    print(f"Success Rate: {success_rate:.1f}%")

    if failed > 0:
        print(f"\n{Colors.YELLOW}Failed Endpoints:{Colors.END}")
        for endpoint, passed in results:
            if not passed:
                print(f"  - {endpoint}")

    print(f"\n{Colors.BLUE}Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")

    return success_rate == 100.0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
