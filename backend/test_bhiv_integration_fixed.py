"""
Test BHIV Integration After Fixes
Verify all components are working correctly
"""

import asyncio
import json
from datetime import datetime

import httpx


async def test_bhiv_assistant():
    """Test BHIV Assistant main endpoint"""
    print("Testing BHIV Assistant...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {
                "user_id": "test_user_001",
                "prompt": "Design a modern 2BHK apartment in Mumbai",
                "city": "Mumbai",
                "project_id": "test_project_001",
                "budget": 5000000,
                "area_sqft": 800,
            }

            response = await client.post("http://localhost:8000/bhiv/v1/prompt", json=payload)

            if response.status_code == 201:
                result = response.json()
                print(f"✅ BHIV Assistant: {result['status']} - {len(result['agents'])} agents")
                return True
            else:
                print(f"❌ BHIV Assistant failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ BHIV Assistant error: {e}")
            return False


async def test_mcp_integration():
    """Test MCP integration with Sohum's service"""
    print("Testing MCP Integration...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test direct Sohum service
            response = await client.get("https://ai-rule-api-w7z5.onrender.com/health")

            if response.status_code == 200:
                print("Sohum's MCP service is reachable")

                # Test local MCP endpoint
                response = await client.get("http://localhost:8003/mcp/metadata/Mumbai")
                if response.status_code == 200:
                    print("Local MCP integration working")
                    return True
                else:
                    print(f"Local MCP endpoint issue: {response.status_code}")
                    return False
            else:
                print(f"❌ Sohum's service unreachable: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ MCP integration error: {e}")
            return False


async def test_rl_integration():
    """Test RL integration with local system"""
    print("Testing RL Integration...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test local RL feedback endpoint
            payload = {
                "user_id": "test_user_001",
                "spec_id": "test_spec_001",
                "rating": 4.5,
                "feedback_text": "Great design!",
                "design_accepted": True,
            }

            response = await client.post("http://localhost:8000/api/v1/rl/feedback", json=payload)

            if response.status_code in [200, 201]:
                print("Local RL integration working")
                return True
            else:
                print(f"RL endpoint issue: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ RL integration error: {e}")
            return False


async def test_geometry_verification():
    """Test geometry verification workflow"""
    print("Testing Geometry Verification...")

    try:
        # Import and test geometry flow
        import sys
        from pathlib import Path

        sys.path.append(str(Path(__file__).parent / "app" / "bhiv_assistant"))

        from workflows.compliance.geometry_verification_flow import GeometryConfig, geometry_verification_flow

        # Create test config
        config = GeometryConfig(
            glb_source_dir=Path("data/geometry_outputs"),
            output_dir=Path("reports/geometry_verification"),
            max_file_size_mb=50.0,
        )

        # Run verification
        result = await geometry_verification_flow(config)

        if result["status"] in ["complete", "no_files"]:
            print(f"Geometry verification: {result['status']}")
            return True
        else:
            print(f"❌ Geometry verification failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Geometry verification error: {e}")
        return False


async def test_config_integration():
    """Test configuration integration"""
    print("Testing Configuration...")

    try:
        import sys
        from pathlib import Path

        sys.path.append(str(Path(__file__).parent / "app" / "bhiv_assistant"))

        from config.integration_config import IntegrationConfig

        config = IntegrationConfig()

        print(f"Config loaded:")
        print(f"   - Sohum MCP: {config.sohum.base_url}")
        print(f"   - RL System: {config.ranjeet.base_url}")
        print(f"   - BHIV Port: {config.bhiv.api_port}")

        return True

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


async def test_storage_system():
    """Test storage system"""
    print("Testing Storage System...")

    try:
        from app.storage_manager import ensure_storage_ready, storage_manager

        # Ensure storage is ready
        storage_ready = ensure_storage_ready()

        if storage_ready:
            print("Storage system initialized")

            # Validate storage paths
            validation_results = storage_manager.validate_storage()
            failed_paths = [name for name, success in validation_results.items() if not success]

            if not failed_paths:
                print("All storage paths validated")
                return True
            else:
                print(f"Some storage paths failed: {failed_paths}")
                return False
        else:
            print("❌ Storage system initialization failed")
            return False

    except Exception as e:
        print(f"❌ Storage system error: {e}")
        return False


async def test_database_system():
    """Test database system"""
    print("Testing Database System...")

    try:
        from app.database_validator import validate_database

        db_healthy = validate_database()

        if db_healthy:
            print("Database system validated")
            return True
        else:
            print("❌ Database validation failed")
            return False

    except Exception as e:
        print(f"❌ Database system error: {e}")
        return False


async def test_automation_status():
    """Test automation status"""
    print("Testing Automation Status...")

    try:
        import subprocess

        # Check if Prefect is available
        result = subprocess.run(["python", "-m", "prefect", "--help"], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("Prefect is available")

            # Check if server is running
            async with httpx.AsyncClient(timeout=5.0) as client:
                try:
                    response = await client.get("http://localhost:4200/api/health")
                    if response.status_code == 200:
                        print("Prefect server is running")
                        return True
                    else:
                        print("Prefect server not running (start with: prefect server start)")
                        return False
                except:
                    print("Prefect server not running (start with: prefect server start)")
                    return False
        else:
            print("❌ Prefect not available")
            return False

    except Exception as e:
        print(f"❌ Automation test error: {e}")
        return False


async def main():
    """Run all integration tests"""
    print("BHIV Integration Test Suite")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print("=" * 50)

    tests = [
        ("Configuration", test_config_integration),
        ("Storage System", test_storage_system),
        ("Database System", test_database_system),
        ("MCP Integration", test_mcp_integration),
        ("RL Integration", test_rl_integration),
        ("Geometry Verification", test_geometry_verification),
        ("Automation Status", test_automation_status),
        ("BHIV Assistant", test_bhiv_assistant),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"{test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<30} {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed! BHIV integration is working!")
    else:
        print("Some tests failed. Check the issues above.")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        exit(1)
