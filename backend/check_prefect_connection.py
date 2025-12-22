#!/usr/bin/env python3
"""
Check Prefect Connection Status
"""

import os
import subprocess
import sys


def check_prefect_status():
    print("PREFECT CONNECTION STATUS CHECK")
    print("=" * 50)

    # Check if prefect is installed
    try:
        import prefect

        print(f"✅ Prefect installed: v{prefect.__version__}")
    except ImportError:
        print("❌ Prefect not installed")
        return False

    # Check prefect CLI
    try:
        result = subprocess.run(["prefect", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Prefect CLI available")
        else:
            print("❌ Prefect CLI not working")
    except FileNotFoundError:
        print("❌ Prefect CLI not found")

    # Check current profile
    try:
        result = subprocess.run(["prefect", "profile", "ls"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Prefect profiles:")
            print(result.stdout)
        else:
            print("❌ Cannot list profiles")
    except Exception as e:
        print(f"❌ Profile check failed: {e}")

    # Check API connection
    try:
        result = subprocess.run(["prefect", "cloud", "workspace", "ls"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Connected to Prefect Cloud:")
            print(result.stdout)
            return True
        else:
            print("❌ Not connected to Prefect Cloud")
            print("Error:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Cloud connection check failed: {e}")
        return False


if __name__ == "__main__":
    is_connected = check_prefect_status()

    if not is_connected:
        print("\n" + "=" * 50)
        print("PREFECT CLOUD CONNECTION SETUP NEEDED")
        print("=" * 50)
        print("Follow these steps to connect:")
        print("1. prefect cloud login")
        print("2. Follow the authentication flow")
        print("3. Select your workspace")
        print("4. Run this script again to verify")
