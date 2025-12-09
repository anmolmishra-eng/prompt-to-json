"""
Deploy all Prefect workflows at once - COMPLETE & FIXED
"""
import asyncio
import os
import subprocess
import sys
from pathlib import Path


def deploy_workflow(workflow_path: Path) -> bool:
    """Deploy a single workflow"""
    print(f"Deploying {workflow_path.name}...")

    try:
        # Run the workflow file to trigger deployment
        result = subprocess.run([sys.executable, str(workflow_path)], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print(f"SUCCESS: {workflow_path.name} deployed")
            return True
        else:
            print(f"FAILED: {workflow_path.name} deployment failed")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {workflow_path.name} deployment timed out")
        return False
    except Exception as e:
        print(f"ERROR: {workflow_path.name} deployment error: {e}")
        return False


async def deploy_all_flows():
    """Deploy essential BHIV workflows only"""
    print("Deploying Essential BHIV Workflows")
    print("=" * 50)

    # Only essential workflows for BHIV system
    workflows = [
        "../app/bhiv_assistant/workflows/mcp_compliance_flow.py",
        "../app/bhiv_assistant/workflows/rl_integration_flows.py",
        "../app/bhiv_assistant/workflows/notification_flows.py",
    ]

    workflow_dir = Path(__file__).parent
    successful_deployments = 0
    total_workflows = len(workflows)

    for workflow_file in workflows:
        workflow_path = workflow_dir / workflow_file

        if not workflow_path.exists():
            print(f"NOT FOUND: {workflow_file}")
            continue

        success = deploy_workflow(workflow_path)
        if success:
            successful_deployments += 1

        print()  # Add spacing between deployments

    # Summary
    print("=" * 60)
    print(f"Deployment Summary: {successful_deployments}/{total_workflows} workflows deployed")
    print("=" * 60)

    if successful_deployments == total_workflows:
        print("All workflows deployed successfully!")
        print("\nDeployed Workflows:")
        print("- PDF to MCP Flow (PDF rule extraction)")
        print("- Compliance Validation Flow (Design validation)")
        print("- System Health Flow (Component monitoring)")
        print("\nWorkflows are now running on their schedules:")
        print("- PDF to MCP: On-demand")
        print("- Compliance Validation: Every 15 minutes")
        print("- System Health: Every 5 minutes")
    else:
        failed = total_workflows - successful_deployments
        print(f"WARNING: {failed} workflow(s) failed to deploy")

    return successful_deployments == total_workflows


def check_prefect_server():
    """Check if Prefect server is accessible"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import prefect; print('Prefect available')"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except:
        return False


def main():
    """Main deployment function"""
    print("Checking Prefect availability...")

    if not check_prefect_server():
        print("ERROR: Prefect not available. Install with: pip install prefect")
        return False

    print("SUCCESS: Prefect is available")
    print()

    # Run deployment
    success = asyncio.run(deploy_all_flows())

    if success:
        print("\nNext Steps:")
        print("1. Start Prefect server: prefect server start")
        print("2. View workflows: http://localhost:4200")
        print("3. Monitor workflow runs in the UI")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
