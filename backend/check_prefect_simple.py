#!/usr/bin/env python3
"""
Check Prefect Connection Status
"""

import subprocess


def check_prefect_status():
    print("PREFECT CONNECTION STATUS CHECK")
    print("=" * 50)

    # Check if prefect is installed
    try:
        import prefect

        print(f"SUCCESS: Prefect installed v{prefect.__version__}")
    except ImportError:
        print("ERROR: Prefect not installed")
        return False

    # Check prefect CLI
    try:
        result = subprocess.run(["prefect", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("SUCCESS: Prefect CLI available")
        else:
            print("ERROR: Prefect CLI not working")
    except FileNotFoundError:
        print("ERROR: Prefect CLI not found")

    # Check current profile
    try:
        result = subprocess.run(["prefect", "profile", "ls"], capture_output=True, text=True)
        if result.returncode == 0:
            print("SUCCESS: Prefect profiles found")
            print(result.stdout)
        else:
            print("ERROR: Cannot list profiles")
    except Exception as e:
        print(f"ERROR: Profile check failed: {e}")

    # Check API connection
    try:
        result = subprocess.run(["prefect", "cloud", "workspace", "ls"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("SUCCESS: Connected to Prefect Cloud")
            print(result.stdout)
            return True
        else:
            print("ERROR: Not connected to Prefect Cloud")
            print("Details:", result.stderr)
            return False
    except Exception as e:
        print(f"ERROR: Cloud connection check failed: {e}")
        return False


if __name__ == "__main__":
    is_connected = check_prefect_status()

    if not is_connected:
        print("\n" + "=" * 50)
        print("PREFECT CLOUD CONNECTION SETUP NEEDED")
        print("=" * 50)
        print("Run these commands:")
        print("1. prefect cloud login")
        print("2. Follow authentication in browser")
        print("3. Select workspace")
        print("4. Run this script again")
