#!/usr/bin/env python3
import asyncio

import httpx
from app.config import settings


async def check_service_health(name, url):
    """Check if service is live and responding"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try health endpoint first
            try:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    print(f"[OK] {name}: HEALTHY (health endpoint)")
                    return True
            except:
                pass

            # Try root endpoint
            try:
                response = await client.get(url)
                if response.status_code in [200, 404]:  # 404 is OK, means server is up
                    print(f"[OK] {name}: LIVE (root endpoint)")
                    return True
            except:
                pass

            print(f"[FAIL] {name}: DOWN")
            return False

    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return False


async def main():
    print("Checking live service URLs...")
    print("=" * 50)

    services = [
        ("Sohum MCP", settings.SOHUM_MCP_URL),
        ("Ranjeet RL", settings.RANJEET_RL_URL),
    ]

    results = []
    for name, url in services:
        print(f"Checking {name}: {url}")
        result = await check_service_health(name, url)
        results.append((name, url, result))
        print()

    print("=" * 50)
    print("SUMMARY:")
    for name, url, is_live in results:
        status = "LIVE" if is_live else "DOWN"
        print(f"{name}: {status}")


if __name__ == "__main__":
    asyncio.run(main())
