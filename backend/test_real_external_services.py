#!/usr/bin/env python3
"""
Test Real External Services
Forces real service calls and shows actual vs mock responses
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def test_real_services():
    """Test actual external service calls"""
    print("=" * 60)
    print("TESTING REAL EXTERNAL SERVICES")
    print("=" * 60)

    from app.config import settings
    from app.external_services import ranjeet_client, service_manager, sohum_client

    print(f"Sohum MCP URL: {settings.SOHUM_MCP_URL}")
    print(f"Ranjeet RL URL: {settings.RANJEET_RL_URL}")

    # Test Sohum MCP - Force real call
    print("\n1. TESTING SOHUM MCP (REAL CALL)...")
    test_case = {
        "city": "Mumbai",
        "project_id": "test_real_001",
        "parameters": {"plot_size": 1000, "location": "urban", "road_width": 12},
    }

    try:
        # Force service to be considered available
        service_manager.service_health["sohum_mcp"] = "healthy"
        service_manager.last_health_check["sohum_mcp"] = datetime.now()

        result = await sohum_client.run_compliance_case(test_case)

        if result.get("mock_response"):
            print("   [MOCK] Service unavailable - using mock response")
            print(f"   Case ID: {result.get('case_id')}")
        else:
            print("   [REAL] External service responded!")
            print(f"   Case ID: {result.get('case_id')}")
            print(f"   Rules Applied: {len(result.get('rules_applied', []))}")

    except Exception as e:
        print(f"   [ERROR] Service call failed: {e}")

    # Test Ranjeet RL - Force real call
    print("\n2. TESTING RANJEET RL (REAL CALL)...")
    test_spec = {
        "objects": [{"id": "room1", "type": "bedroom", "area": 150}],
        "materials": [{"id": "mat1", "type": "concrete"}],
    }

    try:
        # Force service to be considered available
        service_manager.service_health["ranjeet_rl"] = "healthy"
        service_manager.last_health_check["ranjeet_rl"] = datetime.now()

        result = await ranjeet_client.optimize_design(test_spec, "Mumbai")

        if result and result.get("mock_response"):
            print("   [MOCK] Service unavailable - using mock response")
            print(f"   Confidence: {result.get('confidence')}")
        elif result:
            print("   [REAL] External service responded!")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Reward Score: {result.get('reward_score')}")
        else:
            print("   [NULL] Service returned None")

    except Exception as e:
        print(f"   [ERROR] Service call failed: {e}")

    # Show service health status
    print("\n3. SERVICE HEALTH STATUS...")
    from app.external_services import get_service_health_status

    health_status = await get_service_health_status()

    for service, status in health_status.items():
        print(f"   {service}: {status['status']} - Available: {status['available']}")
        print(f"      URL: {status['url']}")


if __name__ == "__main__":
    asyncio.run(test_real_services())
