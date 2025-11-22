"""
Mock smoke tests for deployment validation
Tests that can run without a live server
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.multi_city.city_data_loader import City, CityDataLoader


def run_mock_smoke_tests():
    """Run mock smoke tests without requiring live server"""
    
    tests_passed = 0
    tests_failed = 0
    
    print("Running Mock Smoke Tests...")
    print("=" * 50)
    
    # Test 1: City Data Loader Import
    try:
        loader = CityDataLoader()
        print("PASS - Test 1: City Data Loader Import")
        tests_passed += 1
    except Exception as e:
        print(f"FAIL - Test 1: City Data Loader Import: {e}")
        tests_failed += 1
    
    # Test 2: All Cities Available
    try:
        cities = loader.get_all_cities()
        if len(cities) == 4:
            print("PASS - Test 2: All Cities Available")
            tests_passed += 1
        else:
            print(f"FAIL - Test 2: All Cities Available (count={len(cities)})")
            tests_failed += 1
    except Exception as e:
        print(f"FAIL - Test 2: All Cities Available: {e}")
        tests_failed += 1
    
    # Test 3-6: City Rules for each city
    expected_fsi = {"Mumbai": 1.33, "Pune": 1.5, "Ahmedabad": 1.8, "Nashik": 1.2}
    
    for i, (city_name, expected) in enumerate(expected_fsi.items(), 3):
        try:
            city = City(city_name)
            rules = loader.get_city_rules(city)
            if rules.fsi_base == expected:
                print(f"PASS - Test {i}: {city_name} Rules")
                tests_passed += 1
            else:
                print(f"FAIL - Test {i}: {city_name} Rules (fsi_base={rules.fsi_base})")
                tests_failed += 1
        except Exception as e:
            print(f"FAIL - Test {i}: {city_name} Rules: {e}")
            tests_failed += 1
    
    # Test 7: City Context
    try:
        city = City.MUMBAI
        context = loader.get_city_context(city)
        required_fields = ["city", "dcr_version", "constraints", "source_documents", "typical_use_cases"]
        missing_fields = [field for field in required_fields if field not in context]
        
        if not missing_fields:
            print("PASS - Test 7: City Context")
            tests_passed += 1
        else:
            print(f"FAIL - Test 7: City Context (missing: {missing_fields})")
            tests_failed += 1
    except Exception as e:
        print(f"FAIL - Test 7: City Context: {e}")
        tests_failed += 1
    
    # Test 8: Invalid City Handling
    try:
        invalid_city = loader.validate_city("InvalidCity")
        if invalid_city is None:
            print("PASS - Test 8: Invalid City Handling")
            tests_passed += 1
        else:
            print("FAIL - Test 8: Invalid City Handling")
            tests_failed += 1
    except Exception as e:
        print(f"FAIL - Test 8: Invalid City Handling: {e}")
        tests_failed += 1
    
    # Test 9: Use Cases Count
    try:
        city = City.PUNE
        context = loader.get_city_context(city)
        use_cases = context.get("typical_use_cases", [])
        if len(use_cases) >= 3:
            print("PASS - Test 9: Use Cases Count")
            tests_passed += 1
        else:
            print(f"FAIL - Test 9: Use Cases Count ({len(use_cases)})")
            tests_failed += 1
    except Exception as e:
        print(f"FAIL - Test 9: Use Cases Count: {e}")
        tests_failed += 1
    
    # Test 10: Data Consistency
    try:
        consistent = True
        for city in City:
            rules = loader.get_city_rules(city)
            context = loader.get_city_context(city)
            
            if rules.city.value != context["city"]:
                consistent = False
                break
            
            if rules.fsi_base != context["constraints"]["fsi_base"]:
                consistent = False
                break
        
        if consistent:
            print("PASS - Test 10: Data Consistency")
            tests_passed += 1
        else:
            print("FAIL - Test 10: Data Consistency")
            tests_failed += 1
    except Exception as e:
        print(f"FAIL - Test 10: Data Consistency: {e}")
        tests_failed += 1
    
    # Summary
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n{'='*50}")
    print("MOCK SMOKE TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if tests_failed == 0:
        print("\nALL MOCK SMOKE TESTS PASSED!")
        return True
    else:
        print(f"\n{tests_failed} MOCK SMOKE TESTS FAILED!")
        return False


if __name__ == "__main__":
    success = run_mock_smoke_tests()
    sys.exit(0 if success else 1)