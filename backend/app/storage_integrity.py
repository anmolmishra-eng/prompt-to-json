"""
Storage Manager with Data Integrity
Ensures all design artifacts are stored with proper metadata and retrievability
"""
import json
import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages storage of all design artifacts with integrity checks"""

    def __init__(self):
        self.base_dir = "data"
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure all storage directories exist"""
        dirs = [
            "data/specs",
            "data/previews",
            "data/geometry_outputs",
            "data/evaluations",
            "data/compliance",
            "data/reports",
            "data/uploads",
            "data/iterations",
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def store_spec(self, spec_id: str, spec_json: dict, metadata: Optional[dict] = None) -> str:
        """Store spec JSON with metadata"""
        try:
            filepath = f"data/specs/{spec_id}.json"

            # Store main spec
            with open(filepath, "w") as f:
                json.dump(spec_json, f, indent=2)

            # Store metadata
            if metadata:
                metadata_path = f"data/specs/{spec_id}_metadata.json"
                metadata["stored_at"] = datetime.now().isoformat()
                metadata["file_path"] = filepath
                metadata["file_size"] = os.path.getsize(filepath)

                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)

            logger.info(f"✅ Stored spec: {spec_id}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Failed to store spec {spec_id}: {e}")
            raise

    def store_preview(self, spec_id: str, preview_data: bytes, file_type: str = "glb") -> str:
        """Store preview file (GLB, PNG, JPG)"""
        try:
            timestamp = int(datetime.now().timestamp())
            filename = f"{spec_id}_{timestamp}.{file_type}"
            filepath = f"data/previews/{filename}"

            with open(filepath, "wb") as f:
                f.write(preview_data)

            # Store metadata
            metadata = {
                "spec_id": spec_id,
                "file_type": file_type,
                "file_size": len(preview_data),
                "stored_at": datetime.now().isoformat(),
                "file_path": filepath,
            }

            metadata_path = f"data/previews/{spec_id}_{timestamp}_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"✅ Stored preview: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Failed to store preview for {spec_id}: {e}")
            raise

    def store_geometry(self, spec_id: str, geometry_data: bytes, file_type: str = "glb") -> str:
        """Store geometry file (GLB, STL, OBJ)"""
        try:
            timestamp = int(datetime.now().timestamp())
            filename = f"{spec_id}_{timestamp}.{file_type}"
            filepath = f"data/geometry_outputs/{filename}"

            with open(filepath, "wb") as f:
                f.write(geometry_data)

            # Store metadata
            metadata = {
                "spec_id": spec_id,
                "file_type": file_type,
                "file_size": len(geometry_data),
                "stored_at": datetime.now().isoformat(),
                "file_path": filepath,
            }

            metadata_path = f"data/geometry_outputs/{spec_id}_{timestamp}_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"✅ Stored geometry: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Failed to store geometry for {spec_id}: {e}")
            raise

    def store_evaluation(self, spec_id: str, evaluation_data: dict) -> str:
        """Store evaluation results"""
        try:
            timestamp = int(datetime.now().timestamp())
            filename = f"eval_{spec_id}_{timestamp}.json"
            filepath = f"data/evaluations/{filename}"

            evaluation_data["stored_at"] = datetime.now().isoformat()
            evaluation_data["spec_id"] = spec_id

            with open(filepath, "w") as f:
                json.dump(evaluation_data, f, indent=2)

            # Also append to JSONL for easy querying
            jsonl_path = "data/evaluations/evaluations.jsonl"
            with open(jsonl_path, "a") as f:
                f.write(json.dumps(evaluation_data) + "\n")

            logger.info(f"✅ Stored evaluation: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Failed to store evaluation for {spec_id}: {e}")
            raise

    def store_compliance(self, spec_id: str, case_id: str, compliance_data: dict) -> str:
        """Store compliance check results"""
        try:
            timestamp = int(datetime.now().timestamp())
            filename = f"{case_id}_{timestamp}.json"
            filepath = f"data/compliance/{filename}"

            compliance_data["stored_at"] = datetime.now().isoformat()
            compliance_data["spec_id"] = spec_id
            compliance_data["case_id"] = case_id

            with open(filepath, "w") as f:
                json.dump(compliance_data, f, indent=2)

            logger.info(f"✅ Stored compliance: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Failed to store compliance for {spec_id}: {e}")
            raise

    def store_iteration(self, spec_id: str, iteration_id: str, iteration_data: dict) -> str:
        """Store iteration results"""
        try:
            filename = f"{iteration_id}.json"
            filepath = f"data/iterations/{filename}"

            iteration_data["stored_at"] = datetime.now().isoformat()
            iteration_data["spec_id"] = spec_id
            iteration_data["iteration_id"] = iteration_id

            with open(filepath, "w") as f:
                json.dump(iteration_data, f, indent=2)

            logger.info(f"✅ Stored iteration: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Failed to store iteration {iteration_id}: {e}")
            raise

    def retrieve_spec(self, spec_id: str) -> Optional[dict]:
        """Retrieve spec JSON"""
        try:
            filepath = f"data/specs/{spec_id}.json"
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to retrieve spec {spec_id}: {e}")
            return None

    def retrieve_metadata(self, spec_id: str, artifact_type: str) -> Optional[dict]:
        """Retrieve metadata for any artifact"""
        try:
            # Find metadata file
            search_dirs = {
                "spec": "data/specs",
                "preview": "data/previews",
                "geometry": "data/geometry_outputs",
                "evaluation": "data/evaluations",
                "compliance": "data/compliance",
                "iteration": "data/iterations",
            }

            search_dir = search_dirs.get(artifact_type)
            if not search_dir or not os.path.exists(search_dir):
                return None

            # Find metadata files for this spec
            for filename in os.listdir(search_dir):
                if spec_id in filename and filename.endswith("_metadata.json"):
                    filepath = os.path.join(search_dir, filename)
                    with open(filepath, "r") as f:
                        return json.load(f)

            return None

        except Exception as e:
            logger.error(f"❌ Failed to retrieve metadata for {spec_id}: {e}")
            return None

    def check_integrity(self, spec_id: str) -> dict:
        """Check integrity of all artifacts for a spec"""
        integrity = {
            "spec_id": spec_id,
            "artifacts": {},
            "complete": True,
        }

        # Check spec JSON
        spec_path = f"data/specs/{spec_id}.json"
        integrity["artifacts"]["spec_json"] = {
            "exists": os.path.exists(spec_path),
            "path": spec_path if os.path.exists(spec_path) else None,
        }

        # Check previews
        preview_files = self._find_files("data/previews", spec_id)
        integrity["artifacts"]["previews"] = {
            "exists": len(preview_files) > 0,
            "count": len(preview_files),
            "files": preview_files,
        }

        # Check geometry
        geometry_files = self._find_files("data/geometry_outputs", spec_id)
        integrity["artifacts"]["geometry"] = {
            "exists": len(geometry_files) > 0,
            "count": len(geometry_files),
            "files": geometry_files,
        }

        # Check evaluations
        eval_files = self._find_files("data/evaluations", spec_id)
        integrity["artifacts"]["evaluations"] = {
            "exists": len(eval_files) > 0,
            "count": len(eval_files),
            "files": eval_files,
        }

        # Check compliance
        compliance_files = self._find_files("data/compliance", spec_id)
        integrity["artifacts"]["compliance"] = {
            "exists": len(compliance_files) > 0,
            "count": len(compliance_files),
            "files": compliance_files,
        }

        # Check iterations
        iteration_files = self._find_files("data/iterations", spec_id)
        integrity["artifacts"]["iterations"] = {
            "exists": len(iteration_files) > 0,
            "count": len(iteration_files),
            "files": iteration_files,
        }

        # Determine completeness
        integrity["complete"] = all(
            [
                integrity["artifacts"]["spec_json"]["exists"],
                integrity["artifacts"]["previews"]["exists"] or integrity["artifacts"]["geometry"]["exists"],
            ]
        )

        return integrity

    def _find_files(self, directory: str, pattern: str) -> list:
        """Find files matching pattern in directory"""
        if not os.path.exists(directory):
            return []

        files = []
        for filename in os.listdir(directory):
            if pattern in filename and not filename.endswith("_metadata.json"):
                files.append(filename)

        return files

    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        stats = {
            "directories": {},
            "total_size_mb": 0,
            "total_files": 0,
        }

        dirs = [
            "data/specs",
            "data/previews",
            "data/geometry_outputs",
            "data/evaluations",
            "data/compliance",
            "data/reports",
            "data/uploads",
            "data/iterations",
        ]

        for dir_path in dirs:
            if os.path.exists(dir_path):
                files = os.listdir(dir_path)
                size = sum(
                    os.path.getsize(os.path.join(dir_path, f))
                    for f in files
                    if os.path.isfile(os.path.join(dir_path, f))
                )

                stats["directories"][dir_path] = {
                    "file_count": len(files),
                    "size_mb": round(size / (1024 * 1024), 2),
                }

                stats["total_files"] += len(files)
                stats["total_size_mb"] += stats["directories"][dir_path]["size_mb"]

        stats["total_size_mb"] = round(stats["total_size_mb"], 2)

        return stats


# Global storage manager instance
storage_manager = StorageManager()
