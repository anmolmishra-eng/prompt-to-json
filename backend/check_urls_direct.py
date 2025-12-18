#!/usr/bin/env python3
import asyncio

import httpx


async def check_service_direct(name, url):
    """Check service directly without config"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            print(f"[OK] {name}: Status {response.status_code}")
            return True
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return False


async def main():
    print("Direct URL Check:")
    print("=" * 40)

    services = [
        ("Sohum MCP", "https://ai-rule-api-w7z5.onrender.com"),
        ("Ranjeet RL", "https://land-utilization-rl.onrender.com"),
    ]

    for name, url in services:
        print(f"Testing {name}: {url}")
        await check_service_direct(name, url)
        print()


if __name__ == "__main__":
    asyncio.run(main())
