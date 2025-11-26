#!/usr/bin/env python3
"""
PDF to MCP Workflow Test
Quick test without starting Prefect server
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))


def test_rule_parsing():
    """Test compliance rule parsing"""
    try:
        from workflows.pdf_to_mcp_flow import parse_compliance_rules

        # Test text with various rules
        test_text = """
        FSI: 2.5
        Setback: 3 meter from road
        Maximum height: 15 meter
        Parking: 1 space per 100 sq ft
        """

        rules = parse_compliance_rules(test_text, "Mumbai")

        print(f"Rule parsing: {len(rules['rules'])} rules found")
        for rule in rules["rules"]:
            print(f"  - {rule['type']}: {rule.get('value', rule.get('spaces_per_area', 'N/A'))}")

        return len(rules["rules"]) > 0

    except Exception as e:
        print(f"Rule parsing failed: {e}")
        return False


def test_workflow_import():
    """Test that workflow can be imported"""
    try:
        from workflows.pdf_to_mcp_flow import pdf_to_mcp_flow

        print("Workflow import: SUCCESS")
        return True
    except Exception as e:
        print(f"Workflow import failed: {e}")
        return False


def main():
    """Run PDF workflow tests"""
    print("PDF to MCP Workflow Test")
    print("=" * 40)

    tests = [
        ("Workflow Import", test_workflow_import),
        ("Rule Parsing", test_rule_parsing),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"{test_name}: PASSED")
            else:
                print(f"{test_name}: FAILED")
        except Exception as e:
            print(f"{test_name}: ERROR - {e}")

    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("PDF to MCP workflow is ready!")
        return True
    else:
        print("Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
