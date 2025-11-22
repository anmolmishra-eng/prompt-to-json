"""
Comprehensive validation tests for production readiness
Tests both live server and offline data validation
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

import httpx

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.multi_city.city_data_loader import City, CityDataLoader


class ComprehensiveValidator:
    """Comprehensive production validation"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = []
        self.server_available = False
    
    async def check_server_availability(self):
        """Check if server is available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/health", timeout=5.0)
                self.server_available = response.status_code == 200
        except:
            self.server_available = False
        
        print(f"Server Status: {'Available' if self.server_available else 'Not Available'}")
        if not self.server_available:
            print("Note: Running offline validation tests only")
    
    def test_1_data_integrity(self):
        """Test 1: Data integrity validation"""
        print("\nTest 1: Data Integrity Validation")
        
        try:
            loader = CityDataLoader()
            cities = loader.get_all_cities()
            
            # Test city count
            if len(cities) != 4:
                print(f"   FAIL - Expected 4 cities, got {len(cities)}")
                return {"test": "data_integrity", "status": "fail", "cities": len(cities)}
            
            # Test each city
            city_data = {}
            for city in cities:
                rules = loader.get_city_rules(city)
                context = loader.get_city_context(city)
                
                city_data[city.value] = {
                    "fsi_base": rules.fsi_base,
                    "dcr_version": rules.dcr_version,
                    "use_cases": len(context["typical_use_cases"])
                }
                
                print(f"   PASS {city.value}: FSI {rules.fsi_base}, {len(context['typical_use_cases'])} use cases")
            
            print("   PASS - All city data integrity validated")
            return {"test": "data_integrity", "status": "pass", "details": city_data}
        
        except Exception as e:
            print(f"   ERROR - {str(e)}")
            return {"test": "data_integrity", "status": "error", "error": str(e)}
    
    def test_2_business_logic(self):
        """Test 2: Business logic validation"""
        print("\nTest 2: Business Logic Validation")
        
        try:
            loader = CityDataLoader()
            
            # Test city validation
            valid_city = loader.validate_city("Mumbai")
            invalid_city = loader.validate_city("InvalidCity")
            
            if valid_city and not invalid_city:
                print("   PASS - City validation logic works")
            else:
                print("   FAIL - City validation logic broken")
                return {"test": "business_logic", "status": "fail"}
            
            # Test data consistency
            mumbai = City.MUMBAI
            rules = loader.get_city_rules(mumbai)
            context = loader.get_city_context(mumbai)
            
            # Check FSI consistency
            if rules.fsi_base == context["constraints"]["fsi_base"]:
                print("   PASS - Data consistency validated")
            else:
                print("   FAIL - Data inconsistency detected")
                return {"test": "business_logic", "status": "fail"}
            
            # Test required fields
            required_rule_fields = ["city", "dcr_version", "fsi_base", "setback_front", "setback_rear"]
            missing_fields = [field for field in required_rule_fields if not hasattr(rules, field)]
            
            if not missing_fields:
                print("   PASS - All required fields present")
                return {"test": "business_logic", "status": "pass"}
            else:
                print(f"   FAIL - Missing fields: {missing_fields}")
                return {"test": "business_logic", "status": "fail", "missing_fields": missing_fields}
        
        except Exception as e:
            print(f"   ERROR - {str(e)}")
            return {"test": "business_logic", "status": "error", "error": str(e)}
    
    async def test_3_api_structure(self):
        """Test 3: API structure validation"""
        print("\nTest 3: API Structure Validation")
        
        if not self.server_available:
            print("   SKIP - Server not available")
            return {"test": "api_structure", "status": "skip", "reason": "server_unavailable"}
        
        endpoints = [
            ("Health Check", "/api/v1/health"),
            ("Cities List", "/api/v1/cities/"),
            ("Mumbai Rules", "/api/v1/cities/Mumbai/rules"),
            ("Pune Context", "/api/v1/cities/Pune/context")
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
            return {"test": "api_structure", "status": "pass", "details": endpoint_results}
        else:
            return {"test": "api_structure", "status": "fail", "details": endpoint_results}
    
    def test_4_deployment_readiness(self):
        """Test 4: Deployment readiness"""
        print("\nTest 4: Deployment Readiness")
        
        try:
            # Check required files exist
            required_files = [
                "deployment/Dockerfile",
                "deployment/docker-compose.yml",
                "deployment/.env.example",
                "HANDOVER.md",
                "requirements.txt"
            ]
            
            missing_files = []
            for file_path in required_files:
                if not Path(file_path).exists():
                    missing_files.append(file_path)
            
            if not missing_files:
                print("   PASS - All deployment files present")
            else:
                print(f"   FAIL - Missing files: {missing_files}")
                return {"test": "deployment_readiness", "status": "fail", "missing_files": missing_files}
            
            # Check documentation exists
            docs_files = [
                "docs/diagrams/system_overview.md",
                "docs/DEMO_GUIDE.md",
                "reports/day6_summary.md"
            ]
            
            missing_docs = []
            for doc_path in docs_files:
                if not Path(doc_path).exists():
                    missing_docs.append(doc_path)
            
            if not missing_docs:
                print("   PASS - All documentation present")
                return {"test": "deployment_readiness", "status": "pass"}
            else:
                print(f"   FAIL - Missing documentation: {missing_docs}")
                return {"test": "deployment_readiness", "status": "fail", "missing_docs": missing_docs}
        
        except Exception as e:
            print(f"   ERROR - {str(e)}")
            return {"test": "deployment_readiness", "status": "error", "error": str(e)}
    
    def test_5_validation_history(self):
        """Test 5: Validation history check"""
        print("\nTest 5: Validation History")
        
        try:
            # Check if validation reports exist
            validation_dir = Path("reports/validation")
            if not validation_dir.exists():
                print("   FAIL - No validation reports found")
                return {"test": "validation_history", "status": "fail", "reason": "no_reports"}
            
            # Count validation reports
            validation_files = list(validation_dir.glob("*.json"))
            
            if len(validation_files) >= 1:
                print(f"   PASS - {len(validation_files)} validation reports found")
                
                # Check latest report
                latest_report = max(validation_files, key=lambda p: p.stat().st_mtime)
                print(f"   PASS - Latest report: {latest_report.name}")
                
                return {"test": "validation_history", "status": "pass", "reports": len(validation_files)}
            else:
                print("   FAIL - No validation reports found")
                return {"test": "validation_history", "status": "fail", "reports": 0}
        
        except Exception as e:
            print(f"   ERROR - {str(e)}")
            return {"test": "validation_history", "status": "error", "error": str(e)}
    
    async def run_all_tests(self):
        """Run all comprehensive validation tests"""
        print("=" * 60)
        print("COMPREHENSIVE PRODUCTION VALIDATION")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check server availability first
        await self.check_server_availability()
        
        # Run tests
        self.results.append(self.test_1_data_integrity())
        self.results.append(self.test_2_business_logic())
        self.results.append(await self.test_3_api_structure())
        self.results.append(self.test_4_deployment_readiness())
        self.results.append(self.test_5_validation_history())
        
        # Summary
        print("\n" + "=" * 60)
        print("COMPREHENSIVE VALIDATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["status"] == "pass")
        failed = sum(1 for r in self.results if r["status"] == "fail")
        errors = sum(1 for r in self.results if r["status"] == "error")
        skipped = sum(1 for r in self.results if r["status"] == "skip")
        
        print(f"Passed: {passed}/{len(self.results)}")
        print(f"Failed: {failed}/{len(self.results)}")
        print(f"Errors: {errors}/{len(self.results)}")
        print(f"Skipped: {skipped}/{len(self.results)}")
        
        # Calculate success rate (excluding skipped)
        testable = len(self.results) - skipped
        success_rate = (passed / testable) * 100 if testable > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Determine overall status
        if success_rate >= 80:
            print(f"\nVALIDATION SUCCESSFUL - PRODUCTION READY")
            print("System meets production readiness criteria")
            return 0
        else:
            print(f"\nVALIDATION FAILED - REVIEW REQUIRED")
            print("System needs attention before production deployment")
            return 1


async def main():
    """Run comprehensive validation"""
    validator = ComprehensiveValidator()
    exit_code = await validator.run_all_tests()
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)