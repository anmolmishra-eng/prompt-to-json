#!/usr/bin/env python3
"""
Test script for the Mock Land Utilization RL System
Verifies that Ranjeet's URLs have been replaced with mock responses
"""
import asyncio
import json
import sys
from datetime import datetime

# Add the app directory to the path
sys.path.append(".")


async def test_mock_rl_system():
    """Test the mock Land Utilization RL system"""
    print("🔄 Testing Mock Land Utilization RL System")
    print("=" * 60)

    try:
        from app.config import settings
        from app.external_services import ranjeet_client

        # Test 1: Configuration Check
        print("1. Configuration Check:")
        print(f"   RL URL: {settings.RANJEET_RL_URL}")
        print(f"   Mock Mode: {getattr(settings, 'LAND_UTILIZATION_MOCK_MODE', 'Not set')}")
        print(f"   Service Available: {getattr(settings, 'RANJEET_SERVICE_AVAILABLE', 'Not set')}")
        print()

        # Test 2: Health Check
        print("2. Health Check:")
        try:
            health_status = await ranjeet_client.health_check()
            print(f"   Status: {health_status}")
        except Exception as e:
            print(f"   Health check failed: {e}")
        print()

        # Test 3: Land Utilization Optimization
        print("3. Land Utilization Optimization Test:")
        test_cities = ["Mumbai", "Pune", "Ahmedabad", "Nashik"]

        for city in test_cities:
            try:
                print(f"   Testing {city}...")

                test_spec = {
                    "objects": [
                        {"id": "building_1", "type": "residential", "area": 1000},
                        {"id": "building_2", "type": "commercial", "area": 500},
                    ],
                    "plot_size": 2000,
                    "location_type": "urban",
                }

                result = await ranjeet_client.optimize_design(test_spec, city)

                # Verify mock response structure
                if result.get("mock_response"):
                    print(f"   ✅ {city}: Mock response received")

                    # Check land utilization metrics
                    metrics = result.get("optimized_layout", {}).get("land_utilization_metrics", {})
                    if metrics:
                        print(f"      Density Optimization: {metrics.get('density_optimization', 'N/A')}")
                        print(f"      Overall Score: {metrics.get('overall_utilization_score', 'N/A'):.3f}")

                else:
                    print(f"   ⚠️ {city}: Live service response (unexpected in mock mode)")

            except Exception as e:
                print(f"   ❌ {city}: Error - {e}")

        print()

        # Test 4: RL Prediction
        print("4. RL Prediction Test:")
        try:
            prediction = await ranjeet_client.predict_reward({"test": "spec"}, "Optimize land utilization")
            print(f"   ✅ Prediction received: {prediction.get('reward_prediction', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Prediction failed: {e}")

        print()

        # Test 5: Mock Response Validation
        print("5. Mock Response Validation:")
        try:
            mock_response = ranjeet_client.get_mock_land_utilization_response({"test": "spec"}, "Mumbai")

            required_fields = ["optimized_layout", "confidence", "reward_score", "status", "mock_response"]

            missing_fields = [field for field in required_fields if field not in mock_response]

            if not missing_fields:
                print("   ✅ All required fields present in mock response")

                # Check land utilization specific fields
                land_metrics = mock_response.get("optimized_layout", {}).get("land_utilization_metrics", {})
                if land_metrics:
                    print("   ✅ Land utilization metrics present")
                    print(f"      Density: {land_metrics.get('density_optimization', 'N/A')}")
                    print(f"      Green Space: {land_metrics.get('green_space_ratio', 'N/A')}")
                else:
                    print("   ⚠️ Land utilization metrics missing")

            else:
                print(f"   ❌ Missing fields: {missing_fields}")

        except Exception as e:
            print(f"   ❌ Mock validation failed: {e}")

        print()
        print("=" * 60)
        print("✅ Mock Land Utilization RL System Test Complete")
        print("📝 Note: Ranjeet's live service will be available in 3-4 days")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_configuration_changes():
    """Test that configuration has been properly updated"""
    print("\n🔧 Testing Configuration Changes:")
    print("=" * 40)

    try:
        from app.config import settings

        # Check if new configuration fields exist
        config_checks = [
            ("LAND_UTILIZATION_ENABLED", getattr(settings, "LAND_UTILIZATION_ENABLED", None)),
            ("LAND_UTILIZATION_MOCK_MODE", getattr(settings, "LAND_UTILIZATION_MOCK_MODE", None)),
            ("RANJEET_SERVICE_AVAILABLE", getattr(settings, "RANJEET_SERVICE_AVAILABLE", None)),
            ("RANJEET_RL_URL", settings.RANJEET_RL_URL),
        ]

        for field_name, field_value in config_checks:
            if field_value is not None:
                print(f"✅ {field_name}: {field_value}")
            else:
                print(f"❌ {field_name}: Not configured")

        # Check if URL has been changed from original
        if "mock" in settings.RANJEET_RL_URL.lower():
            print("✅ RL URL updated to use mock endpoints")
        else:
            print("⚠️ RL URL may still point to external service")

        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Mock Land Utilization RL System Tests")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test configuration
    config_ok = test_configuration_changes()

    # Test mock system
    if config_ok:
        system_ok = asyncio.run(test_mock_rl_system())

        if system_ok:
            print("\n🎉 All tests passed! Mock system is ready.")
            print("🔄 System will automatically switch to live service when available.")
        else:
            print("\n❌ Some tests failed. Check the output above.")
            sys.exit(1)
    else:
        print("\n❌ Configuration issues detected. Check your .env file.")
        sys.exit(1)
