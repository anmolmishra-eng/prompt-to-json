"""Test Groq API Key"""
import os
import sys
import httpx
import asyncio
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / "backend" / ".env"
    load_dotenv(env_path)
except:
    pass

async def test_groq():
    key = os.getenv("GROQ_API_KEY", "")

    if not key:
        print("[ERROR] No GROQ_API_KEY found")
        return

    print(f"[INFO] Testing Groq key: {key[:20]}...{key[-4:]}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": "Say 'Groq is working!'"}],
                    "max_tokens": 20
                }
            )

            print(f"[STATUS] HTTP {response.status_code}")

            if response.status_code == 200:
                print("[SUCCESS] Groq API is WORKING!")
                result = response.json()
                print(f"[RESPONSE] {result['choices'][0]['message']['content']}")
                print("\n[NEXT] Restart your backend server to use Groq AI!")
            else:
                print(f"[ERROR] {response.text[:300]}")

    except Exception as e:
        print(f"[EXCEPTION] {e}")

if __name__ == "__main__":
    asyncio.run(test_groq())
