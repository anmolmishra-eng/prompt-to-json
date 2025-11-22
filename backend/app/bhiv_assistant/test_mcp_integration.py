"""
Test MCP Integration Module
"""

import asyncio
import json

import httpx


async def test_mcp_endpoints():
    """Test MCP integration endpoints"""
    base_url = "http://localhost:8003"

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Testing MCP Integration...")

        # Test 1: Get Mumbai rules
        print("\n[1/3] Testing Mumbai rules...")
        try:
            response = await client.get(f"{base_url}/mcp/rules/Mumbai")
            print(f"[OK] Mumbai rules: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   City: {data.get('city')}")
                print(f"   Rules count: {data.get('count')}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"[ERROR] Mumbai rules failed: {e}")

        # Test 2: Query rules
        print("\n[2/3] Testing rule query...")
        try:
            response = await client.post(
                f"{base_url}/mcp/rules/query", params={"city": "Mumbai", "query": "What is FSI for residential?"}
            )
            print(f"[OK] Rule query: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Query: {data.get('query')}")
                print(f"   Results: {len(data.get('results', []))}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"[ERROR] Rule query failed: {e}")

        # Test 3: Get metadata
        print("\n[3/3] Testing metadata...")
        try:
            response = await client.get(f"{base_url}/mcp/metadata/Mumbai")
            print(f"[OK] Metadata: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   City: {data.get('city')}")
                print(f"   Rule count: {data.get('rule_count', 0)}")
                print(f"   Last updated: {data.get('last_updated', 'N/A')}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"[ERROR] Metadata failed: {e}")

        print("\n[DONE] MCP integration test completed!")


if __name__ == "__main__":
    print("Starting MCP Integration tests...")
    print("Make sure the BHIV server is running: python app/main.py")
    print("=" * 60)

    asyncio.run(test_mcp_endpoints())
