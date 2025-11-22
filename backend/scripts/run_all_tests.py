"""
Run all test suites for comprehensive validation
Orchestrates smoke tests, load tests, and integration tests
"""

import asyncio
import subprocess
import sys
import time
from datetime import datetime


def run_test_script(script_name: str, description: str) -> dict:
    """Run a test script and return results"""

    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"], capture_output=True, text=True, timeout=300  # 5 minutes timeout
        )

        end_time = time.time()
        duration = end_time - start_time

        # Print the output
        if result.stdout:
            print(result.stdout)

        if result.stderr and result.returncode != 0:
            print("STDERR:", result.stderr)

        return {
            "script": script_name,
            "description": description,
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "returncode": result.returncode,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired:
        return {
            "script": script_name,
            "description": description,
            "status": "TIMEOUT",
            "returncode": -1,
            "duration": 300,
            "error": "Test timed out after 5 minutes",
        }

    except Exception as e:
        return {
            "script": script_name,
            "description": description,
            "status": "ERROR",
            "returncode": -1,
            "duration": 0,
            "error": str(e),
        }


def main():
    """Run all test suites"""

    print("🚀 COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")

    # Test suites to run
    test_suites = [
        ("smoke_tests.py", "Basic Smoke Tests"),
        ("comprehensive_smoke_tests.py", "Comprehensive Smoke Tests"),
        ("integration_tests.py", "Integration Tests"),
        ("load_tests.py", "Load Tests"),
        ("validate_city_data.py", "Data Validation Tests"),
    ]

    results = []

    # Run each test suite
    for script, description in test_suites:
        result = run_test_script(script, description)
        results.append(result)

    # Generate summary
    total_suites = len(results)
    passed_suites = sum(1 for r in results if r["status"] == "PASS")
    failed_suites = sum(1 for r in results if r["status"] == "FAIL")
    error_suites = sum(1 for r in results if r["status"] in ["ERROR", "TIMEOUT"])
    total_duration = sum(r["duration"] for r in results)

    print(f"\n{'='*60}")
    print("COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Test Suites: {total_suites}")
    print(f"Passed: {passed_suites}")
    print(f"Failed: {failed_suites}")
    print(f"Errors/Timeouts: {error_suites}")
    print(f"Total Duration: {total_duration:.1f} seconds")
    print(f"Success Rate: {(passed_suites/total_suites)*100:.1f}%")
    print(f"Completed at: {datetime.now().isoformat()}")

    # Detailed results
    print(f"\n{'='*60}")
    print("DETAILED RESULTS")
    print(f"{'='*60}")

    for result in results:
        status_icon = "✓" if result["status"] == "PASS" else "✗"
        print(f"{status_icon} {result['description']}: {result['status']} ({result['duration']:.1f}s)")

        if result["status"] != "PASS" and "error" in result:
            print(f"   Error: {result['error']}")

    # Overall status
    if passed_suites == total_suites:
        print(f"\n🎉 ALL TEST SUITES PASSED!")
        print("System is ready for deployment!")
        return 0
    elif passed_suites >= total_suites * 0.8:  # 80% pass rate
        print(f"\n⚠️  MOSTLY SUCCESSFUL ({passed_suites}/{total_suites} passed)")
        print("System may be ready for deployment with caution.")
        return 0
    else:
        print(f"\n❌ MULTIPLE TEST FAILURES ({failed_suites + error_suites}/{total_suites} failed)")
        print("System is NOT ready for deployment!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
