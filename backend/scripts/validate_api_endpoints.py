"""
Validate multi-city API endpoints
Tests all endpoints with real HTTP requests
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import httpx

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.multi_city.city_data_loader import City


async def validate_api_endpoints():
    """Validate all multi-city API endpoints"""

    base_url = "http://localhost:8000"
    results = []

    print("Multi-City API Endpoint Validation")
    print("=" * 50)

    async with httpx.AsyncClient() as client:
        # Test 1: List all cities
        print("\nTesting: GET /api/v1/cities/")
        try:
            response = await client.get(f"{base_url}/api/v1/cities/")
            if response.status_code == 200:
                data = response.json()
                cities_count = data.get("count", 0)
                print(f"  PASS: {cities_count} cities available")
                results.append({"endpoint": "list_cities", "status": "PASS", "cities_count": cities_count})
            else:
                print(f"  FAIL: Status {response.status_code}")
                results.append({"endpoint": "list_cities", "status": "FAIL", "status_code": response.status_code})
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"endpoint": "list_cities", "status": "ERROR", "error": str(e)})

        # Test 2: City rules for each city
        for city in City:
            print(f"\nTesting: GET /api/v1/cities/{city.value}/rules")
            try:
                response = await client.get(f"{base_url}/api/v1/cities/{city.value}/rules")
                if response.status_code == 200:
                    data = response.json()
                    fsi = data.get("fsi_base", "unknown")
                    print(f"  PASS: {city.value} rules (FSI: {fsi})")
                    results.append({"endpoint": f"rules_{city.value}", "status": "PASS", "fsi_base": fsi})
                else:
                    print(f"  FAIL: Status {response.status_code}")
                    results.append(
                        {"endpoint": f"rules_{city.value}", "status": "FAIL", "status_code": response.status_code}
                    )
            except Exception as e:
                print(f"  ERROR: {e}")
                results.append({"endpoint": f"rules_{city.value}", "status": "ERROR", "error": str(e)})

        # Test 3: City context for each city
        for city in City:
            print(f"\nTesting: GET /api/v1/cities/{city.value}/context")
            try:
                response = await client.get(f"{base_url}/api/v1/cities/{city.value}/context")
                if response.status_code == 200:
                    data = response.json()
                    use_cases_count = len(data.get("typical_use_cases", []))
                    print(f"  PASS: {city.value} context ({use_cases_count} use cases)")
                    results.append(
                        {"endpoint": f"context_{city.value}", "status": "PASS", "use_cases_count": use_cases_count}
                    )
                else:
                    print(f"  FAIL: Status {response.status_code}")
                    results.append(
                        {"endpoint": f"context_{city.value}", "status": "FAIL", "status_code": response.status_code}
                    )
            except Exception as e:
                print(f"  ERROR: {e}")
                results.append({"endpoint": f"context_{city.value}", "status": "ERROR", "error": str(e)})

        # Test 4: Invalid city handling
        print(f"\nTesting: GET /api/v1/cities/InvalidCity/rules")
        try:
            response = await client.get(f"{base_url}/api/v1/cities/InvalidCity/rules")
            if response.status_code == 404:
                print(f"  PASS: Invalid city properly rejected")
                results.append({"endpoint": "invalid_city", "status": "PASS"})
            else:
                print(f"  FAIL: Expected 404, got {response.status_code}")
                results.append({"endpoint": "invalid_city", "status": "FAIL", "status_code": response.status_code})
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"endpoint": "invalid_city", "status": "ERROR", "error": str(e)})

    # Generate summary
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["status"] == "PASS")
    failed_tests = sum(1 for r in results if r["status"] == "FAIL")
    error_tests = sum(1 for r in results if r["status"] == "ERROR")

    print(f"\n{'='*50}")
    print("API VALIDATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Errors: {error_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    # Save report
    report_dir = Path("reports/validation")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / f"api_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "error_tests": error_tests,
        "success_rate": (passed_tests / total_tests) * 100,
        "results": results,
    }

    with open(report_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nReport saved to: {report_file}")

    return passed_tests == total_tests


async def main():
    """Run API endpoint validation"""
    success = await validate_api_endpoints()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
