#!/usr/bin/env python3
import asyncio
import time

import httpx


async def wake_service(name, url):
    """Wake up Render service and wait for it to respond"""
    print(f"Waking up {name}...")

    for attempt in range(1, 11):  # Try for 10 attempts
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                start_time = time.time()
                response = await client.get(url)
                elapsed = time.time() - start_time

                if response.status_code in [200, 404]:
                    print(f"[OK] {name}: AWAKE (attempt {attempt}, {elapsed:.1f}s)")
                    return True
                else:
                    print(f"[WAIT] {name}: Status {response.status_code} (attempt {attempt})")

        except Exception as e:
            print(f"[WAIT] {name}: Still waking... (attempt {attempt})")

        if attempt < 10:
            await asyncio.sleep(30)  # Wait 30 seconds between attempts

    print(f"[TIMEOUT] {name}: Failed to wake up after 5 minutes")
    return False


async def main():
    print("Waking up Render services...")
    print("This may take up to 5 minutes...")
    print("=" * 50)

    services = [
        ("Sohum MCP", "https://ai-rule-api-w7z5.onrender.com"),
        ("Ranjeet RL", "https://land-utilization-rl.onrender.com"),
    ]

    # Wake services in parallel
    tasks = [wake_service(name, url) for name, url in services]
    results = await asyncio.gather(*tasks)

    print("=" * 50)
    print("WAKE-UP RESULTS:")
    for i, (name, url) in enumerate(services):
        status = "AWAKE" if results[i] else "FAILED"
        print(f"{name}: {status}")


if __name__ == "__main__":
    asyncio.run(main())
