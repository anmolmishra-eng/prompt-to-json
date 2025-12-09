#!/usr/bin/env python3
"""
Check why port 8000 server is slow to refresh
"""

import asyncio
import time
import httpx


async def check_server_performance():
    """Check server response times and identify bottlenecks"""
    print("Checking Server Performance on Port 8000")
    print("=" * 50)

    base_url = "http://localhost:8000"

    # Test endpoints with timing
    endpoints = [
        "/health",
        "/api/v1/health",
        "/docs",
        "/openapi.json"
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        for endpoint in endpoints:
            print(f"\nTesting: {endpoint}")

            try:
                start_time = time.time()
                response = await client.get(f"{base_url}{endpoint}")
                end_time = time.time()

                duration = (end_time - start_time) * 1000  # Convert to ms

                if response.status_code == 200:
                    print(f"  Status: OK ({response.status_code})")
                    print(f"  Response Time: {duration:.0f}ms")

                    if duration > 5000:  # > 5 seconds
                        print(f"  WARNING: Very slow response!")
                    elif duration > 2000:  # > 2 seconds
                        print(f"  WARNING: Slow response")
                    elif duration > 1000:  # > 1 second
                        print(f"  NOTICE: Moderate response time")
                    else:
                        print(f"  GOOD: Fast response")

                else:
                    print(f"  Status: ERROR ({response.status_code})")
                    print(f"  Response Time: {duration:.0f}ms")

            except Exception as e:
                print(f"  ERROR: {e}")

    print(f"\n" + "=" * 50)
    print("PERFORMANCE ANALYSIS")
    print("=" * 50)
    print("Common causes of slow server refresh:")
    print("1. Database connection issues")
    print("2. External service timeouts (Sentry, Supabase)")
    print("3. GPU detection taking too long")
    print("4. Heavy imports during startup")
    print("5. Storage validation delays")
    print("6. Prefect integration overhead")


if __name__ == "__main__":
    asyncio.run(check_server_performance())
