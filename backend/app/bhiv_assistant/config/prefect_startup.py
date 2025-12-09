"""
BHIV Prefect Server Startup Script
Starts minimal Prefect server with only essential endpoints
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def setup_prefect_environment():
    """Setup Prefect environment variables"""
    os.environ["PREFECT_API_URL"] = "http://localhost:4201/api"
    os.environ["PREFECT_SERVER_API_HOST"] = "0.0.0.0"
    os.environ["PREFECT_SERVER_API_PORT"] = "4201"
    os.environ["PREFECT_UI_URL"] = "http://localhost:4201"

    print("✅ Prefect environment configured")


def create_work_pool():
    """Create default work pool for BHIV workflows"""
    try:
        # Check if work pool exists
        result = subprocess.run(["prefect", "work-pool", "ls"], capture_output=True, text=True, timeout=10)

        if "default-pool" not in result.stdout:
            # Create work pool
            subprocess.run(
                ["prefect", "work-pool", "create", "default-pool", "--type", "process"], check=True, timeout=30
            )
            print("✅ Created default-pool work pool")
        else:
            print("✅ default-pool work pool already exists")

    except Exception as e:
        print(f"⚠️  Work pool creation failed: {e}")


def start_minimal_server():
    """Start minimal Prefect server"""
    print("Starting BHIV Minimal Prefect Server...")

    try:
        # Start server with minimal configuration
        cmd = [
            "prefect",
            "server",
            "start",
            "--host",
            "0.0.0.0",
            "--port",
            "4201",
            "--log-level",
            "WARNING",  # Reduce log noise
        ]

        process = subprocess.Popen(cmd)

        # Wait for server to start
        time.sleep(10)

        # Check if server is running
        health_check = subprocess.run(
            ["curl", "-s", "http://localhost:4201/api/health"], capture_output=True, timeout=5
        )

        if health_check.returncode == 0:
            print("✅ Minimal Prefect server started successfully")
            print("📊 Server: http://localhost:4201")
            print("🔧 API: http://localhost:4201/api")
            return process
        else:
            print("❌ Server health check failed")
            return None

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None


def deploy_essential_workflows():
    """Deploy only essential BHIV workflows"""
    workflows_dir = Path(__file__).parent.parent / "workflows"

    essential_workflows = ["mcp_compliance_flow.py", "rl_integration_flows.py", "notification_flows.py"]

    deployed = 0
    for workflow in essential_workflows:
        workflow_path = workflows_dir / workflow

        if workflow_path.exists():
            try:
                subprocess.run([sys.executable, str(workflow_path)], check=True, timeout=60)
                print(f"✅ Deployed {workflow}")
                deployed += 1
            except Exception as e:
                print(f"❌ Failed to deploy {workflow}: {e}")
        else:
            print(f"⚠️  Workflow not found: {workflow}")

    print(f"📦 Deployed {deployed}/{len(essential_workflows)} workflows")


def main():
    """Main startup function"""
    print("🚀 BHIV Prefect Server Startup")
    print("=" * 40)

    # Setup environment
    setup_prefect_environment()

    # Start server
    server_process = start_minimal_server()

    if server_process:
        # Create work pool
        time.sleep(5)
        create_work_pool()

        # Deploy workflows
        time.sleep(5)
        deploy_essential_workflows()

        print("\n🎉 BHIV Prefect Server Ready!")
        print("Essential endpoints only:")
        print("- Flow management")
        print("- Flow run execution")
        print("- Task run monitoring")
        print("- Deployment management")
        print("- Work pool operations")
        print("- Health checks")
        print("- Logging")

        return server_process

    return None


if __name__ == "__main__":
    process = main()
    if process:
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Prefect server...")
            process.terminate()
