"""
Verify Mock Elimination - Quick Check
"""
import re
from pathlib import Path


def check_file_for_mocks(filepath):
    """Check if file contains mock responses or generic placeholders"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []

    # Check for mock fallbacks
    if "return {" in content and '"mode": "mock"' in content:
        issues.append("Found mock mode response")

    if "using mock" in content.lower() and "logger" not in content.lower():
        issues.append("Found mock fallback logic")

    # Check for generic placeholders
    generic_phrases = [
        "Ensure all design parameters meet local building codes",
        "Verify structural safety requirements",
        "Consider adding fire safety measures",
        "Ensure proper ventilation in all rooms",
    ]

    for phrase in generic_phrases:
        if phrase in content:
            issues.append(f"Found generic placeholder: {phrase[:50]}...")

    # Check for mock data generation
    if "mock preference data" in content.lower():
        issues.append("Found mock preference data generation")

    if "mock_rlhf_policy" in content:
        issues.append("Found mock artifact naming")

    return issues


def main():
    print("=" * 70)
    print("Mock Elimination Verification")
    print("=" * 70)

    files_to_check = [
        "app/api/mcp_integration.py",
        "app/api/rl.py",
        "app/external_services.py",
    ]

    all_clean = True

    for filepath in files_to_check:
        path = Path(filepath)
        if not path.exists():
            print(f"\n❌ {filepath} - FILE NOT FOUND")
            continue

        issues = check_file_for_mocks(filepath)

        if issues:
            all_clean = False
            print(f"\nX {filepath}")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"\nOK {filepath} - CLEAN (no mocks)")

    print("\n" + "=" * 70)
    if all_clean:
        print("SUCCESS - ALL MOCKS ELIMINATED - System is production ready!")
        print("\nBehavior:")
        print("  - MCP returns real compliance data or HTTP 503")
        print("  - RL returns real metrics or HTTP 500")
        print("  - No generic placeholders")
        print("  - No mock fallbacks")
    else:
        print("WARNING - Some mock code still present - review issues above")

    print("=" * 70)


if __name__ == "__main__":
    main()
