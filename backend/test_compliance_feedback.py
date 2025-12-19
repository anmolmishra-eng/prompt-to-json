#!/usr/bin/env python3
"""
Test compliance feedback endpoint
"""
import os
import sys

sys.path.append(".")

import json

import requests


def test_compliance_feedback():
    """Test compliance feedback endpoint"""
    print("Testing Compliance Feedback Endpoint")
    print("=" * 40)

    base_url = "http://localhost:8000/api/v1/compliance/feedback"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzY2MjQyMDc4fQ.AK8tllFORyGleQV7P24AtPaMl1HKCgxD1BV9O5azIJo",
        "Content-Type": "application/json",
    }

    # Test cases
    test_cases = [
        {
            "name": "Positive Feedback",
            "data": {
                "project_id": "proj_test_positive",
                "case_id": "case_positive_001",
                "input_case": {"city": "Mumbai", "parameters": {"plot_size": 1000, "location": "urban"}},
                "output_report": {"rules_applied": ["MUM-FSI-URBAN"], "confidence_score": 0.9},
                "user_feedback": "up",
            },
        },
        {
            "name": "Negative Feedback",
            "data": {
                "project_id": "proj_test_negative",
                "case_id": "case_negative_001",
                "input_case": {"city": "Pune", "parameters": {"plot_size": 800, "location": "suburban"}},
                "output_report": {"rules_applied": ["PUNE-FSI-SUBURBAN"], "confidence_score": 0.2},
                "user_feedback": "down",
            },
        },
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['name']}...")

        try:
            response = requests.post(base_url, headers=headers, json=test_case["data"], timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   Feedback ID: {data.get('feedback_id')}")
                print(f"   Status: {data.get('status')}")
                print(f"   Message: {data.get('message')}")
                results.append({"test": test_case["name"], "status": "PASS"})
            else:
                print(f"   Error: {response.text}")
                results.append({"test": test_case["name"], "status": "FAIL"})

        except Exception as e:
            print(f"   Exception: {e}")
            results.append({"test": test_case["name"], "status": "ERROR"})

    # Summary
    print(f"\nSUMMARY:")
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")

    return passed == total


if __name__ == "__main__":
    success = test_compliance_feedback()
    if success:
        print("\nCompliance feedback tests PASSED!")
    else:
        print("\nSome compliance feedback tests FAILED!")
