"""
OpenAI API Diagnostic Tool
Tests API key validity, rate limits, and model access
"""
import asyncio
import os
import httpx
from datetime import datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

async def test_openai_connection():
    """Test OpenAI API connectivity and diagnose issues"""

    print("=" * 60)
    print("OpenAI API Diagnostic Tool")
    print("=" * 60)
    print()

    # 1. Check API key format
    print("1️⃣  Checking API Key Format...")
    if not OPENAI_API_KEY:
        print("   ❌ FAIL: No API key found in environment")
        print("   💡 Set OPENAI_API_KEY in .env file")
        return

    if not OPENAI_API_KEY.startswith("sk-"):
        print(f"   ⚠️  WARNING: Key doesn't start with 'sk-': {OPENAI_API_KEY[:10]}...")
        print("   💡 OpenAI keys should start with 'sk-'")
    else:
        print(f"   ✅ PASS: Key format looks valid: {OPENAI_API_KEY[:15]}...{OPENAI_API_KEY[-4:]}")

    print()

    # 2. Test API connectivity
    print("2️⃣  Testing API Connectivity...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
            )

            if response.status_code == 200:
                print("   ✅ PASS: Successfully connected to OpenAI API")
                models = response.json()
                print(f"   📊 Available models: {len(models.get('data', []))} models")
            elif response.status_code == 401:
                print("   ❌ FAIL: Authentication failed (401)")
                print("   💡 API key is invalid or expired")
                print(f"   Response: {response.text[:200]}")
                return
            elif response.status_code == 429:
                print("   ⚠️  WARNING: Rate limit hit (429)")
                print("   💡 Too many requests - wait before retrying")
                print(f"   Response: {response.text[:200]}")
            else:
                print(f"   ❌ FAIL: Unexpected status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return
    except Exception as e:
        print(f"   ❌ FAIL: Connection error: {e}")
        return

    print()

    # 3. Test simple completion
    print("3️⃣  Testing Simple Completion...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Say 'test successful' in JSON format"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 50,
                    "response_format": {"type": "json_object"}
                }
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print("   ✅ PASS: Completion successful")
                print(f"   📝 Response: {content[:100]}")
                print(f"   💰 Tokens used: {result['usage']['total_tokens']}")
            elif response.status_code == 429:
                print("   ⚠️  WARNING: Rate limit exceeded")
                print("   💡 Your account may have hit usage limits")
                print(f"   Response: {response.text[:300]}")

                # Check if it's quota or rate limit
                if "quota" in response.text.lower():
                    print("   🚨 QUOTA EXCEEDED: Your OpenAI account has no credits")
                    print("   💡 Add credits at: https://platform.openai.com/account/billing")
                else:
                    print("   💡 Rate limit - wait 60 seconds and retry")
            elif response.status_code == 401:
                print("   ❌ FAIL: Authentication failed")
                print("   💡 API key is invalid")
            else:
                print(f"   ❌ FAIL: Status {response.status_code}")
                print(f"   Response: {response.text[:300]}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

    print()

    # 4. Test design generation prompt
    print("4️⃣  Testing Design Generation Prompt...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Generate a simple office design in JSON with objects array"
                        },
                        {
                            "role": "user",
                            "content": "Design a small office with desk and chair"
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "response_format": {"type": "json_object"}
                }
            )

            if response.status_code == 200:
                result = response.json()
                print("   ✅ PASS: Design generation works!")
                print(f"   💰 Cost estimate: ~${result['usage']['total_tokens'] * 0.000002:.6f}")
            elif response.status_code == 429:
                print("   ⚠️  WARNING: Rate limited on design generation")
            else:
                print(f"   ❌ FAIL: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

    print()
    print("=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)
    print()

    # Summary
    print("📋 SUMMARY:")
    print("   If all tests passed: AI generation should work")
    print("   If rate limited: Wait 60s or add Anthropic key as backup")
    print("   If quota exceeded: Add credits to OpenAI account")
    print("   If auth failed: Check API key in .env file")
    print()
    print("🔧 FIXES:")
    print("   1. Enhanced template fallback is now active")
    print("   2. Better retry logic with exponential backoff")
    print("   3. Automatic fallback to Anthropic if available")
    print()


if __name__ == "__main__":
    asyncio.run(test_openai_connection())
