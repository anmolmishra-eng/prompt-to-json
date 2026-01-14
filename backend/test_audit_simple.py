"""Test Data Audit System"""
import requests

BASE_URL = "http://localhost:8000"


def get_token():
    r = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={"username": "admin", "password": "bhiv2024"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if r.status_code != 200:
        print(f"Login failed: {r.status_code} - {r.text}")
        raise Exception("Authentication failed")
    data = r.json()
    return data.get("access_token") or data.get("token")


def test_storage(token):
    print("\n" + "=" * 70)
    print("TEST: Storage Audit")
    print("=" * 70)
    r = requests.get(f"{BASE_URL}/audit/storage", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        for path, info in data["storage_audit"].items():
            print(f"  {path}: {info['file_count']} files, {info['total_size_mb']} MB")
    return r.status_code == 200


def test_integrity(token):
    print("\n" + "=" * 70)
    print("TEST: Data Integrity")
    print("=" * 70)
    r = requests.get(f"{BASE_URL}/audit/integrity?limit=50", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Total specs: {data['total_specs_audited']}")
        print(f"  Complete: {data['specs_with_complete_data']}")
        print(f"  Integrity Score: {data['integrity_score']}%")
        print(f"  Status: {data['status']}")
    return r.status_code == 200


def test_spec(token, spec_id):
    print("\n" + "=" * 70)
    print(f"TEST: Spec Audit - {spec_id}")
    print("=" * 70)
    r = requests.get(f"{BASE_URL}/audit/spec/{spec_id}", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Completeness: {data['completeness_score']}%")
        print(f"  Status: {data['status']}")
        print(f"  Database: {data['database']}")
    return r.status_code == 200


def get_spec_id(token):
    r = requests.get(f"{BASE_URL}/api/v1/history?limit=1", headers={"Authorization": f"Bearer {token}"})
    if r.status_code == 200:
        data = r.json()
        if data.get("specs"):
            return data["specs"][0]["spec_id"]
    return None


print("\n" + "=" * 70)
print("DATA AUDIT TEST SUITE")
print("=" * 70)

try:
    print("\nAuthenticating...")
    token = get_token()
    print("OK - Authenticated")

    test_storage(token)
    test_integrity(token)

    spec_id = get_spec_id(token)
    if spec_id:
        print(f"\nFound spec: {spec_id}")
        test_spec(token, spec_id)

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback

    traceback.print_exc()
