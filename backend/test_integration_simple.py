#!/usr/bin/env python3
"""
Simple Integration Test - Tests all files work together with venv
"""

import importlib
import os
import sys


def main():
    print("Starting Integration Test")
    print("=" * 40)

    # Test 1: Virtual Environment
    print("\n1. Testing Virtual Environment...")
    venv_active = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
    print(f"   Virtual environment active: {venv_active}")
    print(f"   Python executable: {sys.executable}")

    # Test 2: Core Imports
    print("\n2. Testing Core Backend Imports...")
    core_modules = ["app.main", "app.config", "app.database", "app.models", "app.utils", "app.lm_adapter"]

    core_success = 0
    for module in core_modules:
        try:
            importlib.import_module(module)
            print(f"   [OK] {module}")
            core_success += 1
        except Exception as e:
            print(f"   [FAIL] {module}: {e}")

    # Test 3: API Imports
    print("\n3. Testing API Imports...")
    api_modules = ["app.api.auth", "app.api.generate", "app.api.health", "app.api.bhiv_integrated"]

    api_success = 0
    for module in api_modules:
        try:
            importlib.import_module(module)
            print(f"   [OK] {module}")
            api_success += 1
        except Exception as e:
            print(f"   [FAIL] {module}: {e}")

    # Test 4: BHIV Integration
    print("\n4. Testing BHIV Integration...")
    try:
        from app.api.bhiv_integrated import router
        from app.main import app

        bhiv_routes = [route for route in app.routes if hasattr(route, "path") and "/bhiv" in route.path]
        print(f"   [OK] BHIV router imported")
        print(f"   [OK] BHIV routes found: {len(bhiv_routes)}")
        bhiv_success = True
    except Exception as e:
        print(f"   [FAIL] BHIV integration: {e}")
        bhiv_success = False

    # Test 5: FastAPI App
    print("\n5. Testing FastAPI App...")
    try:
        from app.main import app

        total_routes = len(app.routes)
        print(f"   [OK] FastAPI app created")
        print(f"   [OK] Total routes: {total_routes}")
        app_success = True
    except Exception as e:
        print(f"   [FAIL] FastAPI app: {e}")
        app_success = False

    # Summary
    print("\n" + "=" * 40)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 40)

    results = {
        "Virtual Environment": venv_active,
        "Core Imports": core_success == len(core_modules),
        "API Imports": api_success == len(api_modules),
        "BHIV Integration": bhiv_success,
        "FastAPI App": app_success,
    }

    passed = 0
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\nResult: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("SUCCESS: All integrations working!")
        return True
    else:
        print("WARNING: Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
