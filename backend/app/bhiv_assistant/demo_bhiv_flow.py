"""
Demo: BHIV Assistant API Flow
Shows how the orchestration works without running the server
"""

import json
from datetime import datetime


def demo_bhiv_flow():
    """Demonstrate BHIV Assistant orchestration flow"""
    
    print("🚀 BHIV AI Assistant - Orchestration Flow Demo")
    print("=" * 60)
    
    # Step 1: User Request
    print("\n📝 STEP 1: User Request")
    user_request = {
        "user_id": "demo_user_123",
        "prompt": "modern 2BHK apartment with balcony and parking",
        "city": "Mumbai",
        "project_id": "demo_project_001",
        "context": {
            "budget": 75000,
            "style": "modern",
            "area_sqft": 800
        }
    }
    print(f"Request: {json.dumps(user_request, indent=2)}")
    
    # Step 2: Task 7 Call (Simulated)
    print("\n🔄 STEP 2: Task 7 - Generate Spec")
    print("URL: http://localhost:8000/api/v1/generate")
    task7_response = {
        "spec_id": "spec_20241122_143022",
        "spec_json": {
            "rooms": [
                {"type": "living_room", "area": 300, "furniture": ["sofa", "tv_unit"]},
                {"type": "bedroom_1", "area": 200, "furniture": ["bed", "wardrobe"]},
                {"type": "bedroom_2", "area": 150, "furniture": ["bed", "study_table"]},
                {"type": "kitchen", "area": 100, "furniture": ["cabinets", "counter"]},
                {"type": "balcony", "area": 50, "furniture": ["chairs"]}
            ],
            "total_area": 800,
            "parking": True
        },
        "preview_url": "https://bhiv-previews.s3.amazonaws.com/spec_20241122_143022.glb"
    }
    print(f"✅ Generated spec: {task7_response['spec_id']}")
    print(f"   Total area: {task7_response['spec_json']['total_area']} sqft")
    
    # Step 3: Sohum's MCP Call (Simulated)
    print("\n🏛️ STEP 3: Sohum's MCP - Compliance Check")
    print("URL: https://ai-rule-api-w7z5.onrender.com/compliance/run_case")
    mcp_response = {
        "case_id": "mumbai_case_001",
        "compliant": True,
        "violations": [],
        "geometry_url": "https://mcp-geometry.s3.amazonaws.com/mumbai_case_001.glb",
        "rules_applied": ["MUM-FSI-R15-20", "MUM-PARKING-REQ", "MUM-BALCONY-MIN"]
    }
    print(f"✅ Compliance: {'PASSED' if mcp_response['compliant'] else 'FAILED'}")
    print(f"   Rules applied: {len(mcp_response['rules_applied'])}")
    
    # Step 4: Ranjeet's RL Call (Simulated)
    print("\n🤖 STEP 4: Ranjeet's RL - Land Optimization")
    print("URL: https://api.yotta.com/rl/predict")
    rl_response = {
        "optimized_layout": {
            "efficiency_score": 0.87,
            "space_utilization": 0.92,
            "suggested_changes": [
                "Move kitchen closer to living area",
                "Optimize bedroom 2 layout for better space"
            ]
        },
        "confidence": 0.85,
        "reward_score": 8.7
    }
    print(f"✅ RL Optimization: {rl_response['confidence']:.0%} confidence")
    print(f"   Efficiency score: {rl_response['optimized_layout']['efficiency_score']:.0%}")
    
    # Step 5: BHIV Response (Aggregated)
    print("\n🎯 STEP 5: BHIV Assistant - Unified Response")
    processing_time = 2850  # ms
    bhiv_response = {
        "request_id": "bhiv_20241122_143022",
        "spec_id": task7_response["spec_id"],
        "spec_json": task7_response["spec_json"],
        "preview_url": task7_response["preview_url"],
        "compliance": {
            "compliant": mcp_response["compliant"],
            "violations": mcp_response["violations"],
            "geometry_url": mcp_response["geometry_url"],
            "case_id": mcp_response["case_id"]
        },
        "rl_optimization": {
            "optimized_layout": rl_response["optimized_layout"],
            "confidence": rl_response["confidence"],
            "reward_score": rl_response["reward_score"]
        },
        "processing_time_ms": processing_time,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"✅ Complete response generated")
    print(f"   Processing time: {processing_time}ms")
    print(f"   All systems integrated: Task 7 + Sohum MCP + Ranjeet RL")
    
    # Summary
    print("\n📊 INTEGRATION SUMMARY")
    print("-" * 60)
    print("✅ Task 7: Spec generation from natural language")
    print("✅ Sohum MCP: Compliance validation with Mumbai rules")
    print("✅ Ranjeet RL: Land utilization optimization")
    print("✅ BHIV Assistant: Unified orchestration layer")
    
    print(f"\n🎉 Demo completed! BHIV Assistant successfully orchestrated all 3 systems.")
    
    return bhiv_response


if __name__ == "__main__":
    result = demo_bhiv_flow()
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start BHIV server: python app/main.py")
    print("3. Test with: python test_bhiv_api.py")
    print("4. Access docs: http://localhost:8003/docs")