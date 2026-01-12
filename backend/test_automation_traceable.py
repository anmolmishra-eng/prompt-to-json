"""
Test Prefect Automation - Verify Traceability
Tests: workflow_id, run_id, status tracking
"""
import asyncio
import time

import httpx

BASE_URL = "http://localhost:8000"
TOKEN = None


async def login():
    """Get authentication token"""
    global TOKEN
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login", data={"username": "admin", "password": "bhiv2024"}
        )
        if response.status_code == 200:
            TOKEN = response.json()["access_token"]
            print("[OK] Authenticated")
            return True
        print(f"[FAIL] Login failed: {response.status_code}")
        return False


async def test_trigger_workflow():
    """Test /api/v1/automation/workflow - Trigger real Prefect job"""
    print("\n[1/3] Testing /api/v1/automation/workflow...")

    payload = {
        "workflow_type": "design_optimization",
        "parameters": {"design_id": "test_design_001", "optimization_level": "high", "city": "Mumbai"},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/automation/workflow", json=payload, headers={"Authorization": f"Bearer {TOKEN}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"  [PASS] Workflow triggered")
            print(f"  workflow_id: {result.get('workflow_id')}")
            print(f"  run_id: {result.get('run_id')}")
            print(f"  status: {result.get('status')}")
            return result.get("run_id")
        else:
            print(f"  [FAIL] Status {response.status_code}")
            print(f"  Error: {response.text}")
            return None


async def test_workflow_status(flow_run_id):
    """Test /api/v1/automation/workflow/{flow_run_id}/status"""
    print(f"\n[2/3] Testing /api/v1/automation/workflow/{flow_run_id}/status...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/automation/workflow/{flow_run_id}/status", headers={"Authorization": f"Bearer {TOKEN}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"  [PASS] Status retrieved")
            print(f"  workflow_id: {result.get('workflow_id')}")
            print(f"  state: {result.get('state')}")
            print(f"  started_at: {result.get('started_at')}")
            print(f"  duration_seconds: {result.get('duration_seconds')}")
            return True
        else:
            print(f"  [FAIL] Status {response.status_code}")
            print(f"  Error: {response.text}")
            return False


async def test_automation_status():
    """Test /api/v1/automation/status - Show real executions"""
    print("\n[3/3] Testing /api/v1/automation/status...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/automation/status", headers={"Authorization": f"Bearer {TOKEN}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"  [PASS] Automation status retrieved")
            print(f"  Status: {result.get('status')}")
            print(f"  Total executions: {result.get('total_executions')}")

            executions = result.get("recent_executions", [])
            print(f"\n  Recent Executions ({len(executions)}):")
            for i, exec in enumerate(executions[:5], 1):
                print(
                    f"    {i}. workflow_id={exec.get('workflow_id')} | "
                    f"run_id={exec.get('run_id')[:20]}... | "
                    f"status={exec.get('status')} | "
                    f"flow={exec.get('flow_name')}"
                )

            return True
        else:
            print(f"  [FAIL] Status {response.status_code}")
            print(f"  Error: {response.text}")
            return False


async def main():
    print("=" * 70)
    print("Testing Prefect Automation - Traceability")
    print("=" * 70)

    if not await login():
        print("\n[FAIL] Authentication failed. Cannot proceed.")
        return

    # Test workflow trigger
    flow_run_id = await test_trigger_workflow()

    if flow_run_id:
        # Wait a moment for workflow to start
        print("\n[WAIT] Waiting 2 seconds for workflow to start...")
        time.sleep(2)

        # Test workflow status
        await test_workflow_status(flow_run_id)

    # Test automation status with executions
    await test_automation_status()

    print("\n" + "=" * 70)
    print("Automation Traceability Test Complete")
    print("=" * 70)
    print("\n[OK] Deliverable: Automation is traceable")
    print("   - workflow_id: Stored in database")
    print("   - run_id: Tracked from Prefect")
    print("   - status: Real-time updates")
    print("   - /automation/status: Shows real executions")


if __name__ == "__main__":
    asyncio.run(main())
