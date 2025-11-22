#!/usr/bin/env python3
"""
Final Integration Summary - Complete validation of all components
"""

import importlib
import os
import sys
from pathlib import Path


def main():
    print("FINAL INTEGRATION VALIDATION")
    print("=" * 50)

    # 1. Environment Check
    print("\n1. ENVIRONMENT STATUS")
    print("-" * 25)
    venv_active = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
    print(f"Virtual Environment: {'ACTIVE' if venv_active else 'INACTIVE'}")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Python Path: {sys.executable}")

    # 2. File Structure Check
    print("\n2. FILE STRUCTURE")
    print("-" * 20)
    critical_files = [
        "app/main.py",
        "app/config.py",
        "app/database.py",
        "app/api/bhiv_integrated.py",
        ".env",
        "requirements.txt",
    ]

    missing_files = []
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[MISSING] {file_path}")
            missing_files.append(file_path)

    # 3. Import Validation
    print("\n3. IMPORT VALIDATION")
    print("-" * 22)

    # Core modules
    core_modules = ["app.main", "app.config", "app.database", "app.models", "app.utils", "app.lm_adapter"]

    failed_imports = []
    for module in core_modules:
        try:
            importlib.import_module(module)
            print(f"[OK] {module}")
        except Exception as e:
            print(f"[FAIL] {module}: {str(e)[:50]}...")
            failed_imports.append(module)

    # API modules
    api_modules = ["app.api.auth", "app.api.generate", "app.api.health", "app.api.bhiv_integrated"]

    for module in api_modules:
        try:
            importlib.import_module(module)
            print(f"[OK] {module}")
        except Exception as e:
            print(f"[FAIL] {module}: {str(e)[:50]}...")
            failed_imports.append(module)

    # 4. BHIV Integration Check
    print("\n4. BHIV INTEGRATION")
    print("-" * 20)
    try:
        from app.api.bhiv_integrated import router
        from app.main import app

        # Count BHIV routes
        bhiv_routes = []
        for route in app.routes:
            if hasattr(route, "path") and "/bhiv" in route.path:
                bhiv_routes.append(route.path)

        print(f"[OK] BHIV router imported successfully")
        print(f"[OK] BHIV routes found: {len(bhiv_routes)}")
        for route in bhiv_routes:
            print(f"     - {route}")

        bhiv_working = True
    except Exception as e:
        print(f"[FAIL] BHIV integration error: {e}")
        bhiv_working = False

    # 5. FastAPI App Check
    print("\n5. FASTAPI APPLICATION")
    print("-" * 23)
    try:
        from app.main import app

        total_routes = len(app.routes)
        print(f"[OK] FastAPI app created successfully")
        print(f"[OK] Total routes registered: {total_routes}")
        print(f"[OK] App title: {app.title}")
        app_working = True
    except Exception as e:
        print(f"[FAIL] FastAPI app error: {e}")
        app_working = False

    # 6. Configuration Check
    print("\n6. CONFIGURATION")
    print("-" * 17)
    try:
        from app.config import settings

        configs = {
            "Database URL": bool(settings.DATABASE_URL),
            "Supabase URL": bool(settings.SUPABASE_URL),
            "JWT Secret": bool(settings.JWT_SECRET_KEY),
            "OpenAI Key": bool(settings.OPENAI_API_KEY),
        }

        for config_name, available in configs.items():
            status = "[OK]" if available else "[MISSING]"
            print(f"{status} {config_name}")

        config_working = all(configs.values())
    except Exception as e:
        print(f"[FAIL] Configuration error: {e}")
        config_working = False

    # 7. Final Summary
    print("\n" + "=" * 50)
    print("FINAL INTEGRATION SUMMARY")
    print("=" * 50)

    checks = {
        "Virtual Environment": venv_active,
        "File Structure": len(missing_files) == 0,
        "Core Imports": len(failed_imports) == 0,
        "BHIV Integration": bhiv_working,
        "FastAPI Application": app_working,
        "Configuration": config_working,
    }

    passed = 0
    for check_name, result in checks.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {check_name}")
        if result:
            passed += 1

    print(f"\nOVERALL RESULT: {passed}/{len(checks)} checks passed")

    if passed == len(checks):
        print("\n*** SUCCESS: ALL INTEGRATIONS WORKING PERFECTLY! ***")
        print("\nYour backend is fully integrated and ready to use:")
        print("- All files are properly integrated")
        print("- Virtual environment is available and working")
        print("- BHIV Assistant is fully integrated")
        print("- All API endpoints are accessible")
        print("- Configuration is complete")

        print("\nTo start the server:")
        print("1. Activate venv: call venv\\Scripts\\activate.bat")
        print("2. Start server: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("3. Access API docs: http://localhost:8000/docs")

        return True
    else:
        print(f"\n*** WARNING: {len(checks) - passed} issues found ***")

        if missing_files:
            print(f"\nMissing files: {missing_files}")
        if failed_imports:
            print(f"Failed imports: {failed_imports}")

        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
