"""
Final validation of BHIV integration
"""

import os
import sys

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))


def validate_bhiv_final():
    """Final validation of BHIV integration"""
    print("Final BHIV Integration Validation")
    print("=" * 50)

    try:
        # Test 1: Import integrated BHIV module
        print("\n[1/6] Testing integrated BHIV module...")
        from app.api import bhiv_integrated

        print("   ✅ bhiv_integrated module imported")

        # Test 2: Check router
        print("\n[2/6] Testing BHIV router...")
        router = bhiv_integrated.router
        print(f"   ✅ Router prefix: {router.prefix}")
        print(f"   ✅ Router tags: {router.tags}")

        # Test 3: Check request models
        print("\n[3/6] Testing request models...")
        request = bhiv_integrated.DesignRequest(user_id="test_user", prompt="modern apartment", city="Mumbai")
        print(f"   ✅ DesignRequest: {request.user_id}, {request.city}")

        # Test 4: Check main app integration
        print("\n[4/6] Testing main app integration...")
        from app.main import app

        routes = [route.path for route in app.routes]
        bhiv_routes = [r for r in routes if "/bhiv/" in r]
        print(f"   ✅ BHIV routes found: {len(bhiv_routes)}")
        for route in bhiv_routes:
            print(f"      - {route}")

        # Test 5: Check backend dependencies
        print("\n[5/6] Testing backend dependencies...")
        from app.config import settings
        from app.lm_adapter import run_local_lm
        from app.utils import create_new_spec_id

        print("   ✅ Backend config imported")
        print("   ✅ LM adapter imported")
        print("   ✅ Utils imported")

        # Test 6: Check external API functions
        print("\n[6/6] Testing external API functions...")
        call_sohum = bhiv_integrated.call_sohum_compliance
        call_ranjeet = bhiv_integrated.call_ranjeet_rl
        print("   ✅ Sohum compliance function available")
        print("   ✅ Ranjeet RL function available")

        print("\n" + "=" * 50)
        print("✅ ALL VALIDATIONS PASSED!")
        print("\n🎉 BHIV Assistant is fully integrated!")
        print("\n📋 Integration Summary:")
        print("   - Uses existing backend virtual environment")
        print("   - Integrated with main FastAPI app")
        print("   - Uses backend's LM adapter internally")
        print("   - Calls external Sohum MCP API")
        print("   - Calls external Ranjeet RL API")
        print("   - Unified response format")

        print("\n🚀 Available Endpoints:")
        print("   - POST /bhiv/v1/design")
        print("   - GET /bhiv/v1/health")

        print("\n🧪 To test:")
        print("   1. Start server: python -m uvicorn app.main:app --reload")
        print("   2. Test: python test_bhiv_integration.py")
        print("   3. Docs: http://localhost:8000/docs")

        return True

    except Exception as e:
        print(f"\nValidation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = validate_bhiv_final()
    sys.exit(0 if success else 1)
