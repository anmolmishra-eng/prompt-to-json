#!/usr/bin/env python3
"""
Run end-to-end tests for multi-city pipeline
"""

import subprocess
import sys
import time


def run_e2e_tests():
    """Run comprehensive e2e test suite"""
    
    print("Starting Multi-City E2E Test Suite")
    print("=" * 50)
    
    # Test commands
    test_commands = [
        # Basic city data tests
        ["python", "-m", "pytest", "tests/e2e/test_multi_city_pipeline.py::test_city_rules_available", "-v"],
        
        # Context completeness tests
        ["python", "-m", "pytest", "tests/e2e/test_multi_city_pipeline.py::test_city_context_completeness", "-v"],
        
        # Performance tests
        ["python", "-m", "pytest", "tests/e2e/test_multi_city_pipeline.py::test_performance_benchmarks", "-v"],
        
        # Error handling tests
        ["python", "-m", "pytest", "tests/e2e/test_multi_city_pipeline.py::test_error_handling", "-v"],
        
        # Integration tests (may skip if systems down)
        ["python", "-m", "pytest", "tests/e2e/test_multi_city_pipeline.py::test_end_to_end_pipeline", "-v", "-s"],
        ["python", "-m", "pytest", "tests/e2e/test_multi_city_pipeline.py::test_mcp_rules_for_all_cities", "-v", "-s"],
        ["python", "-m", "pytest", "tests/e2e/test_multi_city_pipeline.py::test_rl_feedback_all_cities", "-v", "-s"],
    ]
    
    results = []
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\nTest {i}/{len(test_commands)}: {' '.join(cmd[-2:])}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            end_time = time.time()
            
            if result.returncode == 0:
                print(f"PASSED ({end_time - start_time:.1f}s)")
                results.append("PASS")
            else:
                print(f"FAILED ({end_time - start_time:.1f}s)")
                print("STDOUT:", result.stdout[-200:] if result.stdout else "None")
                print("STDERR:", result.stderr[-200:] if result.stderr else "None")
                results.append("FAIL")
                
        except subprocess.TimeoutExpired:
            print("TIMEOUT (60s)")
            results.append("TIMEOUT")
        except Exception as e:
            print(f"ERROR: {e}")
            results.append("ERROR")
    
    # Summary
    print("\n" + "=" * 50)
    print("E2E TEST SUMMARY")
    print("=" * 50)
    
    passed = results.count("PASS")
    failed = results.count("FAIL")
    timeouts = results.count("TIMEOUT")
    errors = results.count("ERROR")
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {failed}/{total}")
    print(f"Timeouts: {timeouts}/{total}")
    print(f"Errors: {errors}/{total}")
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\nE2E Tests: OVERALL SUCCESS")
        return 0
    else:
        print("\nE2E Tests: NEEDS ATTENTION")
        return 1


if __name__ == "__main__":
    exit_code = run_e2e_tests()
    sys.exit(exit_code)