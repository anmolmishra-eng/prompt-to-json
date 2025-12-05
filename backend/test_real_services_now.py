#!/usr/bin/env python3
"""
Test Real Services - Now tries real services first
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def test_real_services_first():
    """Test that system now tries real services first"""
    print("TESTING REAL SERVICES FIRST APPROACH")
    print("=" * 50)

    from datetime import datetime

    from app.api.bhiv_integrated import call_ranjeet_rl, call_sohum_compliance
    from app.external_services import ranjeet_client, service_manager, sohum_client

    # Clear any previous health status to force fresh attempts
    service_manager.service_health.clear()
    service_manager.last_health_check.clear()

    # Test 1: Sohum MCP - should try real service first
    print("\n1. TESTING SOHUM MCP (REAL SERVICE FIRST)...")
    test_case = {
        "city": "Mumbai",
        "project_id": "test_project_001",
        "parameters": {"plot_size": 1000, "location": "urban", "road_width": 12},
    }

    try:
        # Increase timeout for real processing
        original_timeout = sohum_client.timeout
        sohum_client.timeout = 90  # 90 seconds for AI processing

        print("   Attempting real service call...")
        result = await sohum_client.run_compliance_case(test_case)

        if result.get("mock_response"):
            print("   [FALLBACK] Real service failed, using mock")
        else:
            print("   [SUCCESS] Real service responded!")
            print(f"   Case ID: {result.get('case_id')}")
            print(f"   Rules Applied: {len(result.get('rules_applied', []))}")

    except Exception as e:
        print(f"   [ERROR] Real service failed: {str(e)[:100]}...")
        print("   [FALLBACK] Will use mock response")
    finally:
        sohum_client.timeout = original_timeout

    # Test 2: BHIV integration - should try real service first
    print("\n2. TESTING BHIV INTEGRATION (REAL SERVICE FIRST)...")
    test_spec = {"version": "1.0", "objects": [{"id": "room1", "type": "bedroom"}]}

    try:
        print("   Attempting BHIV -> Sohum integration...")
        result = await call_sohum_compliance(test_spec, "Mumbai", "bhiv_test_001")

        if result.get("mock_response"):
            print("   [FALLBACK] Using mock response")
        else:
            print("   [SUCCESS] Real service integration working!")
            print(f"   Case ID: {result.get('case_id')}")

    except Exception as e:
        print(f"   [ERROR] BHIV integration failed: {str(e)[:100]}...")

    # Test 3: Ranjeet RL - should try real service first
    print("\n3. TESTING RANJEET RL (REAL SERVICE FIRST)...")

    try:
        print("   Attempting Ranjeet RL service...")
        result = await call_ranjeet_rl(test_spec, "Mumbai")

        if result and result.get("mock_response"):
            print("   [FALLBACK] Real service unavailable, using mock")
        elif result:
            print("   [SUCCESS] Real RL service responded!")
            print(f"   Confidence: {result.get('confidence')}")
        else:
            print("   [NULL] No response")

    except Exception as e:
        print(f"   [ERROR] RL service failed: {str(e)[:100]}...")

    # Show final service health
    print("\n4. FINAL SERVICE HEALTH STATUS...")
    for service, status in service_manager.service_health.items():
        last_check = service_manager.last_health_check.get(service)
        print(f"   {service}: {status} (checked: {last_check})")

    print("\n" + "=" * 50)
    print("REAL SERVICES TEST COMPLETED")
    print("[INFO] System now tries real services first")
    print("[INFO] Falls back to mock only when real services fail")


if __name__ == "__main__":
    asyncio.run(test_real_services_first())
