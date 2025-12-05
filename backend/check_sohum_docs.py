#!/usr/bin/env python3
"""
Check Sohum's API documentation to understand the correct format
"""
import asyncio

import httpx


async def check_sohum_docs():
    """Get API documentation from Sohum's service"""
    base_url = "https://ai-rule-api-w7z5.onrender.com"

    print("CHECKING SOHUM'S API DOCUMENTATION")
    print("=" * 45)

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            # Get OpenAPI spec
            response = await client.get(f"{base_url}/openapi.json")
            if response.status_code == 200:
                spec = response.json()

                # Check /run_case endpoint
                if "paths" in spec and "/run_case" in spec["paths"]:
                    run_case = spec["paths"]["/run_case"]
                    if "post" in run_case:
                        post_spec = run_case["post"]
                        print("POST /run_case specification:")
                        print(f"  Summary: {post_spec.get('summary', 'N/A')}")

                        if "requestBody" in post_spec:
                            req_body = post_spec["requestBody"]
                            if "content" in req_body and "application/json" in req_body["content"]:
                                schema = req_body["content"]["application/json"].get("schema", {})
                                print(f"  Request Schema: {schema}")

                                # Show example if available
                                if "example" in req_body["content"]["application/json"]:
                                    example = req_body["content"]["application/json"]["example"]
                                    print(f"  Example: {example}")

                # Test with a proper request
                print("\nTesting with inferred format...")
                test_data = {
                    "project_id": "test_project_001",
                    "case_id": "mumbai_case_001",
                    "city": "Mumbai",
                    "document": "DCPR_2034.pdf",
                    "parameters": {"plot_size": 1000, "location": "urban", "road_width": 12},
                }

                response = await client.post(f"{base_url}/run_case", json=test_data)
                print(f"Test response: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"SUCCESS: {result}")
                    return True
                else:
                    print(f"Error: {response.text}")

        except Exception as e:
            print(f"Error checking docs: {e}")

    return False


if __name__ == "__main__":
    asyncio.run(check_sohum_docs())
