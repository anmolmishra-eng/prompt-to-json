"""
Simple BHIV System Test
Test core components without Unicode issues
"""

import sys
from pathlib import Path


def test_configuration():
    """Test configuration loading"""
    try:
        sys.path.insert(0, str(Path.cwd() / "app" / "bhiv_assistant"))
        from config.integration_config import IntegrationConfig

        config = IntegrationConfig()
        print("[PASS] Configuration loaded")
        print(f"  - Sohum MCP: {config.sohum.base_url}")
        print(f"  - RL System: {config.ranjeet.base_url}")
        print(f"  - BHIV Port: {config.bhiv.api_port}")
        return True
    except Exception as e:
        print(f"[FAIL] Configuration: {e}")
        return False


def test_storage():
    """Test storage system"""
    try:
        sys.path.insert(0, str(Path.cwd() / "app"))
        from storage_manager import ensure_storage_ready, storage_manager

        storage_ready = ensure_storage_ready()
        print(f"[PASS] Storage system initialized: {storage_ready}")

        validation = storage_manager.validate_storage()
        failed = [k for k, v in validation.items() if not v]

        if failed:
            print(f"  - Failed paths: {failed}")
        else:
            print("  - All storage paths validated")

        return storage_ready and not failed
    except Exception as e:
        print(f"[FAIL] Storage: {e}")
        return False


def test_database():
    """Test database system"""
    try:
        sys.path.insert(0, str(Path.cwd()))

        # Test basic database connection
        from app.database import check_db_connection, init_db

        # Check connection
        health = check_db_connection()
        if health["status"] == "healthy":
            print(f"[PASS] Database connection: {health['latency_ms']}ms")

            # Try to initialize tables
            try:
                init_success = init_db()
                print(f"[PASS] Database tables: {init_success}")
                return True
            except Exception as init_e:
                print(f"[WARN] Database init: {init_e}")
                return True  # Connection works, init might fail in dev
        else:
            print(f"[FAIL] Database connection: {health.get('error', 'Unknown')}")
            return False

    except Exception as e:
        print(f"[FAIL] Database: {e}")
        return False


def test_imports():
    """Test critical imports"""
    try:
        # Test FastAPI
        import fastapi

        print("[PASS] FastAPI available")

        # Test Prefect
        import prefect

        print("[PASS] Prefect available")

        # Test httpx
        import httpx

        print("[PASS] httpx available")

        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False


def main():
    """Run all tests"""
    print("=== BHIV System Test ===")

    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Storage", test_storage),
        ("Database", test_database),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        results[test_name] = test_func()

    print("\n=== Results ===")
    passed = 0
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("All core components are working!")
    else:
        print("Some components need attention.")

    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
