#!/usr/bin/env python3
"""
Simple test for Mock Land Utilization RL System
"""
import asyncio
import sys

sys.path.append(".")


async def test_mock_system():
    print("Testing Mock Land Utilization RL System")
    print("=" * 50)

    try:
        from app.config import settings
        from app.external_services import ranjeet_client

        print(f"RL URL: {settings.RANJEET_RL_URL}")
        print(f"Mock Mode: {getattr(settings, 'LAND_UTILIZATION_MOCK_MODE', 'Not set')}")

        # Test optimization
        test_spec = {"objects": [{"id": "test", "type": "building"}]}
        result = await ranjeet_client.optimize_design(test_spec, "Mumbai")

        print(f"Mock Response: {result.get('mock_response', False)}")
        print(f"Status: {result.get('status', 'unknown')}")

        if result.get("mock_response"):
            print("SUCCESS: Mock system is working!")
            return True
        else:
            print("WARNING: Not using mock system")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_mock_system())
    if result:
        print("\nMock Land Utilization RL System is ready!")
        print("Ranjeet's live service will be available in 3-4 days.")
    else:
        print("\nTest failed - check configuration.")
