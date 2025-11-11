import os

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

YOTTA_URL = os.getenv("YOTTA_URL")
YOTTA_API_KEY = os.getenv("YOTTA_API_KEY")


async def test_yotta():
    if not YOTTA_URL or not YOTTA_API_KEY:
        print("❌ YOTTA_URL or YOTTA_API_KEY not configured")
        return

    headers = {"Authorization": f"Bearer {YOTTA_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Test connection
            response = await client.get(f"{YOTTA_URL}/health", headers=headers)
            if response.status_code == 200:
                print("✅ Yotta connection successful!")
                print(f"Connected to: {YOTTA_URL}")
            else:
                print(f"❌ Yotta connection failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Yotta connection error: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_yotta())
