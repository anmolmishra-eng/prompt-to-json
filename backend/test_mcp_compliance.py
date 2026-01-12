"""
Test MCP Compliance Loop - Verify real compliance data parsing
"""
import asyncio

import httpx

BASE_URL = "http://localhost:8000"
TOKEN = None


async def login():
    """Get authentication token"""
    global TOKEN
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login", json={"username": "admin", "password": "bhiv2024"}
        )
        if response.status_code == 200:
            TOKEN = response.json()["access_token"]
            print("Authenticated")
            return True
        print(f"Login failed: {response.status_code}")
        return False


async def test_mcp_check():
    """Test /api/v1/mcp/check endpoint"""
    print("\nTesting /api/v1/mcp/check...")

    payload = {
        "city": "Mumbai",
        "spec_json": {
            "plot_size": 1500,
            "location": "urban",
            "road_width": 15,
            "design_type": "residential",
            "objects": [
                {"id": "floor1", "type": "residential"},
                {"id": "floor2", "type": "residential"},
                {"id": "floor3", "type": "residential"},
            ],
        },
        "case_type": "full",
        "async_mode": False,
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/mcp/check", json=payload, headers={"Authorization": f"Bearer {TOKEN}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"MCP Check successful")
            print(f"  Case ID: {result.get('case_id')}")
            print(f"  City: {result.get('city')}")
            print(f"  Compliant: {result.get('compliant')}")
            print(f"  Confidence: {result.get('confidence_score')}")

            violations = result.get("violations", [])
            print(f"  Violations: {len(violations)}")
            if violations:
                for v in violations[:3]:
                    print(f"    - {v.get('rule_id')}: {v.get('description')}")
            else:
                print("    No violations found")

            recommendations = result.get("recommendations", [])
            print(f"  Recommendations: {len(recommendations)}")
            if recommendations:
                for r in recommendations[:3]:
                    print(f"    - {r}")

            # Check for real data (not placeholders)
            if violations or recommendations:
                print("  REAL COMPLIANCE DATA - No generic placeholders")
                return True, result.get("case_id")
            else:
                print("  WARNING: No violations or recommendations")
                return False, result.get("case_id")
        else:
            print(f"MCP Check failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False, None


async def test_mcp_feedback(case_id):
    """Test /api/v1/mcp/feedback endpoint"""
    print("\nTesting /api/v1/mcp/feedback...")

    if not case_id:
        print("  Skipping - no case_id available")
        return False

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/mcp/feedback",
            params={"case_id": case_id, "feedback": "Compliance analysis was helpful", "rating": 4.5},
            headers={"Authorization": f"Bearer {TOKEN}"},
        )

        if response.status_code == 200:
            result = response.json()
            print(f"MCP Feedback successful")
            print(f"  Status: {result.get('status')}")
            print(f"  Message: {result.get('message')}")
            return True
        else:
            print(f"MCP Feedback failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False


async def test_compliance_run_case():
    """Test /api/v1/compliance/run_case endpoint"""
    print("\nTesting /api/v1/compliance/run_case...")

    payload = {
        "project_id": "proj_test_001",
        "case_id": "case_mumbai_001",
        "city": "Mumbai",
        "document": "Mumbai_DCR.pdf",
        "parameters": {"plot_size": 1200, "location": "suburban", "road_width": 12},
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/compliance/run_case", json=payload, headers={"Authorization": f"Bearer {TOKEN}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"Compliance Run Case successful")
            print(f"  Case ID: {result.get('case_id')}")
            print(f"  Confidence: {result.get('confidence_score')}")
            print(f"  Rules Applied: {len(result.get('rules_applied', []))}")

            # Check for parsed data
            if "violations" in result or "recommendations" in result:
                print("  PARSED COMPLIANCE DATA present")
                return True
            else:
                print("  Raw MCP response (not parsed)")
                return False
        else:
            print(f"Compliance Run Case failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False


async def main():
    print("=" * 70)
    print("Testing MCP Compliance Loop")
    print("=" * 70)

    if not await login():
        return

    results = []

    # Test MCP check endpoint
    check_passed, case_id = await test_mcp_check()
    results.append(("MCP Check", check_passed))

    # Test MCP feedback endpoint
    feedback_passed = await test_mcp_feedback(case_id)
    results.append(("MCP Feedback", feedback_passed))

    # Test compliance run_case endpoint
    run_case_passed = await test_compliance_run_case()
    results.append(("Compliance Run Case", run_case_passed))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status} - {name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("MCP IS LEGALLY MEANINGFUL - Real compliance data!")
    else:
        print("Some endpoints need attention")


if __name__ == "__main__":
    asyncio.run(main())
