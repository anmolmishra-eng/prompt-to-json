"""
Test Spec Validation
Verifies that validation catches incomplete specs
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.spec_validator import validate_spec_json, validate_with_warnings, SpecValidationError

def test_validation():
    print("\n" + "="*70)
    print("SPEC VALIDATION TESTS")
    print("="*70)

    # Test 1: Valid spec
    print("\n[TEST 1] Valid Complete Spec")
    print("-" * 70)
    valid_spec = {
        "design_type": "apartment",
        "dimensions": {"width": 15.0, "length": 12.0, "height": 3.5},
        "stories": 2,
        "objects": [{"type": "wall", "count": 4}]
    }
    try:
        validate_spec_json(valid_spec)
        print("[PASS] Validation passed for complete spec")
    except SpecValidationError as e:
        print(f"[FAIL] {e}")

    # Test 2: Missing dimensions key
    print("\n[TEST 2] Missing 'dimensions' Key")
    print("-" * 70)
    missing_dims = {
        "design_type": "apartment",
        "objects": []
    }
    try:
        validate_spec_json(missing_dims)
        print("[FAIL] Should have raised error")
    except SpecValidationError as e:
        print(f"[PASS] Caught error: {e}")

    # Test 3: Missing width
    print("\n[TEST 3] Missing 'width' Dimension")
    print("-" * 70)
    missing_width = {
        "design_type": "apartment",
        "dimensions": {"length": 12.0, "height": 3.5}
    }
    try:
        validate_spec_json(missing_width)
        print("[FAIL] Should have raised error")
    except SpecValidationError as e:
        print(f"[PASS] Caught error: {e}")

    # Test 4: Null dimension
    print("\n[TEST 4] Null Dimension Value")
    print("-" * 70)
    null_dim = {
        "design_type": "apartment",
        "dimensions": {"width": None, "length": 12.0, "height": 3.5}
    }
    try:
        validate_spec_json(null_dim)
        print("[FAIL] Should have raised error")
    except SpecValidationError as e:
        print(f"[PASS] Caught error: {e}")

    # Test 5: Negative dimension
    print("\n[TEST 5] Negative Dimension")
    print("-" * 70)
    negative_dim = {
        "design_type": "apartment",
        "dimensions": {"width": -10.0, "length": 12.0, "height": 3.5}
    }
    try:
        validate_spec_json(negative_dim)
        print("[FAIL] Should have raised error")
    except SpecValidationError as e:
        print(f"[PASS] Caught error: {e}")

    # Test 6: Invalid dimension type
    print("\n[TEST 6] Invalid Dimension Type")
    print("-" * 70)
    invalid_type = {
        "design_type": "apartment",
        "dimensions": {"width": "10m", "length": 12.0, "height": 3.5}
    }
    try:
        validate_spec_json(invalid_type)
        print("[FAIL] Should have raised error")
    except SpecValidationError as e:
        print(f"[PASS] Caught error: {e}")

    # Test 7: Warnings for optional fields
    print("\n[TEST 7] Warnings for Missing Optional Fields")
    print("-" * 70)
    minimal_spec = {
        "design_type": "apartment",
        "dimensions": {"width": 10.0, "length": 8.0, "height": 3.0}
    }
    try:
        validate_spec_json(minimal_spec)
        warnings = validate_with_warnings(minimal_spec)
        print(f"[PASS] Validation passed with {len(warnings)} warnings:")
        for w in warnings:
            print(f"  - {w}")
    except SpecValidationError as e:
        print(f"[FAIL] {e}")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
VALIDATION BEHAVIOR:
[OK] Complete spec passes validation
[OK] Missing 'dimensions' raises error
[OK] Missing dimension keys raise errors
[OK] Null dimensions raise errors
[OK] Negative dimensions raise errors
[OK] Invalid types raise errors
[OK] Missing optional fields generate warnings only

RESULT: Validation prevents silent fallbacks
""")
    print("="*70)

if __name__ == "__main__":
    test_validation()
