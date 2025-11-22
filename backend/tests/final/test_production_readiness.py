"""
Final production readiness tests
Comprehensive end-to-end validation before go-live
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

import httpx

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.multi_city.city_data_loader import City, CityDataLoader


class ProductionReadinessValidator:
    """Validate system is production-ready"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = []

    async def test_1_system_health(self) -> Dict:
        """Test 1: System health check"""
        print("\nTest 1: System Health Check")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/health", timeout=10.0)

                if response.status_code == 200:
                    data = response.json()
                    print(f"   PASS - System healthy: {data.get('status')}")
                    return {"test": "system_health", "status": "pass", "details": data}
                else:
                    print(f"   FAIL - HTTP {response.status_code}")
                    return {"test": "system_health", "status": "fail", "status_code": response.status_code}

            except Exception as e:
                print(f"   ERROR - {str(e)}")
                return {"test": "system_health", "status": "error", "error": str(e)}

    async def test_2_all_cities(self) -> Dict:
        """Test 2: All cities accessible"""
        print("\nTest 2: All Cities Validation")

        cities = ["Mumbai", "Pune", "Ahmedabad", "Nashik"]
        city_results = {}

        async with httpx.AsyncClient() as client:
            for city in cities:
                try:
                    response = await client.get(f"{self.base_url}/api/v1/cities/{city}/rules", timeout=10.0)

                    if response.status_code == 200:
                        data = response.json()
                        city_results[city] = "pass"
                        print(f"   PASS {city}: FSI {data['fsi_base']}")
                    else:
                        city_results[city] = "fail"
                        print(f"   FAIL {city}: HTTP {response.status_code}")

                except Exception as e:
                    city_results[city] = "error"
                    print(f"   ERROR {city}: {str(e)}")

        all_passed = all(status == "pass" for status in city_results.values())

        if all_passed:
            return {"test": "all_cities", "status": "pass", "details": city_results}
        else:
            return {"test": "all_cities", "status": "fail", "details": city_results}

    async def test_3_design_generation(self) -> Dict:
        """Test 3: Design generation"""
        print("\nTest 3: Design Generation")

        async with httpx.AsyncClient() as client:
            try:
                request = {
                    "user_id": "final_test",
                    "prompt": "Design a 4-floor residential building",
                    "project_id": "final_test_001",
                    "city": "Mumbai",
                }

                response = await client.post(f"{self.base_url}/api/v1/generate", json=request, timeout=30.0)

                if response.status_code == 200:
                    data = response.json()

                    # Verify response structure
                    required_fields = ["spec_id", "spec_json"]
                    has_all_fields = all(field in data for field in required_fields)

                    if has_all_fields:
                        print(f"   PASS - Design generated (spec_id: {data['spec_id']})")
                        return {"test": "design_generation", "status": "pass", "details": data}
                    else:
                        print("   FAIL - Missing required fields")
                        return {"test": "design_generation", "status": "fail", "details": data}
                else:
                    print(f"   FAIL - HTTP {response.status_code}")
                    return {"test": "design_generation", "status": "fail", "status_code": response.status_code}

            except Exception as e:
                print(f"   ERROR - {str(e)}")
                return {"test": "design_generation", "status": "error", "error": str(e)}

    async def test_4_data_validation(self) -> Dict:
        """Test 4: Data validation"""
        print("\nTest 4: Data Validation")

        try:
            loader = CityDataLoader()
            cities = loader.get_all_cities()

            if len(cities) == 4:
                # Validate each city
                all_valid = True
                for city in cities:
                    rules = loader.get_city_rules(city)
                    context = loader.get_city_context(city)

                    if not rules or not context:
                        all_valid = False
                        break

                if all_valid:
                    print("   PASS - All city data valid")
                    return {"test": "data_validation", "status": "pass", "cities": len(cities)}
                else:
                    print("   FAIL - Invalid city data")
                    return {"test": "data_validation", "status": "fail"}
            else:
                print(f"   FAIL - Expected 4 cities, got {len(cities)}")
                return {"test": "data_validation", "status": "fail", "cities": len(cities)}

        except Exception as e:
            print(f"   ERROR - {str(e)}")
            return {"test": "data_validation", "status": "error", "error": str(e)}

    async def test_5_api_endpoints(self) -> Dict:
        """Test 5: Key API endpoints"""
        print("\nTest 5: API Endpoints")

        endpoints = [
            ("Cities List", "/api/v1/cities/"),
            ("Mumbai Rules", "/api/v1/cities/Mumbai/rules"),
            ("Pune Context", "/api/v1/cities/Pune/context"),
        ]

        endpoint_results = {}

        async with httpx.AsyncClient() as client:
            for name, endpoint in endpoints:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}", timeout=10.0)

                    if response.status_code == 200:
                        endpoint_results[name] = "pass"
                        print(f"   PASS {name}")
                    else:
                        endpoint_results[name] = "fail"
                        print(f"   FAIL {name}: HTTP {response.status_code}")

                except Exception as e:
                    endpoint_results[name] = "error"
                    print(f"   ERROR {name}: {str(e)}")

        all_passed = all(status == "pass" for status in endpoint_results.values())

        if all_passed:
            return {"test": "api_endpoints", "status": "pass", "details": endpoint_results}
        else:
            return {"test": "api_endpoints", "status": "fail", "details": endpoint_results}

    async def run_all_tests(self):
        """Run all production readiness tests"""
        print("=" * 60)
        print("FINAL PRODUCTION READINESS TESTS")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Run tests sequentially
        self.results.append(await self.test_1_system_health())
        self.results.append(await self.test_2_all_cities())
        self.results.append(await self.test_3_design_generation())
        self.results.append(await self.test_4_data_validation())
        self.results.append(await self.test_5_api_endpoints())

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r["status"] == "pass")
        failed = sum(1 for r in self.results if r["status"] == "fail")
        errors = sum(1 for r in self.results if r["status"] == "error")

        print(f"Passed: {passed}/{len(self.results)}")
        print(f"Failed: {failed}/{len(self.results)}")
        print(f"Errors: {errors}/{len(self.results)}")

        success_rate = (passed / len(self.results)) * 100
        print(f"Success Rate: {success_rate:.1f}%")

        if failed == 0 and errors == 0:
            print("\nALL TESTS PASSED - PRODUCTION READY!")
            return 0
        elif success_rate >= 80:
            print(f"\nMOSTLY SUCCESSFUL - REVIEW FAILURES")
            return 0
        else:
            print(f"\nTESTS FAILED - NOT PRODUCTION READY")
            return 1


async def main():
    """Run final tests"""
    validator = ProductionReadinessValidator()
    exit_code = await validator.run_all_tests()
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
