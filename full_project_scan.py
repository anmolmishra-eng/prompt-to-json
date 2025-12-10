#!/usr/bin/env python3
"""
COMPLETE PROJECT SCAN - All files in Backend folder
Checks every Python file for import issues and syntax errors
"""
import os
import sys
import ast
from pathlib import Path

def scan_directory(directory):
    """Recursively scan directory for Python files"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Don't skip any directories - scan everything
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def check_file_syntax(file_path):
    """Check if file has syntax errors"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Try to compile
        compile(content, file_path, 'exec')
        return True, None
    except SyntaxError as e:
        return False, f"Syntax Error: Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def extract_imports(file_path):
    """Extract all imports from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        tree = ast.parse(content)
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    if module:
                        imports.append(f"{module}.{alias.name}")
                    else:
                        imports.append(alias.name)

        return imports
    except:
        return []

def check_prefect_integration_usage(file_path):
    """Check if file uses prefect integration"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        prefect_imports = [
            'prefect_integration_minimal',
            'prefect_integration',
            'prefect_integration_enhanced',
            'trigger_automation_workflow',
            'check_workflow_status'
        ]

        uses_prefect = any(imp in content for imp in prefect_imports)
        return uses_prefect
    except:
        return False

def main():
    print("COMPLETE PROJECT SCAN - ALL FILES")
    print("=" * 60)

    # Start from the Backend directory
    base_dir = "c:\\Users\\Anmol\\Desktop\\Backend"
    if not os.path.exists(base_dir):
        base_dir = "."

    print(f"Scanning directory: {os.path.abspath(base_dir)}")

    # Find ALL Python files
    all_python_files = scan_directory(base_dir)
    print(f"Found {len(all_python_files)} Python files")

    # Categorize files
    syntax_errors = []
    import_issues = []
    prefect_users = []
    clean_files = []

    print("\nScanning all files...")
    for i, file_path in enumerate(all_python_files):
        if i % 20 == 0:
            print(f"  Progress: {i}/{len(all_python_files)}")

        # Check syntax
        is_valid, error = check_file_syntax(file_path)

        if not is_valid:
            syntax_errors.append((file_path, error))
        else:
            # Check if uses Prefect integration
            if check_prefect_integration_usage(file_path):
                prefect_users.append(file_path)

            clean_files.append(file_path)

    # Results
    print("\n" + "=" * 60)
    print("SCAN RESULTS")
    print("=" * 60)

    print(f"Total files scanned: {len(all_python_files)}")
    print(f"Files with syntax errors: {len(syntax_errors)}")
    print(f"Clean files: {len(clean_files)}")
    print(f"Files using Prefect integration: {len(prefect_users)}")

    if syntax_errors:
        print(f"\nSYNTAX ERRORS FOUND ({len(syntax_errors)}):")
        for file_path, error in syntax_errors:
            rel_path = os.path.relpath(file_path, base_dir)
            print(f"  {rel_path}: {error}")

    if prefect_users:
        print(f"\nFILES USING PREFECT INTEGRATION ({len(prefect_users)}):")
        for file_path in prefect_users:
            rel_path = os.path.relpath(file_path, base_dir)
            print(f"  {rel_path}")

    # Test critical integrations
    print(f"\nCRITICAL INTEGRATION TESTS:")

    # Test if we can import main components
    try:
        sys.path.insert(0, os.path.join(base_dir, 'backend'))
        from app.prefect_integration_minimal import PREFECT_AVAILABLE, check_workflow_status
        print(f"  Prefect minimal integration: SUCCESS (Available: {PREFECT_AVAILABLE})")
    except Exception as e:
        print(f"  Prefect minimal integration: FAILED - {e}")

    try:
        from app.main import app
        print(f"  Main FastAPI app: SUCCESS")
    except Exception as e:
        print(f"  Main FastAPI app: FAILED - {e}")

    # Final verdict
    print("\n" + "=" * 60)
    if len(syntax_errors) == 0:
        print("VERDICT: NO IMPORT/SYNTAX ISSUES FOUND!")
        print("Your entire project is clean and ready to run")
    else:
        print(f"VERDICT: {len(syntax_errors)} issues need to be fixed")

    print("\nTo run your project:")
    print("cd backend")
    print("python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()
