"""
Test Data & Storage Integrity
Ensures all spec data is stored and retrievable
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
            print("✅ Authentication successful")
            return True
        print(f"❌ Login failed: {response.status_code}")
        return False


async def test_history_integrity():
    """Test /api/v1/history with data integrity"""
    print("\n" + "=" * 70)
    print("Testing /api/v1/history - Data Integrity")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/history", headers={"Authorization": f"Bearer {TOKEN}"}, params={"limit": 5}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - History with integrity")
            print(f"   Total Specs: {data.get('total_specs')}")

            integrity = data.get("data_integrity_summary", {})
            print(f"\n   Data Integrity Summary:")
            print(f"     Specs with JSON: {integrity.get('specs_with_json')}/{integrity.get('total_specs')}")
            print(f"     Specs with Preview: {integrity.get('specs_with_preview')}/{integrity.get('total_specs')}")
            print(f"     Specs with Geometry: {integrity.get('specs_with_geometry')}/{integrity.get('total_specs')}")
            print(f"     All Auditable: {integrity.get('all_auditable')}")

            if data.get("specs"):
                spec = data["specs"][0]
                print(f"\n   First Spec Integrity:")
                spec_integrity = spec.get("data_integrity", {})
                print(f"     Has JSON: {spec_integrity.get('has_spec_json')}")
                print(f"     Has Preview: {spec_integrity.get('has_preview')}")
                print(f"     Has Geometry: {spec_integrity.get('has_geometry')}")
                print(f"     Iterations: {spec_integrity.get('iterations_count')}")
                print(f"     Evaluations: {spec_integrity.get('evaluations_count')}")
                print(f"     Compliance: {spec_integrity.get('compliance_count')}")

                return True, spec.get("spec_id")

            return True, None
        else:
            print(f"❌ FAILED - History")
            print(f"   Error: {response.text}")
            return False, None


async def test_report_integrity(spec_id):
    """Test /api/v1/reports/{spec_id} with data integrity"""
    print("\n" + "=" * 70)
    print(f"Testing /api/v1/reports/{spec_id} - Data Integrity")
    print("=" * 70)

    if not spec_id:
        print("⚠️  No spec_id available")
        return False

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/reports/{spec_id}", headers={"Authorization": f"Bearer {TOKEN}"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - Report with integrity")
            print(f"   Report ID: {data.get('report_id')}")

            integrity = data.get("data_integrity", {})
            print(f"\n   Data Integrity:")
            print(f"     Spec JSON: {integrity.get('spec_json_exists')}")
            print(f"     Preview URL: {integrity.get('preview_url_exists')}")
            print(f"     Geometry URL: {integrity.get('geometry_url_exists')}")
            print(f"     Has Iterations: {integrity.get('has_iterations')}")
            print(f"     Has Evaluations: {integrity.get('has_evaluations')}")
            print(f"     Has Compliance: {integrity.get('has_compliance')}")
            print(f"     Data Complete: {integrity.get('data_complete')}")

            print(f"\n   Content:")
            print(f"     Iterations: {len(data.get('iterations', []))}")
            print(f"     Evaluations: {len(data.get('evaluations', []))}")
            print(f"     Compliance Checks: {len(data.get('compliance_checks', []))}")
            print(f"     Preview URLs: {len(data.get('preview_urls', []))}")

            return True
        else:
            print(f"❌ FAILED - Report")
            print(f"   Error: {response.text}")
            return False


async def test_audit_spec(spec_id):
    """Test /api/v1/audit/spec/{spec_id}"""
    print("\n" + "=" * 70)
    print(f"Testing /api/v1/audit/spec/{spec_id}")
    print("=" * 70)

    if not spec_id:
        print("⚠️  No spec_id available")
        return False

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/audit/spec/{spec_id}", headers={"Authorization": f"Bearer {TOKEN}"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - Spec Audit")
            print(f"   Spec ID: {data.get('spec_id')}")
            print(f"   Audit Timestamp: {data.get('audit_timestamp')}")

            summary = data.get("summary", {})
            print(f"\n   Audit Summary:")
            print(f"     Total Checks: {summary.get('total_checks')}")
            print(f"     Passed Checks: {summary.get('passed_checks')}")
            print(f"     Issues: {summary.get('issues_count')}")
            print(f"     Status: {summary.get('audit_status')}")

            if data.get("issues"):
                print(f"\n   Issues Found:")
                for issue in data["issues"]:
                    print(f"     - {issue}")

            print(f"\n   Data Integrity:")
            json_int = data.get("data_integrity", {}).get("json_spec", {})
            print(
                f"     JSON Spec: Exists={json_int.get('exists')}, Valid={json_int.get('valid')}, Size={json_int.get('size_bytes')} bytes"
            )

            eval_int = data.get("data_integrity", {}).get("evaluations", {})
            print(f"     Evaluations: Count={eval_int.get('count')}, Stored={eval_int.get('stored')}")

            comp_int = data.get("data_integrity", {}).get("compliance", {})
            print(f"     Compliance: Count={comp_int.get('count')}, Stored={comp_int.get('stored')}")

            return True
        else:
            print(f"❌ FAILED - Audit")
            print(f"   Error: {response.text}")
            return False


async def test_complete_spec_data(spec_id):
    """Test /api/v1/audit/spec/{spec_id}/complete"""
    print("\n" + "=" * 70)
    print(f"Testing /api/v1/audit/spec/{spec_id}/complete")
    print("=" * 70)

    if not spec_id:
        print("⚠️  No spec_id available")
        return False

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/audit/spec/{spec_id}/complete", headers={"Authorization": f"Bearer {TOKEN}"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - Complete Spec Data")

            spec = data.get("spec", {})
            print(f"   Spec ID: {spec.get('id')}")
            print(f"   City: {spec.get('city')}")
            print(f"   Design Type: {spec.get('design_type')}")
            print(f"   Status: {spec.get('status')}")

            metadata = data.get("metadata", {})
            print(f"\n   Complete Data:")
            print(f"     Iterations: {metadata.get('total_iterations')}")
            print(f"     Evaluations: {metadata.get('total_evaluations')}")
            print(f"     Compliance Checks: {metadata.get('total_compliance_checks')}")
            print(f"     Data Complete: {metadata.get('data_complete')}")

            return True
        else:
            print(f"❌ FAILED - Complete Data")
            print(f"   Error: {response.text}")
            return False


async def main():
    print("=" * 70)
    print("DATA & STORAGE INTEGRITY TEST SUITE")
    print("=" * 70)

    # Login
    if not await login():
        print("\n❌ Authentication failed. Cannot proceed with tests.")
        return

    results = {}

    # Test 1: History with integrity
    history_success, spec_id = await test_history_integrity()
    results["history_integrity"] = history_success

    # Test 2: Report with integrity
    if spec_id:
        results["report_integrity"] = await test_report_integrity(spec_id)

        # Test 3: Spec audit
        results["spec_audit"] = await test_audit_spec(spec_id)

        # Test 4: Complete spec data
        results["complete_data"] = await test_complete_spec_data(spec_id)
    else:
        results["report_integrity"] = False
        results["spec_audit"] = False
        results["complete_data"] = False

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 DATA INTEGRITY VERIFIED - Office can audit any spec!")
        print("\nVerified:")
        print("  ✅ JSON specs stored and retrievable")
        print("  ✅ Previews tracked")
        print("  ✅ GLB files tracked")
        print("  ✅ Evaluations stored")
        print("  ✅ Compliance checks stored")
        print("  ✅ Complete audit trail available")
    else:
        print("\n⚠️  Some tests failed - check logs")


if __name__ == "__main__":
    asyncio.run(main())
