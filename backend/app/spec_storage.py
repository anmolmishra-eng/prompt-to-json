"""
Spec Storage Manager - Enforces local JSON storage
All specs MUST be stored locally, no exceptions
"""
import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SpecStorageManager:
    """Manages local storage of spec JSON files"""

    def __init__(self, storage_dir: str = "data/specs"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Spec storage initialized: {self.storage_dir}")

    def save(self, spec_id: str, spec_json: Dict) -> str:
        """Save spec JSON locally - REQUIRED"""
        spec_file = self.storage_dir / f"{spec_id}.json"

        # Ensure spec_id is in the JSON
        if "spec_id" not in spec_json:
            spec_json["spec_id"] = spec_id

        with open(spec_file, "w") as f:
            json.dump(spec_json, f, indent=2)

        logger.info(f"Spec saved locally: {spec_id}")
        return str(spec_file)

    def load(self, spec_id: str) -> Optional[Dict]:
        """Load spec from local storage"""
        spec_file = self.storage_dir / f"{spec_id}.json"

        if not spec_file.exists():
            logger.warning(f"Spec not found locally: {spec_id}")
            return None

        with open(spec_file) as f:
            return json.load(f)

    def exists(self, spec_id: str) -> bool:
        """Check if spec exists locally"""
        return (self.storage_dir / f"{spec_id}.json").exists()

    def delete(self, spec_id: str) -> bool:
        """Delete spec from local storage"""
        spec_file = self.storage_dir / f"{spec_id}.json"

        if spec_file.exists():
            spec_file.unlink()
            logger.info(f"Spec deleted: {spec_id}")
            return True

        return False

    def list_all(self) -> list:
        """List all stored spec IDs"""
        return [f.stem for f in self.storage_dir.glob("*.json")]


# Global instance
spec_storage = SpecStorageManager()
