#!/usr/bin/env python3
"""
Check Sohum's actual API endpoints and format
"""
import asyncio

import httpx


async def check_sohum_api():
    """Check what endpoints Sohum's service actually has"""
    base_url = "https://ai-rule-api-w7z5.onrender.com"

    print("CHECKING SOHUM'S ACTUAL API")
    print("=" * 40)

    async with httpx.AsyncClient(timeout=30) as client:
        # Check root
        try:
            response = await client.get(base_url)
            print(f"Root: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Root error: {e}")

        # Check common endpoints
        endpoints = ["/", "/docs", "/health", "/api", "/compliance", "/run_case", "/api/docs"]

        for endpoint in endpoints:
            try:
                response = await client.get(f"{base_url}{endpoint}")
                print(f"{endpoint}: {response.status_code}")
                if response.status_code == 200 and "json" in response.headers.get("content-type", ""):
                    print(f"  JSON: {response.json()}")
            except Exception as e:
                print(f"{endpoint}: ERROR - {e}")


if __name__ == "__main__":
    asyncio.run(check_sohum_api())
