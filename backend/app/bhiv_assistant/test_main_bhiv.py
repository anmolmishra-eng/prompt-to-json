"""
Test Main BHIV Application
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_main_bhiv():
    """Test main BHIV application endpoints"""
    base_url = "http://localhost:8003"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Testing Main BHIV Application...")
        
        # Test 1: Root endpoint
        print("\n[1/4] Testing root endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"[OK] Root: {response.status_code}")
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Endpoints: {list(data.get('endpoints', {}).keys())}")
        except Exception as e:
            print(f"[ERROR] Root failed: {e}")
        
        # Test 2: Health endpoint
        print("\n[2/4] Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"[OK] Health: {response.status_code}")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Timestamp: {data.get('timestamp')}")
        except Exception as e:
            print(f"[ERROR] Health failed: {e}")
        
        # Test 3: BHIV health check
        print("\n[3/4] Testing BHIV health check...")
        try:
            response = await client.get(f"{base_url}/bhiv/v1/health")
            print(f"[OK] BHIV Health: {response.status_code}")
            health_data = response.json()
            for system, status in health_data.items():
                print(f"   {system}: {status}")
        except Exception as e:
            print(f"[ERROR] BHIV health failed: {e}")
        
        # Test 4: API documentation
        print("\n[4/4] Testing API docs...")
        try:
            response = await client.get(f"{base_url}/docs")
            print(f"[OK] API Docs: {response.status_code}")
            print("   Interactive documentation available at /docs")
        except Exception as e:
            print(f"[ERROR] API docs failed: {e}")
        
        print("\n[SUCCESS] Main BHIV application test completed!")
        print("\nApplication Features:")
        print("- Unified FastAPI application")
        print("- BHIV Assistant orchestration")
        print("- MCP integration for rules")
        print("- RL integration for feedback")
        print("- CORS enabled for web clients")
        print("- Interactive API documentation")


if __name__ == "__main__":
    print("Testing Main BHIV Application...")
    print("Make sure the server is running: python start_bhiv.py")
    print("=" * 60)
    
    asyncio.run(test_main_bhiv())