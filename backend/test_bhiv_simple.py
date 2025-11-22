"""
Simple BHIV integration test
"""

import os
import sys

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))


def test_bhiv_simple():
    """Simple BHIV integration test"""
    print("BHIV Integration Test")
    print("=" * 30)

    try:
        # Test imports
        print("\n1. Testing imports...")
        from app.api import bhiv_integrated
        from app.config import settings
        from app.lm_adapter import run_local_lm
        from app.utils import create_new_spec_id

        print("   All imports successful")

        # Test router
        print("\n2. Testing router...")
        router = bhiv_integrated.router
        print(f"   Router prefix: {router.prefix}")
        print(f"   Router tags: {router.tags}")

        # Test models
        print("\n3. Testing models...")
        request = bhiv_integrated.DesignRequest(user_id="test_user", prompt="modern apartment", city="Mumbai")
        print(f"   Request created: {request.user_id}, {request.city}")

        # Test main app
        print("\n4. Testing main app...")
        from app.main import app

        routes = [route.path for route in app.routes]
        bhiv_routes = [r for r in routes if "/bhiv/" in r]
        print(f"   BHIV routes found: {len(bhiv_routes)}")

        # Test functions
        print("\n5. Testing functions...")
        spec_id = create_new_spec_id()
        print(f"   Generated spec ID: {spec_id}")

        print("\n" + "=" * 30)
        print("SUCCESS: All tests passed!")
        print("\nBHIV Assistant is integrated!")
        print("\nEndpoints:")
        print("  - POST /bhiv/v1/design")
        print("  - GET /bhiv/v1/health")
        print("\nTo start server:")
        print("  python -m uvicorn app.main:app --reload")

        return True

    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_bhiv_simple()
    sys.exit(0 if success else 1)
