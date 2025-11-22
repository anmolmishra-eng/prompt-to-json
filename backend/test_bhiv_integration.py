"""
Test BHIV Assistant integration with main backend
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_bhiv_integration():
    """Test BHIV Assistant integration"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("Testing BHIV Assistant Integration...")
        print("=" * 60)
        
        # Test 1: Health check
        print("\n[1/3] Testing BHIV health check...")
        try:
            response = await client.get(f"{base_url}/bhiv/v1/health")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                health_data = response.json()
                for system, status in health_data.items():
                    print(f"   {system}: {status}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Failed: {e}")
        
        # Test 2: Design generation
        print("\n[2/3] Testing BHIV design generation...")
        try:
            design_request = {
                "user_id": "test_user_123",
                "prompt": "modern 2BHK apartment with balcony",
                "city": "Mumbai",
                "project_id": "test_project_001",
                "context": {
                    "budget": 50000,
                    "style": "modern",
                    "dimensions": {"width": 30, "length": 40}
                }
            }
            
            print(f"   Request: {design_request['prompt']}")
            print(f"   City: {design_request['city']}")
            
            response = await client.post(
                f"{base_url}/bhiv/v1/design",
                json=design_request
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Request ID: {result.get('request_id')}")
                print(f"   Spec ID: {result.get('spec_id')}")
                print(f"   Processing Time: {result.get('processing_time_ms')}ms")
                print(f"   Compliance: {result.get('compliance', {}).get('compliant')}")
                print(f"   RL Optimization: {'Yes' if result.get('rl_optimization') else 'No'}")
                print(f"   Design Type: {result.get('spec_json', {}).get('design_type')}")
            else:
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   Failed: {e}")
        
        # Test 3: Main API health (ensure integration doesn't break existing)
        print("\n[3/3] Testing main API health...")
        try:
            response = await client.get(f"{base_url}/api/v1/health")
            print(f"   Main API Status: {response.status_code}")
            if response.status_code == 200:
                health = response.json()
                print(f"   Database: {health.get('database')}")
                print(f"   GPU: {health.get('gpu')}")
        except Exception as e:
            print(f"   Failed: {e}")
        
        print("\n" + "=" * 60)
        print("BHIV Integration Test Complete!")


if __name__ == "__main__":
    print("Starting BHIV Integration Tests...")
    print("Make sure the main backend is running: python -m uvicorn app.main:app --reload")
    print()
    
    asyncio.run(test_bhiv_integration())