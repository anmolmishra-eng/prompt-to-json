"""
Test RL Feedback Integration
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_rl_endpoints():
    """Test RL feedback integration endpoints"""
    base_url = "http://localhost:8003"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Testing RL Feedback Integration...")
        
        # Test 1: Submit feedback
        print("\n[1/2] Testing feedback submission...")
        try:
            feedback_data = {
                "user_id": "test_user_123",
                "spec_id": "spec_test_001",
                "rating": 4.5,
                "feedback_text": "Great design, love the layout!",
                "design_accepted": True,
                "timestamp": datetime.now().isoformat()
            }
            
            response = await client.post(
                f"{base_url}/rl/feedback",
                json=feedback_data
            )
            
            print(f"[OK] Feedback submission: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success', False)}")
                print(f"   Weights updated: {result.get('weights_updated', False)}")
            else:
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Feedback submission failed: {e}")
        
        # Test 2: Get confidence score
        print("\n[2/2] Testing confidence score...")
        try:
            spec_data = {
                "spec_json": {
                    "rooms": [
                        {"type": "bedroom", "area": 120},
                        {"type": "living_room", "area": 200}
                    ],
                    "total_area": 800,
                    "style": "modern"
                },
                "city": "Mumbai"
            }
            
            response = await client.post(
                f"{base_url}/rl/confidence",
                json=spec_data
            )
            
            print(f"[OK] Confidence score: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Confidence: {result.get('confidence')}")
                print(f"   City: {result.get('city')}")
            else:
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Confidence score failed: {e}")
        
        print("\n[DONE] RL integration test completed!")


if __name__ == "__main__":
    print("Starting RL Feedback Integration tests...")
    print("Make sure the BHIV server is running: python app/main.py")
    print("=" * 60)
    
    asyncio.run(test_rl_endpoints())