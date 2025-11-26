#!/usr/bin/env python3
"""
Comprehensive import checker for the backend folder
Identifies all import issues and missing dependencies
"""

import importlib
import os
import sys
import traceback
from pathlib import Path


def check_file_imports(file_path):
    """Check imports in a single Python file"""
    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract import statements
        import_lines = []
        for line_num, line in enumerate(content.split("\n"), 1):
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                import_lines.append((line_num, line))

        # Test each import
        for line_num, import_line in import_lines:
            try:
                # Skip relative imports for now
                if import_line.startswith("from .") or import_line.startswith("from app."):
                    continue

                # Check if import is inside a try block (look at previous lines)
                is_in_try_block = False
                lines = content.split("\n")
                for i in range(max(0, line_num - 10), line_num):
                    if i < len(lines) and lines[i].strip().startswith("try:"):
                        is_in_try_block = True
                        break
                    elif i < len(lines) and lines[i].strip().startswith("except"):
                        is_in_try_block = False
                        break

                # Skip imports that are properly handled in try blocks
                if is_in_try_block:
                    continue

                # Extract module name
                if import_line.startswith("import "):
                    module_name = import_line.split()[1].split(".")[0]
                elif import_line.startswith("from "):
                    module_name = import_line.split()[1].split(".")[0]
                else:
                    continue

                # Try to import
                importlib.import_module(module_name)

            except ImportError as e:
                issues.append(
                    {"file": file_path, "line": line_num, "import": import_line, "error": str(e), "type": "ImportError"}
                )
            except Exception as e:
                issues.append(
                    {
                        "file": file_path,
                        "line": line_num,
                        "import": import_line,
                        "error": str(e),
                        "type": type(e).__name__,
                    }
                )

    except Exception as e:
        issues.append({"file": file_path, "line": 0, "import": "FILE_READ_ERROR", "error": str(e), "type": "FileError"})

    return issues


def find_python_files(directory):
    """Find all Python files in directory"""
    python_files = []

    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {"__pycache__", ".git", "venv", "env", "node_modules", ".pytest_cache"}
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def main():
    """Main function to check all imports"""
    backend_dir = Path(__file__).parent
    print(f"Checking imports in: {backend_dir}")

    # Add backend to Python path
    sys.path.insert(0, str(backend_dir))

    # Find all Python files
    python_files = find_python_files(backend_dir)
    print(f"Found {len(python_files)} Python files")

    all_issues = []

    # Check each file
    for file_path in python_files:
        rel_path = os.path.relpath(file_path, backend_dir)
        print(f"Checking: {rel_path}")

        issues = check_file_imports(file_path)
        all_issues.extend(issues)

    # Summary
    print(f"\n{'='*60}")
    print(f"IMPORT CHECK SUMMARY")
    print(f"{'='*60}")
    print(f"Files checked: {len(python_files)}")
    print(f"Issues found: {len(all_issues)}")

    if all_issues:
        print(f"\n{'='*60}")
        print(f"ISSUES FOUND:")
        print(f"{'='*60}")

        # Group by error type
        by_type = {}
        for issue in all_issues:
            error_type = issue["type"]
            if error_type not in by_type:
                by_type[error_type] = []
            by_type[error_type].append(issue)

        for error_type, issues in by_type.items():
            print(f"\n{error_type} ({len(issues)} issues):")
            print("-" * 40)

            for issue in issues:
                rel_path = os.path.relpath(issue["file"], backend_dir)
                print(f"  {rel_path}:{issue['line']}")
                print(f"    Import: {issue['import']}")
                print(f"    Error: {issue['error']}")
                print()

    else:
        print("No import issues found!")

    return len(all_issues)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(min(exit_code, 1))  # Return 1 if any issues found
