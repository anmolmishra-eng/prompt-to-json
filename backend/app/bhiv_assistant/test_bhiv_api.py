"""
Test script for BHIV Assistant API
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_bhiv_api():
    """Test BHIV Assistant API endpoints"""
    base_url = "http://localhost:8003"
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("Testing BHIV Assistant API...")
        
        # Test 1: Root endpoint
        print("\n[1/3] Testing root endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"[OK] Root: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"[ERROR] Root failed: {e}")
        
        # Test 2: Health check
        print("\n[2/3] Testing health check...")
        try:
            response = await client.get(f"{base_url}/bhiv/v1/health")
            print(f"[OK] Health: {response.status_code}")
            health_data = response.json()
            for system, status in health_data.items():
                print(f"   {system}: {status}")
        except Exception as e:
            print(f"[ERROR] Health check failed: {e}")
        
        # Test 3: Design generation (mock request)
        print("\n[3/3] Testing design generation...")
        try:
            design_request = {
                "user_id": "test_user_123",
                "prompt": "modern 2BHK apartment with balcony",
                "city": "Mumbai",
                "project_id": "test_project_001",
                "context": {
                    "budget": 50000,
                    "style": "modern"
                }
            }
            
            print(f"   Request: {json.dumps(design_request, indent=2)}")
            
            response = await client.post(
                f"{base_url}/bhiv/v1/design",
                json=design_request
            )
            
            print(f"[OK] Design: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Request ID: {result.get('request_id')}")
                print(f"   Spec ID: {result.get('spec_id')}")
                print(f"   Processing Time: {result.get('processing_time_ms')}ms")
                print(f"   Compliance: {result.get('compliance', {}).get('compliant')}")
                print(f"   RL Optimization: {'Yes' if result.get('rl_optimization') else 'No'}")
            else:
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Design generation failed: {e}")
        
        print("\n[DONE] Test completed!")


if __name__ == "__main__":
    print("Starting BHIV Assistant API tests...")
    print("Make sure the server is running: python app/main.py")
    print("=" * 60)
    
    asyncio.run(test_bhiv_api())