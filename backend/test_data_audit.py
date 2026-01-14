"""
Test Data Audit & Storage Integrity System
Validates all audit endpoints and storage checks
"""
import json

import requests

BASE_URL = "http://localhost:8000"


def get_auth_token():
    """Get JWT token"""
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"username": "admin", "password": "bhiv2024"})
    if response.status_code == 200:
        return response.json()["access_token"]
    raise Exception(f"Login failed: {response.text}")


def test_audit_storage(token):
    """Test storage audit endpoint"""
    print("\n" + "=" * 70)
    print("🔍 Testing Storage Audit")
    print("=" * 70)

    response = requests.get(f"{BASE_URL}/audit/storage", headers={"Authorization": f"Bearer {token}"})

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Storage Audit Results:")
        for dir_path, info in data["storage_audit"].items():
            status = "✅" if info["exists"] else "❌"
            print(f"{status} {dir_path}: {info['file_count']} files, {info['total_size_mb']} MB")
        print(f"\nAudited by: {data['audited_by']}")
        print(f"Timestamp: {data['audit_timestamp']}")
    else:
        print(f"❌ Failed: {response.text}")

    return response.status_code == 200


def test_audit_integrity(token):
    """Test data integrity audit"""
    print("\n" + "=" * 70)
    print("🔍 Testing Data Integrity Audit")
    print("=" * 70)

    response = requests.get(f"{BASE_URL}/audit/integrity?limit=50", headers={"Authorization": f"Bearer {token}"})

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Integrity Audit Results:")
        print(f"Total specs audited: {data['total_specs_audited']}")
        print(f"Complete data: {data['specs_with_complete_data']}")
        print(f"Missing data: {data['specs_with_missing_data']}")
        print(f"\nIntegrity Score: {data['integrity_score']}%")
        print(f"Status: {data['status']}")

        print(f"\nMissing Artifacts:")
        for artifact, count in data["missing_artifacts"].items():
            if count > 0:
                print(f"  ❌ {artifact}: {count} specs")

        print(f"\nSpecs by Status:")
        for status, count in data["specs_by_status"].items():
            print(f"  • {status}: {count}")
    else:
        print(f"❌ Failed: {response.text}")

    return response.status_code == 200


def test_audit_spec(token, spec_id):
    """Test single spec audit"""
    print("\n" + "=" * 70)
    print(f"🔍 Testing Spec Audit: {spec_id}")
    print("=" * 70)

    response = requests.get(f"{BASE_URL}/audit/spec/{spec_id}", headers={"Authorization": f"Bearer {token}"})

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Spec Audit Results:")
        print(f"Spec ID: {data['spec_id']}")
        print(f"Completeness Score: {data['completeness_score']}%")
        print(f"Status: {data['status']}")

        print(f"\nDatabase:")
        for key, value in data["database"].items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")

        print(f"\nLocal Storage:")
        for key, info in data["local_storage"].items():
            if isinstance(info, dict):
                status = "✅" if info.get("exists") else "❌"
                print(f"  {status} {key}: {info}")

        print(f"\nArtifacts:")
        for key, value in data["artifacts"].items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")
    else:
        print(f"❌ Failed: {response.text}")

    return response.status_code == 200


def test_audit_user(token, user_id):
    """Test user data audit"""
    print("\n" + "=" * 70)
    print(f"🔍 Testing User Audit: {user_id}")
    print("=" * 70)

    response = requests.get(f"{BASE_URL}/audit/user/{user_id}", headers={"Authorization": f"Bearer {token}"})

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ User Audit Results:")

        if "summary" in data:
            summary = data["summary"]
            print(f"User ID: {summary['user_id']}")
            print(f"Total specs: {summary['total_specs']}")
            print(f"Specs with JSON: {summary['specs_with_json']}")
            print(f"Specs with preview: {summary['specs_with_preview']}")
            print(f"Specs with geometry: {summary['specs_with_geometry']}")
            print(f"Total iterations: {summary['total_iterations']}")
            print(f"Total evaluations: {summary['total_evaluations']}")
            print(f"Total compliance: {summary['total_compliance']}")
            print(f"\nStatus: {data['status']}")

            if data.get("specs"):
                print(f"\nFirst 3 specs:")
                for spec in data["specs"][:3]:
                    print(
                        f"  • {spec['spec_id']}: JSON={spec['has_json']}, Preview={spec['has_preview']}, Geometry={spec['has_geometry']}"
                    )
        else:
            print(f"Message: {data.get('message', 'No data')}")
    else:
        print(f"❌ Failed: {response.text}")

    return response.status_code == 200


def test_fix_spec(token, spec_id):
    """Test spec integrity fix"""
    print("\n" + "=" * 70)
    print(f"🔧 Testing Spec Fix: {spec_id}")
    print("=" * 70)

    response = requests.post(f"{BASE_URL}/audit/fix/{spec_id}", headers={"Authorization": f"Bearer {token}"})

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Fix Results:")
        print(f"Spec ID: {data['spec_id']}")
        print(f"Status: {data['status']}")
        print(f"Fixes applied: {data['fixed_count']}")

        if data["fixes_applied"]:
            print(f"\nFixes:")
            for fix in data["fixes_applied"]:
                print(f"  ✅ {fix}")
        else:
            print(f"\n✅ No fixes needed - spec is complete")
    else:
        print(f"❌ Failed: {response.text}")

    return response.status_code == 200


def get_sample_spec_id(token):
    """Get a sample spec ID for testing"""
    response = requests.get(f"{BASE_URL}/api/v1/history?limit=1", headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        data = response.json()
        if data.get("specs") and len(data["specs"]) > 0:
            return data["specs"][0]["spec_id"]
    return None


def main():
    print("\n" + "=" * 70)
    print("🚀 Data Audit & Storage Integrity Test Suite")
    print("=" * 70)

    try:
        # Get auth token
        print("\n🔐 Authenticating...")
        token = get_auth_token()
        print("✅ Authentication successful")

        # Test storage audit
        test_audit_storage(token)

        # Test data integrity audit
        test_audit_integrity(token)

        # Get sample spec for testing
        print("\n📋 Getting sample spec...")
        spec_id = get_sample_spec_id(token)

        if spec_id:
            print(f"✅ Found spec: {spec_id}")

            # Test spec audit
            test_audit_spec(token, spec_id)

            # Test spec fix
            test_fix_spec(token, spec_id)
        else:
            print("⚠️ No specs found for testing")

        # Test user audit (using admin user)
        test_audit_user(token, "admin")

        print("\n" + "=" * 70)
        print("✅ All Data Audit Tests Completed")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
