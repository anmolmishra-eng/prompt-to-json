#!/usr/bin/env python3
"""
Comprehensive Import Validation
Validates all imports across the entire project
"""
import ast
import importlib.util
import os
import sys
from pathlib import Path


def find_python_files(directory):
    """Find all Python files in directory"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def check_imports_in_file(file_path):
    """Check all imports in a single file"""
    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse AST
        tree = ast.parse(content, filename=file_path)

        # Check imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    try:
                        importlib.import_module(alias.name)
                    except ImportError as e:
                        issues.append(f"Import error: {alias.name} - {e}")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    try:
                        if node.level > 0:  # Relative import
                            # Handle relative imports
                            continue
                        else:
                            importlib.import_module(node.module)
                    except ImportError as e:
                        issues.append(f"ImportFrom error: {node.module} - {e}")

    except SyntaxError as e:
        issues.append(f"Syntax error: {e}")
    except Exception as e:
        issues.append(f"Parse error: {e}")

    return issues


def main():
    """Main validation process"""
    print("Comprehensive Import Validation")
    print("=" * 50)

    # Get project root
    project_root = Path(__file__).parent
    print(f"Checking project: {project_root}")

    # Find all Python files
    python_files = find_python_files(project_root)
    print(f"Found {len(python_files)} Python files")

    # Check each file
    total_issues = 0
    files_with_issues = 0

    for file_path in python_files:
        rel_path = os.path.relpath(file_path, project_root)
        issues = check_imports_in_file(file_path)

        if issues:
            files_with_issues += 1
            total_issues += len(issues)
            print(f"\nERROR {rel_path}:")
            for issue in issues:
                print(f"   {issue}")

    # Summary
    print("\n" + "=" * 50)
    print("IMPORT VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Files checked: {len(python_files)}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total issues: {total_issues}")

    if total_issues == 0:
        print("All imports are valid!")
        return True
    else:
        print("Import issues found!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
