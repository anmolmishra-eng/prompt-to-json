"""
Setup Prefect Infrastructure for BHIV Workflows
Cross-platform Python setup script
"""

import subprocess
import sys
import os
import time
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors"""
    print(f"Running: {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] {description or 'Command completed'}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"[ERROR] {description or 'Command failed'}")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"[ERROR] Exception running command: {e}")
        return False


def setup_prefect():
    """Setup Prefect infrastructure"""
    print("Setting up Prefect workflow orchestration...")
    print("=" * 60)
    
    # Step 1: Install Prefect packages
    print("\n[1/5] Installing Prefect packages...")
    packages = [
        "prefect==2.14.3",
        "prefect-docker==0.4.1", 
        "prefect-sqlalchemy==0.2.4"
    ]
    
    for package in packages:
        success = run_command(f"pip install {package}", f"Installing {package}")
        if not success:
            print(f"[WARNING] Failed to install {package}, continuing...")
    
    # Step 2: Set API URL
    print("\n[2/5] Configuring Prefect API URL...")
    run_command(
        'prefect config set PREFECT_API_URL="http://localhost:4200/api"',
        "Setting API URL"
    )
    
    # Step 3: Create directory structure
    print("\n[3/5] Creating workflow directories...")
    base_dir = Path(__file__).parent
    directories = [
        base_dir / "ingestion",
        base_dir / "monitoring", 
        base_dir / "compliance"
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"[OK] Created directory: {directory}")
        except Exception as e:
            print(f"[ERROR] Failed to create {directory}: {e}")
    
    # Step 4: Check Prefect installation
    print("\n[4/5] Verifying Prefect installation...")
    run_command("prefect version", "Checking Prefect version")
    
    # Step 5: Instructions for manual steps
    print("\n[5/5] Setup complete!")
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Start Prefect server:")
    print("   prefect server start")
    print()
    print("2. In another terminal, create work pool:")
    print("   prefect work-pool create default-pool --type process")
    print()
    print("3. Access Prefect UI:")
    print("   http://localhost:4200")
    print()
    print("4. Start a worker (optional):")
    print("   prefect worker start --pool default-pool")
    print("=" * 60)


if __name__ == "__main__":
    setup_prefect()