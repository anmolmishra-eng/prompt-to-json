#!/usr/bin/env python3
"""
Complete test for compliance run_case endpoint
"""
import os
import sys

sys.path.append(".")

import json
from datetime import datetime

import requests


def test_run_case_complete():
    """Test compliance run_case endpoint with all supported cities"""
    print("Testing Compliance Run Case Endpoint")
    print("=" * 50)

    base_url = "http://localhost:8000/api/v1/compliance/run_case"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzY2MjQyMDc4fQ.AK8tllFORyGleQV7P24AtPaMl1HKCgxD1BV9O5azIJo",
        "Content-Type": "application/json",
    }

    # Test cases for different Indian cities
    test_cases = [
        {
            "name": "Mumbai Residential",
            "data": {
                "project_id": "proj_mumbai_tower",
                "case_id": "mumbai_residential_001",
                "city": "Mumbai",
                "document": "DCPR_2034.pdf",
                "parameters": {
                    "plot_size": 1000,
                    "location": "urban",
                    "road_width": 15,
                    "building_type": "residential",
                    "floors": 5,
                },
            },
        },
        {
            "name": "Pune Eco Housing",
            "data": {
                "project_id": "proj_pune_green",
                "case_id": "pune_eco_001",
                "city": "Pune",
                "document": "Pune_DCR.pdf",
                "parameters": {
                    "plot_size": 800,
                    "location": "suburban",
                    "road_width": 12,
                    "building_type": "eco_friendly",
                },
            },
        },
        {
            "name": "Ahmedabad Heritage",
            "data": {
                "project_id": "proj_ahmedabad_heritage",
                "case_id": "ahmedabad_heritage_001",
                "city": "Ahmedabad",
                "document": "Ahmedabad_DCR.pdf",
                "parameters": {"plot_size": 1200, "location": "heritage_zone", "road_width": 18},
            },
        },
        {
            "name": "Nashik Wine Tourism",
            "data": {
                "project_id": "proj_nashik_wine",
                "case_id": "nashik_tourism_001",
                "city": "Nashik",
                "document": "Nashik_DCR.pdf",
                "parameters": {"plot_size": 600, "location": "tourism_zone", "road_width": 10},
            },
        },
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['name']}...")

        try:
            response = requests.post(base_url, headers=headers, json=test_case["data"], timeout=30)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                # Verify response structure
                required_fields = ["project_id", "case_id", "city", "rules_applied", "confidence_score"]
                missing_fields = [field for field in required_fields if field not in data]

                if missing_fields:
                    print(f"   ❌ Missing fields: {missing_fields}")
                else:
                    print(f"   ✅ Response structure valid")
                    print(f"   City: {data.get('city')}")
                    print(f"   Rules Applied: {len(data.get('rules_applied', []))}")
                    print(f"   Confidence: {data.get('confidence_score')}")
                    print(f"   Authority: {data.get('clause_summaries', [{}])[0].get('authority', 'N/A')}")

                results.append(
                    {
                        "test": test_case["name"],
                        "status": "PASS",
                        "city": data.get("city"),
                        "rules_count": len(data.get("rules_applied", [])),
                        "confidence": data.get("confidence_score"),
                    }
                )
            else:
                print(f"   ❌ Error: {response.text}")
                results.append({"test": test_case["name"], "status": "FAIL", "error": response.text})

        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({"test": test_case["name"], "status": "ERROR", "error": str(e)})

    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")

    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")

    for result in results:
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        print(f"{status_icon} {result['test']}: {result['status']}")
        if result["status"] == "PASS":
            print(f"    City: {result['city']}, Rules: {result['rules_count']}, Confidence: {result['confidence']}")

    # Check local storage
    print(f"\n{'='*50}")
    print("STORAGE VERIFICATION")
    print(f"{'='*50}")

    # Check MCP rules
    mcp_dir = "data/mcp_rules"
    if os.path.exists(mcp_dir):
        files = os.listdir(mcp_dir)
        print(f"MCP Rules: {len(files)} files")
        for file in files:
            print(f"  - {file}")

    # Check PDF documents
    pdf_dir = "data/pdfs"
    if os.path.exists(pdf_dir):
        cities = os.listdir(pdf_dir)
        print(f"PDF Documents: {len(cities)} cities")
        for city in cities:
            print(f"  - {city}")

    return passed == total


if __name__ == "__main__":
    success = test_run_case_complete()
    if success:
        print(f"\n🎉 All compliance run_case tests PASSED!")
    else:
        print(f"\n⚠️ Some compliance run_case tests FAILED!")
