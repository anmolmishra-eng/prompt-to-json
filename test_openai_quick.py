"""Quick OpenAI API Test"""
import os
import sys
import httpx
import asyncio
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / "backend" / ".env"
    load_dotenv(env_path)
except:
    pass

async def test_openai():
    key = os.getenv("OPENAI_API_KEY", "")

    if not key:
        print("[ERROR] No OPENAI_API_KEY found in environment")
        return

    print(f"[INFO] Testing key: {key[:20]}...{key[-4:]}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": "Say 'test'"}],
                    "max_tokens": 10
                }
            )

            print(f"[STATUS] HTTP {response.status_code}")

            if response.status_code == 200:
                print("[SUCCESS] OpenAI API is WORKING!")
                result = response.json()
                print(f"[RESPONSE] {result['choices'][0]['message']['content']}")
            elif response.status_code == 429:
                print("[WARNING] RATE LIMITED - Too many requests")
                print(f"Response: {response.text[:300]}")
            elif response.status_code == 401:
                print("[ERROR] AUTHENTICATION FAILED - Invalid API key")
            else:
                print(f"[ERROR] {response.text[:300]}")

    except Exception as e:
        print(f"[EXCEPTION] {e}")

if __name__ == "__main__":
    asyncio.run(test_openai())
