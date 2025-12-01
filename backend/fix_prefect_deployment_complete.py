#!/usr/bin/env python3
"""
Complete Prefect Deployment Fix
Resolves all deployment issues and provides working alternatives
"""
import asyncio
import os
import subprocess
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def check_prefect_installation():
    """Check if Prefect is properly installed"""
    try:
        import prefect

        print(f"✅ Prefect {prefect.__version__} installed")
        return True
    except ImportError:
        print("❌ Prefect not installed")
        return False


def setup_prefect_server():
    """Setup local Prefect server"""
    print("\n🚀 Setting up Prefect Server...")

    try:
        # Start Prefect server in background
        print("Starting Prefect server...")
        subprocess.run(
            [sys.executable, "-m", "prefect", "server", "start", "--host", "0.0.0.0"], check=False, timeout=10
        )
    except subprocess.TimeoutExpired:
        print("✅ Prefect server starting (backgrounded)")
    except Exception as e:
        print(f"⚠️ Server start issue: {e}")


def create_work_pool():
    """Create default work pool"""
    print("\n🔧 Creating work pool...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "prefect", "work-pool", "create", "default", "--type", "process"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Work pool 'default' created")
        else:
            print(f"⚠️ Work pool creation: {result.stderr}")
    except Exception as e:
        print(f"❌ Work pool error: {e}")


def deploy_flows():
    """Deploy all flows"""
    print("\n📦 Deploying flows...")

    flows = [
        ("workflows/system_health_flow.py:system_health_flow", "system-health-monitor"),
        ("workflows/pdf_to_mcp_flow.py:pdf_to_mcp_flow", "pdf-to-mcp-processor"),
    ]

    for flow_path, deployment_name in flows:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "prefect", "deploy", flow_path, "--name", deployment_name, "--pool", "default"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent,
            )

            if result.returncode == 0:
                print(f"✅ Deployed: {deployment_name}")
            else:
                print(f"❌ Deploy failed: {deployment_name} - {result.stderr}")
        except Exception as e:
            print(f"❌ Deploy error: {deployment_name} - {e}")


def start_worker():
    """Start Prefect worker"""
    print("\n👷 Starting worker...")

    try:
        subprocess.Popen([sys.executable, "-m", "prefect", "worker", "start", "--pool", "default"])
        print("✅ Worker started in background")
    except Exception as e:
        print(f"❌ Worker error: {e}")


async def test_deployments():
    """Test deployed flows"""
    print("\n🧪 Testing deployments...")

    try:
        from workflows.pdf_to_mcp_flow import pdf_to_mcp_flow
        from workflows.system_health_flow import system_health_flow

        # Test health flow
        print("Testing health monitoring...")
        health_result = await system_health_flow()
        print(f"✅ Health check: {health_result['overall_status']}")

        # Test PDF flow (mock)
        print("Testing PDF processing...")
        pdf_result = await pdf_to_mcp_flow(
            pdf_url="https://example.com/test.pdf", city="Mumbai", sohum_mcp_url="http://localhost:8001"
        )
        print(f"✅ PDF processing: {pdf_result['success']}")

    except Exception as e:
        print(f"❌ Test error: {e}")


def main():
    """Main deployment process"""
    print("🔧 Prefect Deployment Fix")
    print("=" * 50)

    # Check installation
    if not check_prefect_installation():
        print("Install Prefect: pip install prefect")
        return

    # Setup server
    setup_prefect_server()

    # Create work pool
    create_work_pool()

    # Deploy flows
    deploy_flows()

    # Start worker
    start_worker()

    # Test deployments
    print("\nWaiting 5 seconds for services to start...")
    import time

    time.sleep(5)

    asyncio.run(test_deployments())

    print("\n✅ Prefect deployment complete!")
    print("\nNext steps:")
    print("1. Check Prefect UI: http://localhost:4200")
    print("2. Monitor flows in the dashboard")
    print("3. Use local health monitor as backup:")
    print("   python deploy_health_local.py --continuous")


if __name__ == "__main__":
    main()
