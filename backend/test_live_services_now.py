#!/usr/bin/env python3
import asyncio

import httpx


async def test_services_directly():
    """Test services directly to verify they're actually working"""
    services = [
        ("Sohum MCP", "https://ai-rule-api-w7z5.onrender.com"),
        ("Ranjeet RL", "https://land-utilization-rl.onrender.com"),
    ]

    print("DIRECT SERVICE TEST:")
    print("=" * 30)

    for name, url in services:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                print(f"{name}: Status {response.status_code} - LIVE")
        except Exception as e:
            print(f"{name}: ERROR - {str(e)[:50]}...")


if __name__ == "__main__":
    asyncio.run(test_services_directly())
