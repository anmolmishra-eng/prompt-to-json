"""
Integration tests for deployment validation
Tests end-to-end workflows and data consistency
"""

import asyncio
import sys
from pathlib import Path

import httpx

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.multi_city.city_data_loader import City


async def run_integration_tests():
    """Run integration tests"""
    
    tests_passed = 0
    tests_failed = 0
    base_url = "http://localhost"
    
    print("Running Integration Tests...")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Data Consistency Across Endpoints
        try:
            # Get cities list
            cities_response = await client.get(f"{base_url}/api/v1/cities/", timeout=10.0)
            cities_data = cities_response.json()
            cities_list = cities_data.get("cities", [])
            
            # Verify each city has consistent data
            consistent = True
            for city in cities_list:
                rules_response = await client.get(f"{base_url}/api/v1/cities/{city}/rules", timeout=10.0)
                context_response = await client.get(f"{base_url}/api/v1/cities/{city}/context", timeout=10.0)
                
                if rules_response.status_code != 200 or context_response.status_code != 200:
                    consistent = False
                    break
                
                rules_data = rules_response.json()
                context_data = context_response.json()
                
                # Check data consistency
                if rules_data.get("city") != context_data.get("city"):
                    consistent = False
                    break
                
                if rules_data.get("fsi_base") != context_data.get("constraints", {}).get("fsi_base"):
                    consistent = False
                    break
            
            if consistent:
                print("✓ Test 1: Data Consistency - PASS")
                tests_passed += 1
            else:
                print("✗ Test 1: Data Consistency - FAIL")
                tests_failed += 1
                
        except Exception as e:
            print(f"✗ Test 1: Data Consistency - ERROR: {e}")
            tests_failed += 1
        
        # Test 2: All Cities Have Required Fields
        try:
            all_valid = True
            required_fields = ["city", "dcr_version", "fsi_base", "setback_front", "setback_rear"]
            
            for city in ["Mumbai", "Pune", "Ahmedabad", "Nashik"]:
                response = await client.get(f"{base_url}/api/v1/cities/{city}/rules", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    for field in required_fields:
                        if field not in data:
                            all_valid = False
                            break
                else:
                    all_valid = False
                    break
            
            if all_valid:
                print("✓ Test 2: Required Fields - PASS")
                tests_passed += 1
            else:
                print("✗ Test 2: Required Fields - FAIL")
                tests_failed += 1
                
        except Exception as e:
            print(f"✗ Test 2: Required Fields - ERROR: {e}")
            tests_failed += 1
        
        # Test 3: Context Completeness
        try:
            all_complete = True
            required_context_fields = ["city", "dcr_version", "constraints", "source_documents", "typical_use_cases"]
            
            for city in ["Mumbai", "Pune", "Ahmedabad", "Nashik"]:
                response = await client.get(f"{base_url}/api/v1/cities/{city}/context", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    for field in required_context_fields:
                        if field not in data:
                            all_complete = False
                            break
                    
                    # Check use cases count
                    if len(data.get("typical_use_cases", [])) < 3:
                        all_complete = False
                        break
                else:
                    all_complete = False
                    break
            
            if all_complete:
                print("✓ Test 3: Context Completeness - PASS")
                tests_passed += 1
            else:
                print("✗ Test 3: Context Completeness - FAIL")
                tests_failed += 1
                
        except Exception as e:
            print(f"✗ Test 3: Context Completeness - ERROR: {e}")
            tests_failed += 1
        
        # Test 4: Error Handling Consistency
        try:
            invalid_cities = ["Delhi", "Bangalore", "Chennai", "InvalidCity"]
            all_handled = True
            
            for invalid_city in invalid_cities:
                rules_response = await client.get(f"{base_url}/api/v1/cities/{invalid_city}/rules", timeout=10.0)
                context_response = await client.get(f"{base_url}/api/v1/cities/{invalid_city}/context", timeout=10.0)
                
                if rules_response.status_code != 404 or context_response.status_code != 404:
                    all_handled = False
                    break
            
            if all_handled:
                print("✓ Test 4: Error Handling - PASS")
                tests_passed += 1
            else:
                print("✗ Test 4: Error Handling - FAIL")
                tests_failed += 1
                
        except Exception as e:
            print(f"✗ Test 4: Error Handling - ERROR: {e}")
            tests_failed += 1
        
        # Test 5: API Response Format Consistency
        try:
            format_consistent = True
            
            # Check cities list format
            cities_response = await client.get(f"{base_url}/api/v1/cities/", timeout=10.0)
            if cities_response.status_code == 200:
                data = cities_response.json()
                if not ("cities" in data and "count" in data):
                    format_consistent = False
            else:
                format_consistent = False
            
            # Check rules format consistency
            for city in ["Mumbai", "Pune"]:
                response = await client.get(f"{base_url}/api/v1/cities/{city}/rules", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    expected_keys = {"city", "dcr_version", "fsi_base", "setback_front", "setback_rear", "parking_ratio"}
                    if not expected_keys.issubset(set(data.keys())):
                        format_consistent = False
                        break
                else:
                    format_consistent = False
                    break
            
            if format_consistent:
                print("✓ Test 5: Response Format - PASS")
                tests_passed += 1
            else:
                print("✗ Test 5: Response Format - FAIL")
                tests_failed += 1
                
        except Exception as e:
            print(f"✗ Test 5: Response Format - ERROR: {e}")
            tests_failed += 1
    
    # Summary
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n{'='*50}")
    print("INTEGRATION TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {tests_failed} INTEGRATION TESTS FAILED!")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)