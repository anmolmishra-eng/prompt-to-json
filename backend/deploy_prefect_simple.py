#!/usr/bin/env python3
"""
Simple Prefect Deployment Script
Minimal setup for Prefect workflows
"""
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description):
    """Run command with error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"⚠️ {description} warning: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False


def main():
    """Simple deployment process"""
    print("🚀 Simple Prefect Deployment")
    print("=" * 40)

    # Change to backend directory
    backend_dir = Path(__file__).parent
    print(f"Working directory: {backend_dir}")

    # Step 1: Create work pool
    run_command(f"{sys.executable} -m prefect work-pool create default --type process", "Creating work pool")

    # Step 2: Deploy health monitoring
    run_command(
        f"{sys.executable} -m prefect deploy workflows/system_health_flow.py:system_health_flow --name health-monitor --pool default",
        "Deploying health monitor",
    )

    # Step 3: Deploy PDF processor
    run_command(
        f"{sys.executable} -m prefect deploy workflows/pdf_to_mcp_flow.py:pdf_to_mcp_flow --name pdf-processor --pool default",
        "Deploying PDF processor",
    )

    print("\n✅ Deployment complete!")
    print("\nTo start worker:")
    print(f"  {sys.executable} -m prefect worker start --pool default")
    print("\nTo use local alternative:")
    print("  python deploy_health_local.py --continuous")


if __name__ == "__main__":
    main()
