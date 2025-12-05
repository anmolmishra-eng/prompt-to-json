#!/usr/bin/env python3
"""
Test Sohum MCP with correct data format
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def test_sohum_correct_format():
    """Test Sohum MCP with the correct data format"""
    print("TESTING SOHUM MCP WITH CORRECT FORMAT")
    print("=" * 50)

    from datetime import datetime

    from app.external_services import sohum_client

    # Try the format that Sohum's service expects
    test_cases = [
        # Format 1: Simple case
        {"city": "Mumbai", "project_id": "test_001", "case_id": "mumbai_test_001"},
        # Format 2: With parameters
        {
            "city": "Mumbai",
            "project_id": "test_002",
            "case_id": "mumbai_test_002",
            "parameters": {"plot_size": 1000, "location": "urban", "road_width": 12},
        },
        # Format 3: Minimal
        {"case_id": "mumbai_test_003"},
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        try:
            result = await sohum_client.run_compliance_case(test_case)
            print(f"   SUCCESS: {result.get('case_id', 'No case_id')}")
            if not result.get("mock_response"):
                print("   REAL SERVICE RESPONDED!")
                return True
        except Exception as e:
            print(f"   ERROR: {e}")

    print("\nAll formats failed - using mock responses")
    return False


if __name__ == "__main__":
    success = asyncio.run(test_sohum_correct_format())
