"""
Smoke tests for deployment validation
Quick tests to verify basic functionality
"""

import asyncio
import sys
from pathlib import Path

import httpx

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.multi_city.city_data_loader import City


async def run_smoke_tests():
    """Run basic smoke tests"""

    base_url = "http://localhost"
    results = []

    print("Running Smoke Tests...")
    print("=" * 40)

    async with httpx.AsyncClient() as client:
        # Test 1: Health endpoint
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✓ Health check: PASS")
                results.append(True)
            else:
                print("✗ Health check: FAIL")
                results.append(False)
        except Exception as e:
            print(f"✗ Health check: ERROR - {e}")
            results.append(False)

        # Test 2: API documentation
        try:
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("✓ API docs: PASS")
                results.append(True)
            else:
                print("✗ API docs: FAIL")
                results.append(False)
        except Exception as e:
            print(f"✗ API docs: ERROR - {e}")
            results.append(False)

        # Test 3: Cities list
        try:
            response = await client.get(f"{base_url}/api/v1/cities/")
            if response.status_code == 200:
                data = response.json()
                if data.get("count") == 4:
                    print("✓ Cities list: PASS")
                    results.append(True)
                else:
                    print("✗ Cities list: FAIL (wrong count)")
                    results.append(False)
            else:
                print("✗ Cities list: FAIL")
                results.append(False)
        except Exception as e:
            print(f"✗ Cities list: ERROR - {e}")
            results.append(False)

        # Test 4: Sample city rules
        try:
            response = await client.get(f"{base_url}/api/v1/cities/Mumbai/rules")
            if response.status_code == 200:
                data = response.json()
                if data.get("fsi_base") == 1.33:
                    print("✓ Mumbai rules: PASS")
                    results.append(True)
                else:
                    print("✗ Mumbai rules: FAIL (wrong data)")
                    results.append(False)
            else:
                print("✗ Mumbai rules: FAIL")
                results.append(False)
        except Exception as e:
            print(f"✗ Mumbai rules: ERROR - {e}")
            results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)

    print("\n" + "=" * 40)
    print(f"Smoke Tests: {passed}/{total} passed")

    if passed == total:
        print("✓ All smoke tests PASSED")
        return True
    else:
        print("✗ Some smoke tests FAILED")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_smoke_tests())
    sys.exit(0 if success else 1)
