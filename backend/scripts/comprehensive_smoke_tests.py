"""
Comprehensive smoke tests for deployment validation
Tests all critical system components
"""

import asyncio
import sys
from pathlib import Path

import httpx

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.multi_city.city_data_loader import City


async def run_comprehensive_smoke_tests():
    """Run comprehensive smoke tests"""

    tests_passed = 0
    tests_failed = 0
    base_url = "http://localhost"

    print("Running Comprehensive Smoke Tests...")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Test 1: System Health
        try:
            response = await client.get(f"{base_url}/api/v1/health", timeout=10.0)
            if response.status_code == 200:
                print("PASS - Test 1: System Health")
                tests_passed += 1
            else:
                print(f"FAIL - Test 1: System Health (status={response.status_code})")
                tests_failed += 1
        except Exception as e:
            print(f"ERROR - Test 1: System Health: {e}")
            tests_failed += 1

        # Test 2: API Documentation
        try:
            response = await client.get(f"{base_url}/docs", timeout=10.0)
            if response.status_code == 200:
                print("PASS - Test 2: API Documentation")
                tests_passed += 1
            else:
                print(f"FAIL - Test 2: API Documentation (status={response.status_code})")
                tests_failed += 1
        except Exception as e:
            print(f"ERROR - Test 2: API Documentation: {e}")
            tests_failed += 1

        # Test 3: Cities List Endpoint
        try:
            response = await client.get(f"{base_url}/api/v1/cities/", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("count") == 4:
                    print("PASS - Test 3: Cities List")
                    tests_passed += 1
                else:
                    print(f"FAIL - Test 3: Cities List (count={data.get('count')})")
                    tests_failed += 1
            else:
                print(f"FAIL - Test 3: Cities List (status={response.status_code})")
                tests_failed += 1
        except Exception as e:
            print(f"ERROR - Test 3: Cities List: {e}")
            tests_failed += 1

        # Test 4-7: City Rules for each city
        cities = ["Mumbai", "Pune", "Ahmedabad", "Nashik"]
        expected_fsi = {"Mumbai": 1.33, "Pune": 1.5, "Ahmedabad": 1.8, "Nashik": 1.2}

        for i, city in enumerate(cities, 4):
            try:
                response = await client.get(f"{base_url}/api/v1/cities/{city}/rules", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("fsi_base") == expected_fsi[city]:
                        print(f"PASS - Test {i}: {city} Rules")
                        tests_passed += 1
                    else:
                        print(f"FAIL - Test {i}: {city} Rules (fsi_base={data.get('fsi_base')})")
                        tests_failed += 1
                else:
                    print(f"FAIL - Test {i}: {city} Rules (status={response.status_code})")
                    tests_failed += 1
            except Exception as e:
                print(f"ERROR - Test {i}: {city} Rules: {e}")
                tests_failed += 1

        # Test 8: City Context
        try:
            response = await client.get(f"{base_url}/api/v1/cities/Mumbai/context", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                if "typical_use_cases" in data and len(data["typical_use_cases"]) >= 3:
                    print("PASS - Test 8: City Context")
                    tests_passed += 1
                else:
                    print("FAIL - Test 8: City Context (missing use cases)")
                    tests_failed += 1
            else:
                print(f"FAIL - Test 8: City Context (status={response.status_code})")
                tests_failed += 1
        except Exception as e:
            print(f"ERROR - Test 8: City Context: {e}")
            tests_failed += 1

        # Test 9: Error Handling (Invalid City)
        try:
            response = await client.get(f"{base_url}/api/v1/cities/InvalidCity/rules", timeout=10.0)
            if response.status_code == 404:
                print("PASS - Test 9: Error Handling")
                tests_passed += 1
            else:
                print(f"FAIL - Test 9: Error Handling (status={response.status_code})")
                tests_failed += 1
        except Exception as e:
            print(f"ERROR - Test 9: Error Handling: {e}")
            tests_failed += 1

        # Test 10: Performance Test (Response Time)
        try:
            import time

            start_time = time.time()
            response = await client.get(f"{base_url}/api/v1/cities/", timeout=10.0)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # ms

            if response.status_code == 200 and response_time < 1000:  # Under 1 second
                print(f"PASS - Test 10: Performance ({response_time:.1f}ms)")
                tests_passed += 1
            else:
                print(f"FAIL - Test 10: Performance ({response_time:.1f}ms)")
                tests_failed += 1
        except Exception as e:
            print(f"ERROR - Test 10: Performance: {e}")
            tests_failed += 1

    # Summary
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0

    print(f"\n{'='*60}")
    print("COMPREHENSIVE SMOKE TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print(f"Success Rate: {success_rate:.1f}%")

    if tests_failed == 0:
        print("\nALL SMOKE TESTS PASSED!")
        return True
    else:
        print(f"\n{tests_failed} SMOKE TESTS FAILED!")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_smoke_tests())
    sys.exit(0 if success else 1)
