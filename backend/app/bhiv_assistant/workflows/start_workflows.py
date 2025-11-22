"""
Complete workflow startup script
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


def check_prefect_server():
    """Check if Prefect server is running"""
    try:
        import httpx

        response = httpx.get("http://localhost:4200/api/health", timeout=5.0)
        return response.status_code == 200
    except:
        return False


async def start_workflows():
    """Complete workflow startup process"""

    print("🚀 BHIV Workflow Startup")
    print("=" * 50)

    # Step 1: Check if Prefect server is running
    print("\n[1/4] Checking Prefect server...")
    if check_prefect_server():
        print("✅ Prefect server is running")
    else:
        print("❌ Prefect server not running")
        print("Please start Prefect server first:")
        print("  prefect server start")
        return {"status": "server_not_running"}

    # Step 2: Deploy all workflows
    print("\n[2/4] Deploying workflows...")
    try:
        from workflows.deploy_all_flows import deploy_all_workflows

        deployment_result = await deploy_all_workflows()

        if deployment_result["status"] == "success":
            print("✅ All workflows deployed successfully")
        else:
            print(f"❌ Deployment failed: {deployment_result.get('error')}")
            return deployment_result

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return {"status": "deployment_error", "error": str(e)}

    # Step 3: Test workflows
    print("\n[3/4] Testing workflows...")
    try:
        from workflows.test_all_flows import test_all_workflows

        test_result = await test_all_workflows()

        successful_tests = sum(1 for r in test_result.values() if r.get("status") not in ["error", "failed"])
        total_tests = len(test_result)

        print(f"✅ Workflow tests completed: {successful_tests}/{total_tests} passed")

    except Exception as e:
        print(f"⚠️ Testing error: {e}")
        # Continue even if tests fail

    # Step 4: Monitor status
    print("\n[4/4] Checking final status...")
    try:
        from workflows.monitor_flows import monitor_workflows

        monitor_result = await monitor_workflows()

        if monitor_result["status"] == "monitoring_complete":
            print("✅ Monitoring completed")

    except Exception as e:
        print(f"⚠️ Monitoring error: {e}")

    # Final summary
    print("\n" + "=" * 50)
    print("🎉 WORKFLOW STARTUP COMPLETE")
    print("=" * 50)
    print("\nNext steps:")
    print("1. View workflows: http://localhost:4200")
    print("2. Start worker: prefect worker start --pool default-pool")
    print("3. Monitor logs: Check Prefect UI for execution logs")

    return {"status": "startup_complete"}


if __name__ == "__main__":
    result = asyncio.run(start_workflows())
    print(f"\nStartup result: {result['status']}")
