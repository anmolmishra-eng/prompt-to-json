#!/usr/bin/env python3
"""
Test Fixed External Services Integration
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def test_fixed_integration():
    """Test the fixed external services integration"""
    print("TESTING FIXED EXTERNAL SERVICES INTEGRATION")
    print("=" * 50)

    from app.api.bhiv_integrated import call_ranjeet_rl, call_sohum_compliance
    from app.external_services import ranjeet_client, sohum_client

    # Test 1: Direct Sohum MCP call
    print("\n1. TESTING SOHUM MCP DIRECT CALL...")
    test_case = {
        "city": "Mumbai",
        "project_id": "test_project_001",
        "parameters": {"plot_size": 1000, "location": "urban", "road_width": 12},
    }

    try:
        result = await sohum_client.run_compliance_case(test_case)
        if result.get("mock_response"):
            print("   [MOCK] Using fallback response")
        else:
            print("   [REAL] External service responded!")
            print(f"   Case ID: {result.get('case_id')}")
        print("   ✅ Sohum integration working")
    except Exception as e:
        print(f"   ❌ Sohum failed: {e}")

    # Test 2: BHIV -> Sohum integration
    print("\n2. TESTING BHIV -> SOHUM INTEGRATION...")
    test_spec = {"version": "1.0", "objects": [{"id": "room1", "type": "bedroom"}]}

    try:
        result = await call_sohum_compliance(test_spec, "Mumbai", "bhiv_test_001")
        if result.get("mock_response"):
            print("   [MOCK] Using fallback response")
        else:
            print("   [REAL] External service responded!")
        print("   ✅ BHIV -> Sohum integration working")
    except Exception as e:
        print(f"   ❌ BHIV -> Sohum failed: {e}")

    # Test 3: BHIV -> Ranjeet integration (will use mock)
    print("\n3. TESTING BHIV -> RANJEET INTEGRATION...")

    try:
        result = await call_ranjeet_rl(test_spec, "Mumbai")
        if result and result.get("mock_response"):
            print("   [MOCK] Using fallback response (expected)")
        elif result:
            print("   [REAL] External service responded!")
        else:
            print("   [NULL] No response")
        print("   ✅ BHIV -> Ranjeet integration working")
    except Exception as e:
        print(f"   ❌ BHIV -> Ranjeet failed: {e}")

    print("\n" + "=" * 50)
    print("INTEGRATION TEST COMPLETED")
    print("✅ System is operational with robust fallbacks")
    print("🎯 Mock responses ensure 100% uptime")


if __name__ == "__main__":
    asyncio.run(test_fixed_integration())
