"""
Test Runner for BHIV Assistant
"""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run all BHIV tests"""
    print("Running BHIV Assistant Tests...")
    print("=" * 50)

    # Check if pytest is installed
    try:
        import pytest

        print("[OK] pytest is available")
    except ImportError:
        print("[ERROR] pytest not installed. Install with: pip install pytest pytest-asyncio")
        return False

    # Run tests
    test_commands = [
        # Integration tests
        ["python", "-m", "pytest", "tests/integration/test_bhiv_layer.py", "-v"],
        ["python", "-m", "pytest", "tests/integration/test_mcp_integration.py", "-v"],
        ["python", "-m", "pytest", "tests/integration/test_rl_integration.py", "-v"],
        # All tests
        ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
    ]

    for i, cmd in enumerate(test_commands, 1):
        print(f"\n[{i}/{len(test_commands)}] Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)

            if result.returncode == 0:
                print(f"[OK] Test passed")
                print(result.stdout)
            else:
                print(f"[ERROR] Test failed")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)

        except Exception as e:
            print(f"[ERROR] Failed to run test: {e}")

    print("\n" + "=" * 50)
    print("Test run completed!")

    # Quick validation
    print("\nRunning quick validation...")
    try:
        from app.main_bhiv import app

        print("[OK] Main BHIV app imports successfully")

        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/")
        if response.status_code == 200:
            print("[OK] Root endpoint responds correctly")
        else:
            print(f"[ERROR] Root endpoint failed: {response.status_code}")

    except Exception as e:
        print(f"[ERROR] Validation failed: {e}")


if __name__ == "__main__":
    run_tests()
