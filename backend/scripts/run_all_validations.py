"""
Run all multi-city validations
Comprehensive validation suite
"""

import asyncio
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_validation_script(script_name: str) -> dict:
    """Run a validation script and return results"""
    
    print(f"\n{'='*60}")
    print(f"Running {script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "script": script_name,
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    except subprocess.TimeoutExpired:
        return {
            "script": script_name,
            "status": "TIMEOUT",
            "returncode": -1,
            "error": "Script timed out after 60 seconds"
        }
    
    except Exception as e:
        return {
            "script": script_name,
            "status": "ERROR",
            "returncode": -1,
            "error": str(e)
        }


async def run_all_validations():
    """Run all validation scripts"""
    
    print("Multi-City Comprehensive Validation Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")
    
    # List of validation scripts to run
    validation_scripts = [
        "validate_city_data.py",
        "validate_api_endpoints.py"
    ]
    
    results = []
    
    # Run each validation script
    for script in validation_scripts:
        result = run_validation_script(script)
        results.append(result)
        
        # Print summary for this script
        print(f"\nResult: {result['status']}")
        if result['status'] == 'PASS':
            # Extract key metrics from stdout
            stdout = result['stdout']
            if 'Success Rate:' in stdout:
                success_rate_line = [line for line in stdout.split('\n') if 'Success Rate:' in line]
                if success_rate_line:
                    print(f"  {success_rate_line[0].strip()}")
        else:
            print(f"  Return Code: {result['returncode']}")
            if 'error' in result:
                print(f"  Error: {result['error']}")
    
    # Overall summary
    total_scripts = len(results)
    passed_scripts = sum(1 for r in results if r["status"] == "PASS")
    failed_scripts = sum(1 for r in results if r["status"] == "FAIL")
    error_scripts = sum(1 for r in results if r["status"] in ["ERROR", "TIMEOUT"])
    
    print(f"\n{'='*60}")
    print("COMPREHENSIVE VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Scripts: {total_scripts}")
    print(f"Passed: {passed_scripts}")
    print(f"Failed: {failed_scripts}")
    print(f"Errors/Timeouts: {error_scripts}")
    print(f"Overall Success Rate: {(passed_scripts/total_scripts)*100:.1f}%")
    print(f"Completed at: {datetime.now().isoformat()}")
    
    # Determine overall status
    if passed_scripts == total_scripts:
        print("\nSTATUS: ALL VALIDATIONS PASSED")
        return True
    else:
        print("\nSTATUS: SOME VALIDATIONS FAILED")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_validations())
    sys.exit(0 if success else 1)