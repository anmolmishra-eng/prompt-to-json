"""
Validate city data structure and completeness
Tests data integrity without requiring running server
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.multi_city.city_data_loader import City, CityDataLoader


def validate_city_data():
    """Validate all city data for completeness and consistency"""

    loader = CityDataLoader()
    results = []

    print("Multi-City Data Validation")
    print("=" * 50)

    for city in City:
        print(f"\nValidating {city.value}...")

        result = {"city": city.value, "timestamp": datetime.now().isoformat(), "tests": {}}

        # Test 1: City rules exist
        try:
            rules = loader.get_city_rules(city)
            result["tests"]["rules_exist"] = "PASS"
            result["tests"]["fsi_base"] = rules.fsi_base
            result["tests"]["dcr_version"] = rules.dcr_version
        except Exception as e:
            result["tests"]["rules_exist"] = f"FAIL: {e}"

        # Test 2: City context complete
        try:
            context = loader.get_city_context(city)
            required_fields = ["city", "dcr_version", "constraints", "source_documents", "typical_use_cases"]
            missing_fields = [field for field in required_fields if field not in context]

            if not missing_fields:
                result["tests"]["context_complete"] = "PASS"
            else:
                result["tests"]["context_complete"] = f"FAIL: Missing {missing_fields}"
        except Exception as e:
            result["tests"]["context_complete"] = f"FAIL: {e}"

        # Test 3: Constraints validation
        try:
            context = loader.get_city_context(city)
            constraints = context["constraints"]

            required_constraints = ["fsi_base", "setback_front_m", "setback_rear_m", "parking_ratio"]
            missing_constraints = [c for c in required_constraints if c not in constraints]

            if not missing_constraints:
                result["tests"]["constraints_valid"] = "PASS"
            else:
                result["tests"]["constraints_valid"] = f"FAIL: Missing {missing_constraints}"
        except Exception as e:
            result["tests"]["constraints_valid"] = f"FAIL: {e}"

        # Test 4: Use cases defined
        try:
            context = loader.get_city_context(city)
            use_cases = context["typical_use_cases"]

            if len(use_cases) >= 3:  # Should have at least 3 use cases
                result["tests"]["use_cases_defined"] = "PASS"
                result["tests"]["use_case_count"] = len(use_cases)
            else:
                result["tests"]["use_cases_defined"] = f"FAIL: Only {len(use_cases)} use cases"
        except Exception as e:
            result["tests"]["use_cases_defined"] = f"FAIL: {e}"

        # Calculate overall status
        passed_tests = sum(1 for test in result["tests"].values() if str(test) == "PASS")
        total_tests = len(
            [
                k
                for k in result["tests"].keys()
                if not k.endswith("_count") and not k.endswith("_base") and not k.endswith("_version")
            ]
        )

        result["overall_status"] = "PASS" if passed_tests == total_tests else "FAIL"
        result["passed_tests"] = passed_tests
        result["total_tests"] = total_tests

        results.append(result)

        # Print results
        print(f"  Overall: {result['overall_status']} ({passed_tests}/{total_tests})")
        for test_name, test_result in result["tests"].items():
            if (
                not test_name.endswith("_count")
                and not test_name.endswith("_base")
                and not test_name.endswith("_version")
            ):
                status = "PASS" if str(test_result) == "PASS" else "FAIL"
                print(f"    {test_name}: {status}")

    # Generate summary
    total_cities = len(results)
    passed_cities = sum(1 for r in results if r["overall_status"] == "PASS")

    print(f"\n{'='*50}")
    print("VALIDATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total Cities: {total_cities}")
    print(f"Passed: {passed_cities}")
    print(f"Failed: {total_cities - passed_cities}")
    print(f"Success Rate: {(passed_cities/total_cities)*100:.1f}%")

    # Save report
    report_dir = Path("reports/validation")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / f"city_data_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_cities": total_cities,
        "passed_cities": passed_cities,
        "failed_cities": total_cities - passed_cities,
        "success_rate": (passed_cities / total_cities) * 100,
        "results": results,
    }

    with open(report_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nReport saved to: {report_file}")

    return passed_cities == total_cities


if __name__ == "__main__":
    success = validate_city_data()
    sys.exit(0 if success else 1)
