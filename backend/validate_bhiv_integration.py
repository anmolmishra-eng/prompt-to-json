"""
Validate BHIV integration without running server
"""

import sys
import os

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def validate_bhiv_integration():
    """Validate BHIV integration"""
    print("Validating BHIV Integration...")
    print("=" * 50)
    
    try:
        # Test 1: Import BHIV module
        print("\n[1/5] Testing BHIV module import...")
        from app.api import bhiv
        print("   ✅ BHIV module imported successfully")
        
        # Test 2: Check BHIV router
        print("\n[2/5] Testing BHIV router...")
        router = bhiv.router
        print(f"   ✅ Router prefix: {router.prefix}")
        print(f"   ✅ Router tags: {router.tags}")
        
        # Test 3: Check BHIV assistant class
        print("\n[3/5] Testing BHIV assistant class...")
        assistant = bhiv.BHIVAssistant()
        print("   ✅ BHIVAssistant class instantiated")
        
        # Test 4: Check request models
        print("\n[4/5] Testing request models...")
        request = bhiv.DesignRequest(
            user_id="test_user",
            prompt="modern apartment",
            city="Mumbai"
        )
        print(f"   ✅ DesignRequest: {request.user_id}, {request.city}")
        
        # Test 5: Check main app integration
        print("\n[5/5] Testing main app integration...")
        from app.main import app
        routes = [route.path for route in app.routes]
        bhiv_routes = [r for r in routes if '/bhiv/' in r]
        print(f"   ✅ BHIV routes found: {len(bhiv_routes)}")
        for route in bhiv_routes:
            print(f"      - {route}")
        
        print("\n" + "=" * 50)
        print("✅ ALL VALIDATIONS PASSED!")
        print("\nBHIV Assistant is successfully integrated!")
        print("\nEndpoints available:")
        print("  - POST /bhiv/v1/design")
        print("  - GET /bhiv/v1/health")
        print("\nTo test live:")
        print("  1. Start server: python -m uvicorn app.main:app --reload")
        print("  2. Test: python test_bhiv_integration.py")
        print("  3. Docs: http://localhost:8000/docs")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = validate_bhiv_integration()
    sys.exit(0 if success else 1)