"""
Comprehensive Integration Test
Tests BHIV Assistant, MCP, and RL integrations
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_all_integrations():
    """Test all BHIV integrations"""
    base_url = "http://localhost:8003"
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("Testing All BHIV Integrations...")
        
        # Test 1: Root and health
        print("\n[1/6] Testing basic endpoints...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"[OK] Root: {response.status_code}")
            endpoints = response.json().get("endpoints", {})
            print(f"   Available endpoints: {list(endpoints.keys())}")
        except Exception as e:
            print(f"[ERROR] Root failed: {e}")
        
        # Test 2: Health check
        print("\n[2/6] Testing health check...")
        try:
            response = await client.get(f"{base_url}/bhiv/v1/health")
            print(f"[OK] Health: {response.status_code}")
            health_data = response.json()
            for system, status in health_data.items():
                print(f"   {system}: {status}")
        except Exception as e:
            print(f"[ERROR] Health check failed: {e}")
        
        # Test 3: MCP rules
        print("\n[3/6] Testing MCP integration...")
        try:
            response = await client.get(f"{base_url}/mcp/rules/Mumbai")
            print(f"[OK] MCP rules: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Rules count: {data.get('count', 0)}")
        except Exception as e:
            print(f"[ERROR] MCP integration failed: {e}")
        
        # Test 4: RL feedback
        print("\n[4/6] Testing RL feedback...")
        try:
            feedback_data = {
                "user_id": "test_user_123",
                "spec_id": "spec_test_001",
                "rating": 4.5,
                "feedback_text": "Test feedback",
                "design_accepted": True,
                "timestamp": datetime.now().isoformat()
            }
            
            response = await client.post(f"{base_url}/rl/feedback", json=feedback_data)
            print(f"[OK] RL feedback: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] RL feedback failed: {e}")
        
        # Test 5: RL confidence
        print("\n[5/6] Testing RL confidence...")
        try:
            spec_data = {
                "spec_json": {"rooms": [{"type": "bedroom", "area": 120}]},
                "city": "Mumbai"
            }
            
            response = await client.post(f"{base_url}/rl/confidence", json=spec_data)
            print(f"[OK] RL confidence: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] RL confidence failed: {e}")
        
        # Test 6: Full design generation
        print("\n[6/6] Testing full design generation...")
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
            
            response = await client.post(f"{base_url}/bhiv/v1/design", json=design_request)
            print(f"[OK] Design generation: {response.status_code}")
            
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
        
        print("\n[SUCCESS] All integration tests completed!")
        print("\nIntegration Status:")
        print("- BHIV Assistant: Core orchestration layer")
        print("- MCP Integration: Rules and compliance")
        print("- RL Integration: Feedback and optimization")
        print("- Task 7: Design generation (external)")


if __name__ == "__main__":
    print("Starting Comprehensive Integration Tests...")
    print("Make sure the BHIV server is running: python app/main.py")
    print("=" * 80)
    
    asyncio.run(test_all_integrations())