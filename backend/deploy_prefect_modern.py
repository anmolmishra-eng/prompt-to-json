#!/usr/bin/env python3
"""
Modern Prefect Deployment Script
Uses current Prefect 3.x API
"""
import asyncio
import subprocess
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def run_command(cmd, description):
    """Run command with error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"⚠️ {description} warning: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False


async def deploy_with_modern_api():
    """Deploy using modern Prefect API"""
    try:
        from workflows.pdf_to_mcp_flow import pdf_to_mcp_flow
        from workflows.system_health_flow import system_health_flow

        print("🚀 Deploying with modern Prefect API...")

        # Deploy health monitoring flow
        try:
            health_deployment = system_health_flow.serve(
                name="system-health-monitor",
                tags=["monitoring", "health", "system"],
                description="System health monitoring service",
                interval=300,  # 5 minutes
            )
            print("✅ Health monitoring flow deployed")
        except Exception as e:
            print(f"⚠️ Health flow deployment: {e}")

        # Deploy PDF processing flow
        try:
            pdf_deployment = pdf_to_mcp_flow.serve(
                name="pdf-to-mcp-processor",
                tags=["compliance", "pdf", "mcp"],
                description="PDF compliance rule extraction service",
            )
            print("✅ PDF processing flow deployed")
        except Exception as e:
            print(f"⚠️ PDF flow deployment: {e}")

        return True

    except Exception as e:
        print(f"❌ Modern API deployment failed: {e}")
        return False


def main():
    """Main deployment process"""
    print("🚀 Modern Prefect Deployment")
    print("=" * 50)

    # Method 1: Try modern API deployment
    print("\n📦 Method 1: Modern API Deployment")
    modern_success = asyncio.run(deploy_with_modern_api())

    if not modern_success:
        print("\n📦 Method 2: Command Line Deployment")

        # Method 2: Use command line deployment
        commands = [
            (f"{sys.executable} -m prefect work-pool create default --type process", "Creating work pool"),
            (
                f"{sys.executable} -m prefect deploy workflows/system_health_flow.py:system_health_flow --name health-monitor --pool default",
                "Deploying health monitor",
            ),
            (
                f"{sys.executable} -m prefect deploy workflows/pdf_to_mcp_flow.py:pdf_to_mcp_flow --name pdf-processor --pool default",
                "Deploying PDF processor",
            ),
        ]

        success_count = 0
        for cmd, desc in commands:
            if run_command(cmd, desc):
                success_count += 1

        print(f"\n📊 Command deployment: {success_count}/{len(commands)} successful")

    print("\n✅ Deployment process complete!")
    print("\n📋 Next steps:")
    print("1. Start worker: python -m prefect worker start --pool default")
    print("2. Check UI: http://localhost:4200 (if using local server)")
    print("3. Monitor flows in Prefect dashboard")
    print("4. Use local fallback: python deploy_health_local.py --continuous")


if __name__ == "__main__":
    main()
