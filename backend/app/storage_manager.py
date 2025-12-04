"""
Storage Manager - Handle all file storage and directory management
Ensures all storage paths exist and are properly initialized
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class StorageManager:
    """Centralized storage management for BHIV system"""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd()
        self.storage_paths = self._initialize_storage_paths()
        self._ensure_directories_exist()

    def _initialize_storage_paths(self) -> Dict[str, Path]:
        """Initialize all required storage paths"""
        return {
            # Data directories
            "data": self.base_dir / "data",
            "pdfs": self.base_dir / "data" / "pdfs",
            "geometry_outputs": self.base_dir / "data" / "geometry_outputs",
            "mcp_rules": self.base_dir / "data" / "mcp_rules",
            "uploads": self.base_dir / "data" / "uploads",
            # Report directories
            "reports": self.base_dir / "reports",
            "validation": self.base_dir / "reports" / "validation",
            "geometry_verification": self.base_dir / "reports" / "geometry_verification",
            "logs": self.base_dir / "reports" / "logs",
            # Cache directories
            "cache": self.base_dir / "cache",
            "temp": self.base_dir / "temp",
            # Model directories
            "models": self.base_dir / "models_ckpt",
            "rl_models": self.base_dir / "models_ckpt" / "opt_ppo",
        }

    def _ensure_directories_exist(self):
        """Create all required directories"""
        for name, path in self.storage_paths.items():
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {path}")
            except Exception as e:
                logger.error(f"Failed to create directory {path}: {e}")

    def get_path(self, path_name: str) -> Path:
        """Get a storage path by name"""
        if path_name not in self.storage_paths:
            raise ValueError(f"Unknown storage path: {path_name}")
        return self.storage_paths[path_name]

    def create_sample_files(self):
        """Create sample files for testing"""
        try:
            # Create sample GLB file
            glb_dir = self.get_path("geometry_outputs")
            sample_glb = glb_dir / "sample_design.glb"
            if not sample_glb.exists():
                # Create minimal GLB file (just empty file for testing)
                sample_glb.write_bytes(b"GLB sample data")
                logger.info(f"Created sample GLB: {sample_glb}")

            # Create sample PDF directory structure
            pdf_dir = self.get_path("pdfs")
            for city in ["Mumbai", "Pune", "Ahmedabad", "Nashik"]:
                city_dir = pdf_dir / city
                city_dir.mkdir(exist_ok=True)

                sample_pdf = city_dir / f"{city}_DCR_Sample.pdf"
                if not sample_pdf.exists():
                    # Create placeholder PDF file
                    sample_pdf.write_text(f"Sample DCR document for {city}")
                    logger.info(f"Created sample PDF: {sample_pdf}")

            # Create sample MCP rules
            mcp_dir = self.get_path("mcp_rules")
            sample_rules = {
                "city": "Mumbai",
                "rules": [
                    {"type": "FSI", "value": 1.33, "category": "residential"},
                    {"type": "setback", "front": 3.0, "rear": 3.0, "side": 1.5},
                ],
                "last_updated": datetime.now().isoformat(),
            }

            rules_file = mcp_dir / "mumbai_rules.json"
            if not rules_file.exists():
                with open(rules_file, "w") as f:
                    json.dump(sample_rules, f, indent=2)
                logger.info(f"Created sample rules: {rules_file}")

        except Exception as e:
            logger.error(f"Failed to create sample files: {e}")

    def validate_storage(self) -> Dict[str, bool]:
        """Validate all storage paths are accessible"""
        results = {}

        for name, path in self.storage_paths.items():
            try:
                # Check if directory exists and is writable
                if path.exists() and path.is_dir():
                    # Test write access
                    test_file = path / ".write_test"
                    test_file.write_text("test")
                    test_file.unlink()
                    results[name] = True
                else:
                    results[name] = False
            except Exception as e:
                logger.error(f"Storage validation failed for {name}: {e}")
                results[name] = False

        return results

    def cleanup_temp_files(self, older_than_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        try:
            temp_dir = self.get_path("temp")
            cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)

            cleaned = 0
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned += 1

            logger.info(f"Cleaned up {cleaned} temporary files")
            return cleaned

        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {e}")
            return 0


# Global storage manager instance
storage_manager = StorageManager()


def get_storage_path(path_name: str) -> Path:
    """Get storage path - convenience function"""
    return storage_manager.get_path(path_name)


def ensure_storage_ready():
    """Ensure all storage is ready - call this on startup"""
    storage_manager._ensure_directories_exist()
    storage_manager.create_sample_files()

    # Validate storage
    validation_results = storage_manager.validate_storage()
    failed_paths = [name for name, success in validation_results.items() if not success]

    if failed_paths:
        logger.warning(f"Storage validation failed for: {failed_paths}")
    else:
        logger.info("All storage paths validated successfully")

    return len(failed_paths) == 0
