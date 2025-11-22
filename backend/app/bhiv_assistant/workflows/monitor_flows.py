"""
Monitor Prefect workflow status
"""

import asyncio
from datetime import datetime

import httpx


async def check_prefect_server():
    """Check if Prefect server is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:4200/api/health", timeout=5.0)
            return response.status_code == 200
    except:
        return False


async def get_deployment_status():
    """Get status of all deployments"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:4200/api/deployments", timeout=10.0)
            if response.status_code == 200:
                return response.json()
            return []
    except Exception as e:
        print(f"Failed to get deployment status: {e}")
        return []


async def get_flow_runs():
    """Get recent flow runs"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:4200/api/flow_runs", timeout=10.0)
            if response.status_code == 200:
                return response.json()
            return []
    except Exception as e:
        print(f"Failed to get flow runs: {e}")
        return []


async def monitor_workflows():
    """Monitor all BHIV workflows"""

    print("BHIV Workflow Monitor")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Check Prefect server
    server_running = await check_prefect_server()
    print(f"Prefect Server: {'✅ Running' if server_running else '❌ Not running'}")

    if not server_running:
        print("\n❌ Prefect server is not running!")
        print("Start with: prefect server start")
        return {"status": "server_down"}

    # Get deployments
    print("\n📋 DEPLOYMENTS")
    print("-" * 30)
    deployments = await get_deployment_status()

    if deployments:
        for deployment in deployments:
            name = deployment.get("name", "Unknown")
            status = deployment.get("status", "Unknown")
            print(f"  {name}: {status}")
    else:
        print("  No deployments found")

    # Get recent flow runs
    print("\n🏃 RECENT FLOW RUNS")
    print("-" * 30)
    flow_runs = await get_flow_runs()

    if flow_runs:
        for run in flow_runs[:10]:  # Show last 10 runs
            name = run.get("name", "Unknown")
            state = run.get("state", {}).get("name", "Unknown")
            start_time = run.get("start_time", "Unknown")
            print(f"  {name}: {state} ({start_time})")
    else:
        print("  No recent flow runs found")

    # Summary
    print("\n📊 SUMMARY")
    print("-" * 30)
    print(f"Total deployments: {len(deployments)}")
    print(f"Recent flow runs: {len(flow_runs)}")

    return {
        "status": "monitoring_complete",
        "server_running": server_running,
        "deployments": len(deployments),
        "flow_runs": len(flow_runs),
    }


if __name__ == "__main__":
    result = asyncio.run(monitor_workflows())
    print(f"\nMonitoring result: {result['status']}")
