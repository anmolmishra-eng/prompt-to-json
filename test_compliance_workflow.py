"""
Test Compliance Validation Workflow
"""
import asyncio
from datetime import datetime

async def test_compliance_validation_workflow():
    """Test the compliance validation workflow"""
    print("Testing Compliance Validation Workflow...")

    # Mock data
    spec_id = "test_spec_001"
    city = "Mumbai"
    case_types = ["fsi", "setback", "height", "parking"]

    # Test 1: Mock spec fetching
    print("\n1. Testing spec fetching...")
    mock_spec = {
        "spec_id": spec_id,
        "spec_json": {
            "design_type": "residential",
            "plot_area": 1000,
            "built_area": 800,
            "floors": 2,
            "setbacks": {"front": 3, "rear": 3, "side": 1.5}
        }
    }
    print(f"✓ Mock spec created: {mock_spec['spec_json']['design_type']}")

    # Test 2: Mock compliance checks
    print("\n2. Testing compliance checks...")
    mock_results = []
    for case_type in case_types:
        result = {
            "case_id": f"{case_type}_{city}_mock",
            "compliant": case_type in ["fsi", "height"],  # FSI and height pass
            "violations": [] if case_type in ["fsi", "height"] else [f"{case_type} violation detected"],
            "status": "completed",
            "confidence_score": 0.85
        }
        mock_results.append(result)
        status = "PASS" if result["compliant"] else "FAIL"
        print(f"  {case_type}: {status}")

    # Test 3: Aggregate results
    print("\n3. Testing result aggregation...")
    all_compliant = all(r["compliant"] for r in mock_results)
    all_violations = []
    for r in mock_results:
        all_violations.extend(r["violations"])

    final_result = {
        "spec_id": spec_id,
        "city": city,
        "case_types": case_types,
        "compliant": all_compliant,
        "violations": all_violations,
        "check_results": mock_results,
        "timestamp": datetime.utcnow().isoformat(),
        "total_checks": len(case_types),
        "passed_checks": sum(1 for r in mock_results if r["compliant"])
    }

    print(f"✓ Overall compliance: {'PASS' if all_compliant else 'FAIL'}")
    print(f"✓ Checks passed: {final_result['passed_checks']}/{final_result['total_checks']}")
    print(f"✓ Violations found: {len(all_violations)}")

    # Test 4: Notification format
    print("\n4. Testing notification format...")
    message = f"""
    Compliance Check Complete for Spec {spec_id}

    Status: {'✓ Compliant' if all_compliant else '✗ Non-Compliant'}

    {'Violations Found: ' + str(len(all_violations)) if all_violations else 'No violations found.'}
    """
    print(f"✓ Notification: {message.strip()}")

    return final_result

if __name__ == "__main__":
    result = asyncio.run(test_compliance_validation_workflow())
    print(f"\n✅ Test completed successfully!")
    print(f"Final result keys: {list(result.keys())}")
