#!/usr/bin/env python3
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def search_in_file(filepath, patterns):
    """Search for patterns in a file"""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            found = []
            for pattern_name, pattern in patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    found.append(pattern_name)
            return found
    except:
        return []


def scan_project():
    """Scan project for service URL usage"""
    patterns = {
        "SOHUM_MCP_URL": r"SOHUM_MCP_URL|SOHAM_URL|ai-rule-api",
        "RANJEET_RL_URL": r"RANJEET_RL_URL|land-utilization-rl",
        "sohum_integration": r"sohum|compliance.*check|mcp",
        "ranjeet_integration": r"ranjeet|land.*utilization|rl.*feedback",
    }

    results = {}

    # Scan backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))

    for root, dirs, files in os.walk(backend_dir):
        # Skip cache and temp directories
        dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git", "node_modules", "cache", "temp"]]

        for file in files:
            if file.endswith((".py", ".md", ".txt", ".env", ".yaml", ".yml")):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, backend_dir)

                found = search_in_file(filepath, patterns)
                if found:
                    results[rel_path] = found

    return results


def check_config_values():
    """Check actual config values"""
    try:
        from app.config import settings

        print("CONFIG VALUES:")
        print(f"  SOHUM_MCP_URL: {settings.SOHUM_MCP_URL}")
        print(f"  RANJEET_RL_URL: {settings.RANJEET_RL_URL}")
        print(f"  LAND_UTILIZATION_MOCK_MODE: {settings.LAND_UTILIZATION_MOCK_MODE}")
        print(f"  RANJEET_SERVICE_AVAILABLE: {settings.RANJEET_SERVICE_AVAILABLE}")
        return True
    except Exception as e:
        print(f"CONFIG ERROR: {e}")
        return False


def main():
    print("SERVICE URL INTEGRATION CHECK")
    print("=" * 50)

    # Check config
    config_ok = check_config_values()
    print()

    # Scan files
    print("FILE USAGE SCAN:")
    results = scan_project()

    if not results:
        print("  No service URL references found!")
        return

    for filepath, patterns in results.items():
        print(f"  {filepath}: {', '.join(patterns)}")

    print()
    print("INTEGRATION SUMMARY:")

    # Check key integrations
    key_files = ["app/config.py", "app/service_monitor.py", "app/api/compliance.py", "app/api/mock_rl.py"]

    for key_file in key_files:
        if any(key_file in path for path in results.keys()):
            print(f"  ✓ {key_file}: INTEGRATED")
        else:
            print(f"  ✗ {key_file}: NOT FOUND")


if __name__ == "__main__":
    main()
