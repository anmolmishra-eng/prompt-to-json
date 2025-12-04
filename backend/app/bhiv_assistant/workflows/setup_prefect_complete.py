"""
Complete Prefect Setup and Deployment Script
Run this to set up and deploy all BHIV workflows
"""

import asyncio
import subprocess
import sys
from pathlib import Path


def install_prefect():
    """Install Prefect if not available"""
    try:
        import prefect

        print("✅ Prefect already installed")
        return True
    except ImportError:
        print("📦 Installing Prefect...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "prefect"])
            print("✅ Prefect installed successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to install Prefect: {e}")
            return False


def setup_prefect_server():
    """Set up Prefect server configuration"""
    try:
        # Set Prefect API URL to local server
        subprocess.run(
            [sys.executable, "-m", "prefect", "config", "set", "PREFECT_API_URL=http://localhost:4200/api"], check=True
        )

        print("✅ Prefect server configuration set")
        return True
    except Exception as e:
        print(f"❌ Failed to configure Prefect: {e}")
        return False


def create_work_pool():
    """Create default work pool"""
    try:
        # Create work pool
        result = subprocess.run(
            [sys.executable, "-m", "prefect", "work-pool", "create", "default-pool", "--type", "process"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 or "already exists" in result.stderr:
            print("✅ Work pool 'default-pool' ready")
            return True
        else:
            print(f"⚠️ Work pool creation: {result.stderr}")
            return True  # Continue anyway
    except Exception as e:
        print(f"❌ Failed to create work pool: {e}")
        return False


async def deploy_workflows():
    """Deploy all BHIV workflows"""
    try:
        print("🚀 Deploying BHIV workflows...")

        # Import and deploy workflows
        from .deploy_all_flows import deploy_all_workflows

        result = await deploy_all_workflows()

        if result["status"] == "success":
            print("✅ All workflows deployed successfully")
            return True
        else:
            print(f"❌ Deployment failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Failed to deploy workflows: {e}")
        return False


def start_prefect_server():
    """Instructions to start Prefect server"""
    print("\n" + "=" * 50)
    print("🎯 PREFECT SETUP COMPLETE!")
    print("=" * 50)
    print("\n📋 Next Steps:")
    print("1. Start Prefect server:")
    print("   prefect server start")
    print("\n2. In another terminal, start worker:")
    print("   prefect worker start --pool default-pool")
    print("\n3. Access Prefect UI:")
    print("   http://localhost:4200")
    print("\n4. Test workflows:")
    print("   python workflows/test_all_flows.py")
    print("=" * 50)


async def main():
    """Main setup function"""
    print("🔧 Setting up BHIV Prefect Workflows...")
    print("=" * 50)

    # Step 1: Install Prefect
    if not install_prefect():
        return False

    # Step 2: Configure Prefect
    if not setup_prefect_server():
        return False

    # Step 3: Create work pool
    if not create_work_pool():
        return False

    # Step 4: Deploy workflows
    if not await deploy_workflows():
        return False

    # Step 5: Show next steps
    start_prefect_server()

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed. Check errors above.")
        sys.exit(1)
