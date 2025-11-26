#!/usr/bin/env python3
"""
Deploy System Health Monitor to Prefect Cloud
"""
import os
import sys
from pathlib import Path


def deploy_health_monitor():
    """Deploy the system health monitoring flow"""

    # Get the correct path to the workflow file
    current_dir = Path(__file__).parent
    workflow_file = current_dir / "workflows" / "system_health_flow.py"

    if not workflow_file.exists():
        print(f"❌ Workflow file not found: {workflow_file}")
        return False

    print(f"✅ Found workflow file: {workflow_file}")

    # Build the deployment command
    cmd = [
        "uvx",
        "prefect-cloud",
        "deploy",
        f"{workflow_file}:system_health_flow",
        "--name",
        "backend-health-monitor",
        "--from",
        "anmolmishra-eng/prompt-to-json",
    ]

    print(f"🚀 Running deployment command:")
    print(f"   {' '.join(cmd)}")

    # Execute the command
    import subprocess

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Deployment successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Deployment failed!")
        print(f"Error: {e.stderr}")
        print(f"Output: {e.stdout}")
        return False


if __name__ == "__main__":
    success = deploy_health_monitor()
    sys.exit(0 if success else 1)
