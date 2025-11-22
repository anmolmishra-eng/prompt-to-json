#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify all dependencies can be installed and imported
Run this before committing to catch dependency issues early
"""

import importlib
import os
import subprocess
import sys

# Set UTF-8 encoding for Windows
if os.name == "nt":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")


def test_requirements_syntax():
    """Test if requirements-ci.txt has valid syntax"""
    print("[TESTING] Checking requirements file syntax...")
    try:
        with open("requirements-ci.txt", "r") as f:
            lines = f.readlines()

        invalid_lines = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith("#"):
                # Basic syntax validation
                if (
                    "==" in line
                    and not line.replace("==", "")
                    .replace(".", "")
                    .replace("-", "")
                    .replace("_", "")
                    .replace("[", "")
                    .replace("]", "")
                    .replace(" ", "")
                    .isalnum()
                ):
                    invalid_lines.append(f"Line {i}: {line}")

        if invalid_lines:
            print(f"[FAIL] Invalid syntax found:")
            for line in invalid_lines:
                print(f"  {line}")
            return False
        else:
            print("[PASS] Requirements file syntax is valid")
            return True
    except Exception as e:
        print(f"[ERROR] Error reading requirements file: {e}")
        return False


def test_core_imports():
    """Test if core modules can be imported"""
    print("[TESTING] Checking core imports...")
    core_modules = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "jwt", "httpx"]

    failed_imports = []
    for module in core_modules:
        try:
            importlib.import_module(module)
            print(f"[PASS] {module}")
        except ImportError:
            print(f"[FAIL] {module}")
            failed_imports.append(module)

    return len(failed_imports) == 0


def main():
    print("Testing dependencies before commit...\n")

    syntax_ok = test_requirements_syntax()
    import_ok = test_core_imports()

    if syntax_ok and import_ok:
        print("\n[SUCCESS] All dependency tests passed! Safe to commit.")
        return 0
    else:
        print("\n[FAILED] Dependency issues found. Fix before committing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
