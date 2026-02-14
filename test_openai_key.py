import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv("backend/.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def test_openai():
    print(f"Testing OpenAI API Key: {OPENAI_API_KEY[:20]}...")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": "Say 'test'"}],
                    "max_tokens": 5
                }
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                print("✅ OpenAI API key is working!")
                return True
            elif response.status_code == 429:
                print("⚠️ Rate limit exceeded. Wait or upgrade plan.")
                print(f"Response: {response.text}")
                return False
            elif response.status_code == 401:
                print("❌ Invalid API key")
                return False
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openai())
