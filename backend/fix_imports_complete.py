#!/usr/bin/env python3
"""
Complete Import Issues Fix
Resolves all remaining import issues in the project
"""
import os
import re
from pathlib import Path


def fix_bhiv_assistant_imports():
    """Fix BHIV assistant import issues"""
    fixes = [
        # Fix config imports
        {
            "file": "app/bhiv_assistant/start_bhiv.py",
            "old": "from config.integration_config import",
            "new": "from .config.integration_config import",
        },
        {
            "file": "app/bhiv_assistant/validate_api.py",
            "old": "from config.integration_config import",
            "new": "from .config.integration_config import",
        },
        {
            "file": "app/bhiv_assistant/app/main.py",
            "old": "from config.integration_config import",
            "new": "from ...config.integration_config import",
        },
        # Fix app imports
        {
            "file": "app/bhiv_assistant/run_tests.py",
            "old": "from app.main_bhiv import",
            "new": "from .app.main_bhiv import",
        },
        {
            "file": "app/bhiv_assistant/validate_api.py",
            "old": "from app.bhiv_layer.assistant_api import",
            "new": "from .app.bhiv_layer.assistant_api import",
        },
        # Fix workflow imports
        {
            "file": "app/bhiv_assistant/workflows/deploy_all_flows.py",
            "old": "from workflows.compliance.geometry_verification_flow import",
            "new": "from .compliance.geometry_verification_flow import",
        },
        {
            "file": "app/bhiv_assistant/workflows/deploy_all_flows.py",
            "old": "from workflows.ingestion.pdf_to_mcp_flow import",
            "new": "from .ingestion.pdf_to_mcp_flow import",
        },
        {
            "file": "app/bhiv_assistant/workflows/deploy_all_flows.py",
            "old": "from workflows.monitoring.log_aggregation_flow import",
            "new": "from .monitoring.log_aggregation_flow import",
        },
    ]

    return fixes


def fix_optional_imports():
    """Fix optional dependency imports"""
    fixes = [
        # Fix reportlab import
        {
            "file": "fix_404_error.py",
            "old": "from reportlab.pdfgen import canvas\n        from reportlab.lib.pagesizes import letter",
            "new": "try:\n            from reportlab.pdfgen import canvas\n            from reportlab.lib.pagesizes import letter\n        except ImportError:\n            canvas = None\n            letter = None",
        },
        # Fix trimesh import (already handled)
        {
            "file": "app/bhiv_assistant/workflows/compliance/geometry_verification_flow.py",
            "old": "import trimesh",
            "new": "try:\n    import trimesh\nexcept ImportError:\n    trimesh = None",
        },
        # Fix trl import (already handled)
        {"file": "app/rlhf/train_rlhf.py", "old": "from trl import", "new": "try:\n    from trl import"},
    ]

    return fixes


def apply_fix(file_path, old_text, new_text):
    """Apply a single fix to a file"""
    try:
        if not os.path.exists(file_path):
            print(f"   File not found: {file_path}")
            return False

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if old_text in content:
            content = content.replace(old_text, new_text)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"   Fixed: {file_path}")
            return True
        else:
            print(f"   Pattern not found in: {file_path}")
            return False

    except Exception as e:
        print(f"   Error fixing {file_path}: {e}")
        return False


def main():
    """Main fix process"""
    print("Complete Import Issues Fix")
    print("=" * 50)

    project_root = Path(__file__).parent

    # Get all fixes
    all_fixes = fix_bhiv_assistant_imports() + fix_optional_imports()

    # Apply fixes
    fixed_count = 0
    for fix in all_fixes:
        file_path = project_root / fix["file"]
        if apply_fix(file_path, fix["old"], fix["new"]):
            fixed_count += 1

    print(f"\nApplied {fixed_count} fixes")

    # Create missing __init__.py files
    missing_inits = [
        "app/bhiv_assistant/config/__init__.py",
        "app/bhiv_assistant/workflows/__init__.py",
        "app/bhiv_assistant/workflows/compliance/__init__.py",
        "app/bhiv_assistant/workflows/ingestion/__init__.py",
        "app/bhiv_assistant/workflows/monitoring/__init__.py",
    ]

    print("\nCreating missing __init__.py files:")
    for init_file in missing_inits:
        init_path = project_root / init_file
        init_path.parent.mkdir(parents=True, exist_ok=True)

        if not init_path.exists():
            init_path.write_text("# Package initialization\n")
            print(f"   Created: {init_file}")
        else:
            print(f"   Exists: {init_file}")

    print("\nImport fixes complete!")


if __name__ == "__main__":
    main()
