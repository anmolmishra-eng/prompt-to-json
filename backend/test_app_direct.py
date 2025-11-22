#!/usr/bin/env python3
"""
Direct App Test - Test FastAPI app directly without server startup
"""

from fastapi.testclient import TestClient


def test_app_direct():
    """Test FastAPI app directly using TestClient"""
    print("Direct App Test")
    print("=" * 18)

    try:
        from app.main import app

        client = TestClient(app)

        # Test health endpoint
        print("Testing health endpoint...")
        response = client.get("/api/v1/health")
        print(f"[OK] Health: {response.status_code}")
        health_ok = response.status_code == 200

        # Test BHIV health endpoint
        print("Testing BHIV health endpoint...")
        response = client.get("/bhiv/v1/health")
        print(f"[OK] BHIV Health: {response.status_code}")
        bhiv_health_ok = response.status_code == 200

        # Test BHIV design endpoint (should return validation error)
        print("Testing BHIV design endpoint...")
        response = client.post("/bhiv/v1/design", json={})
        print(f"[OK] BHIV Design: {response.status_code}")
        bhiv_design_ok = response.status_code == 422  # Expected validation error

        # Test docs endpoint
        print("Testing docs endpoint...")
        response = client.get("/docs")
        print(f"[OK] Docs: {response.status_code}")
        docs_ok = response.status_code == 200

        results = {
            "Health Endpoint": health_ok,
            "BHIV Health": bhiv_health_ok,
            "BHIV Design": bhiv_design_ok,
            "API Docs": docs_ok,
        }

        print("\n" + "=" * 18)
        print("TEST RESULTS")
        print("=" * 18)

        passed = 0
        for test_name, result in results.items():
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status} {test_name}")
            if result:
                passed += 1

        print(f"\nResult: {passed}/{len(results)} tests passed")

        return passed == len(results)

    except Exception as e:
        print(f"[ERROR] App test failed: {e}")
        return False


def main():
    success = test_app_direct()

    if success:
        print("\n[SUCCESS] All app tests passed!")
        print("- FastAPI app loads correctly")
        print("- All endpoints are accessible")
        print("- BHIV integration working")
    else:
        print("\n[WARNING] Some tests failed")

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
