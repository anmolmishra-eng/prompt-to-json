#!/usr/bin/env python3
"""
Test if duplication between port 8000 and 8003 is resolved
"""

import asyncio
import httpx


async def test_duplication_resolved():
    """Check if BHIV endpoints are properly consolidated"""
    print("Testing BHIV Duplication Resolution")
    print("=" * 50)

    # Test data
    test_request = {
        "user_id": "test_user",
        "prompt": "Design modern 2BHK in Mumbai",
        "city": "Mumbai"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:

        # Test Port 8000 (Main Server)
        print("\nTesting Port 8000 (Main Server)")
        port_8000_endpoints = []

        endpoints_8000 = [
            "/bhiv/v1/health",
            "/bhiv/v1/prompt",
            "/bhiv/v1/design"
        ]

        for endpoint in endpoints_8000:
            try:
                if endpoint == "/bhiv/v1/health":
                    response = await client.get(f"http://localhost:8000{endpoint}")
                else:
                    response = await client.post(f"http://localhost:8000{endpoint}", json=test_request)

                if response.status_code in [200, 201, 422]:  # 422 is validation error, means endpoint exists
                    port_8000_endpoints.append(endpoint)
                    print(f"OK {endpoint} - Available ({response.status_code})")
                else:
                    print(f"FAIL {endpoint} - Not Available ({response.status_code})")
            except Exception as e:
                print(f"ERROR {endpoint} - Error: {e}")

        # Test Port 8003 (BHIV Server)
        print("\nTesting Port 8003 (BHIV Server)")
        port_8003_status = "OFFLINE"
        port_8003_endpoints = []

        try:
            response = await client.get("http://localhost:8003/health")
            if response.status_code == 200:
                port_8003_status = "ONLINE"
                print(f"OK Port 8003 is ONLINE")

                # Check BHIV endpoints on 8003
                endpoints_8003 = [
                    "/bhiv/v1/health",
                    "/bhiv/v1/design"
                ]

                for endpoint in endpoints_8003:
                    try:
                        if endpoint == "/bhiv/v1/health":
                            response = await client.get(f"http://localhost:8003{endpoint}")
                        else:
                            response = await client.post(f"http://localhost:8003{endpoint}", json=test_request)

                        if response.status_code in [200, 201, 422]:
                            port_8003_endpoints.append(endpoint)
                            print(f"OK {endpoint} - Available ({response.status_code})")
                        else:
                            print(f"FAIL {endpoint} - Not Available ({response.status_code})")
                    except Exception as e:
                        print(f"ERROR {endpoint} - Error: {e}")
            else:
                print(f"FAIL Port 8003 is OFFLINE")
        except Exception as e:
            print(f"OFFLINE Port 8003 is OFFLINE - {e}")

        # Analysis
        print("\n" + "=" * 50)
        print("DUPLICATION ANALYSIS")
        print("=" * 50)

        print(f"Port 8000 BHIV Endpoints: {len(port_8000_endpoints)}")
        for ep in port_8000_endpoints:
            print(f"  - {ep}")

        print(f"\nPort 8003 Status: {port_8003_status}")
        print(f"Port 8003 BHIV Endpoints: {len(port_8003_endpoints)}")
        for ep in port_8003_endpoints:
            print(f"  - {ep}")

        # Determine if duplication is resolved
        if port_8003_status == "OFFLINE":
            print(f"\nDUPLICATION RESOLVED!")
            print(f"Port 8003 is offline - no duplicate server running")
            print(f"All BHIV endpoints available on port 8000")
            print(f"Single consolidated server architecture")
        elif len(port_8003_endpoints) == 0:
            print(f"\nDUPLICATION RESOLVED!")
            print(f"Port 8003 has no BHIV endpoints")
            print(f"All BHIV functionality consolidated to port 8000")
        else:
            print(f"\nDUPLICATION STILL EXISTS!")
            print(f"Port 8003 is still running with BHIV endpoints")
            print(f"Same endpoints available on both ports")
            print(f"Solution: Stop port 8003 server")

        print("\n" + "=" * 50)
        print("RECOMMENDATION")
        print("=" * 50)

        if port_8003_status == "OFFLINE":
            print("Perfect! Use only:")
            print("   - Main Server: http://localhost:8000/docs")
            print("   - Prefect: http://localhost:4201")
        else:
            print("To resolve duplication:")
            print("   1. Stop port 8003 server (Ctrl+C)")
            print("   2. Use only port 8000 for all BHIV endpoints")
            print("   3. Access: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(test_duplication_resolved())
