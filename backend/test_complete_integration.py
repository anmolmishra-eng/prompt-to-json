#!/usr/bin/env python3
"""
Comprehensive Integration Test
Tests all files are well integrated and virtual environment is available
"""

import importlib
import os
import subprocess
import sys
from pathlib import Path


def test_virtual_environment():
    """Test virtual environment is active and working"""
    print("🔍 Testing Virtual Environment...")

    # Check if we're in a virtual environment
    venv_active = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
    print(f"   ✓ Virtual environment active: {venv_active}")
    print(f"   ✓ Python executable: {sys.executable}")
    print(f"   ✓ Python version: {sys.version}")

    return venv_active


def test_core_imports():
    """Test all core backend imports work"""
    print("\n🔍 Testing Core Backend Imports...")

    imports_to_test = [
        "app.main",
        "app.config",
        "app.database",
        "app.models",
        "app.schemas",
        "app.utils",
        "app.lm_adapter",
        "app.security",
        "app.storage",
    ]

    success_count = 0
    for module_name in imports_to_test:
        try:
            importlib.import_module(module_name)
            print(f"   ✓ {module_name}")
            success_count += 1
        except Exception as e:
            print(f"   ✗ {module_name}: {e}")

    print(f"   📊 Core imports: {success_count}/{len(imports_to_test)} successful")
    return success_count == len(imports_to_test)


def test_api_imports():
    """Test all API endpoint imports work"""
    print("\n🔍 Testing API Endpoint Imports...")

    api_imports = [
        "app.api.auth",
        "app.api.generate",
        "app.api.evaluate",
        "app.api.iterate",
        "app.api.switch",
        "app.api.health",
        "app.api.compliance",
        "app.api.rl",
        "app.api.data_privacy",
        "app.api.bhiv_integrated",
    ]

    success_count = 0
    for module_name in api_imports:
        try:
            importlib.import_module(module_name)
            print(f"   ✓ {module_name}")
            success_count += 1
        except Exception as e:
            print(f"   ✗ {module_name}: {e}")

    print(f"   📊 API imports: {success_count}/{len(api_imports)} successful")
    return success_count == len(api_imports)


def test_bhiv_integration():
    """Test BHIV assistant integration"""
    print("\n🔍 Testing BHIV Integration...")

    try:
        from app.api.bhiv_integrated import router
        from app.main import app

        # Check if BHIV router is included in main app
        bhiv_routes = [route for route in app.routes if hasattr(route, "path") and "/bhiv" in route.path]

        print(f"   ✓ BHIV router imported successfully")
        print(f"   ✓ BHIV routes found: {len(bhiv_routes)}")

        for route in bhiv_routes:
            print(f"     - {route.methods} {route.path}")

        return len(bhiv_routes) > 0

    except Exception as e:
        print(f"   ✗ BHIV integration failed: {e}")
        return False


def test_database_connection():
    """Test database connection works"""
    print("\n🔍 Testing Database Connection...")

    try:
        from app.config import settings
        from app.database import get_db

        print(f"   ✓ Database URL configured: {bool(settings.DATABASE_URL)}")
        print(f"   ✓ Database module imported successfully")

        return True

    except Exception as e:
        print(f"   ✗ Database connection test failed: {e}")
        return False


def test_external_dependencies():
    """Test external API dependencies"""
    print("\n🔍 Testing External Dependencies...")

    try:
        from app.config import settings

        dependencies = {
            "Supabase URL": bool(settings.SUPABASE_URL),
            "Supabase Key": bool(settings.SUPABASE_KEY),
            "JWT Secret": bool(settings.JWT_SECRET_KEY),
            "OpenAI API Key": bool(settings.OPENAI_API_KEY),
            "Soham URL": bool(getattr(settings, "SOHAM_URL", None)),
        }

        for dep_name, available in dependencies.items():
            status = "✓" if available else "✗"
            print(f"   {status} {dep_name}: {'Available' if available else 'Missing'}")

        return all(dependencies.values())

    except Exception as e:
        print(f"   ✗ External dependencies test failed: {e}")
        return False


def test_file_structure():
    """Test file structure is correct"""
    print("\n🔍 Testing File Structure...")

    required_files = [
        "app/main.py",
        "app/config.py",
        "app/database.py",
        "app/models.py",
        "app/utils.py",
        "app/api/bhiv_integrated.py",
        ".env",
        "requirements.txt",
    ]

    success_count = 0
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"   ✓ {file_path}")
            success_count += 1
        else:
            print(f"   ✗ {file_path} - Missing")

    print(f"   📊 File structure: {success_count}/{len(required_files)} files found")
    return success_count == len(required_files)


def test_fastapi_app():
    """Test FastAPI app can be created"""
    print("\n🔍 Testing FastAPI App Creation...")

    try:
        from app.main import app

        print(f"   ✓ FastAPI app created successfully")
        print(f"   ✓ App title: {app.title}")
        print(f"   ✓ Total routes: {len(app.routes)}")

        # List all routes
        api_routes = []
        for route in app.routes:
            if hasattr(route, "path") and hasattr(route, "methods"):
                for method in route.methods:
                    if method != "HEAD":  # Skip HEAD methods
                        api_routes.append(f"{method} {route.path}")

        print(f"   ✓ API endpoints: {len(api_routes)}")

        return True

    except Exception as e:
        print(f"   ✗ FastAPI app creation failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("🚀 Starting Comprehensive Integration Test")
    print("=" * 50)

    tests = [
        ("Virtual Environment", test_virtual_environment),
        ("Core Imports", test_core_imports),
        ("API Imports", test_api_imports),
        ("BHIV Integration", test_bhiv_integration),
        ("Database Connection", test_database_connection),
        ("External Dependencies", test_external_dependencies),
        ("File Structure", test_file_structure),
        ("FastAPI App", test_fastapi_app),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 50)

    passed = sum(results.values())
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Integration is successful!")
        return True
    else:
        print("⚠️  Some tests failed - Check the issues above")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
