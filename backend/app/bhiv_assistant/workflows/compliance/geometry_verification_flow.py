"""
Prefect Flow: Geometry/GLB Output Verification
Verifies that generated GLB files meet quality standards
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List

from prefect import flow, task
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Import trimesh with fallback
try:
    import trimesh
except ImportError:
    try:
        # Try installing trimesh if not available
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "trimesh"])
        import trimesh

        logger.info("Trimesh installed successfully")
    except Exception:
        trimesh = None
        logger.warning("Trimesh not available - geometry validation will be limited")


class GeometryConfig(BaseModel):
    """Configuration for geometry verification"""

    glb_source_dir: Path = Path("data/geometry_outputs")
    output_dir: Path = Path("reports/geometry_verification")
    max_file_size_mb: float = 50.0  # Max GLB file size

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.glb_source_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


@task(name="scan-glb-files")
def scan_glb_files(source_dir: Path) -> List[Path]:
    """Scan directory for GLB files"""
    if not source_dir.exists():
        source_dir.mkdir(parents=True, exist_ok=True)
        return []

    glb_files = list(source_dir.glob("**/*.glb"))
    logger.info(f"Found {len(glb_files)} GLB files to verify")

    return glb_files


@task(name="verify-glb-file")
async def verify_glb_file(glb_path: Path, max_size_mb: float) -> Dict:
    """
    Verify a single GLB file
    Checks:
    - File size
    - File integrity
    - Basic geometry validation
    """
    try:
        if trimesh is None:
            # Basic file validation without trimesh
            file_size_mb = glb_path.stat().st_size / (1024 * 1024)
            size_ok = file_size_mb <= max_size_mb

            # Basic file format check
            is_glb = glb_path.suffix.lower() == ".glb"
            file_exists = glb_path.exists() and glb_path.stat().st_size > 0

            return {
                "filename": glb_path.name,
                "file_size_mb": round(file_size_mb, 2),
                "size_ok": size_ok,
                "is_valid": is_glb and file_exists and size_ok,
                "status": "pass" if (is_glb and file_exists and size_ok) else "fail",
                "issues": []
                if (is_glb and file_exists and size_ok)
                else ["Basic validation only - trimesh not available"],
                "validation_type": "basic",
            }

        # Check file size
        file_size_mb = glb_path.stat().st_size / (1024 * 1024)

        size_ok = file_size_mb <= max_size_mb

        # Load and validate geometry
        try:
            mesh = trimesh.load(str(glb_path))

            # Enhanced validation
            if hasattr(mesh, "vertices") and hasattr(mesh, "faces"):
                has_vertices = len(mesh.vertices) > 0
                has_faces = len(mesh.faces) > 0
                is_watertight = mesh.is_watertight if hasattr(mesh, "is_watertight") else False

                is_valid = has_vertices and has_faces

                # Additional geometry checks
                validation_details = {
                    "vertex_count": len(mesh.vertices),
                    "face_count": len(mesh.faces),
                    "is_watertight": is_watertight,
                    "bounds": mesh.bounds.tolist() if hasattr(mesh, "bounds") else None,
                }
            else:
                is_valid = False
                validation_details = {"error": "Mesh object missing vertices or faces"}

        except Exception as e:
            logger.error(f"Failed to load GLB {glb_path.name}: {e}")
            is_valid = False
            validation_details = {"error": str(e)}

        result = {
            "filename": glb_path.name,
            "file_size_mb": round(file_size_mb, 2),
            "size_ok": size_ok,
            "is_valid": is_valid,
            "status": "pass" if (size_ok and is_valid) else "fail",
            "validation_type": "full",
            "geometry_details": validation_details,
        }

        issues = []
        if not size_ok:
            issues.append(f"File size {file_size_mb:.2f}MB exceeds limit {max_size_mb}MB")
        if not is_valid:
            issues.append("Geometry validation failed")

        if issues:
            result["issues"] = issues

        return result

    except Exception as e:
        logger.error(f"Verification failed for {glb_path.name}: {e}")
        return {
            "filename": glb_path.name,
            "status": "error",
            "error": str(e),
            "file_size_mb": 0,
            "size_ok": False,
            "is_valid": False,
        }


@task(name="generate-verification-report")
def generate_verification_report(results: List[Dict], output_dir: Path) -> Path:
    """Generate verification report"""
    import json
    from datetime import datetime

    output_dir.mkdir(parents=True, exist_ok=True)

    report_file = output_dir / f"geometry_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    passed = [r for r in results if r.get("status") == "pass"]
    failed = [r for r in results if r.get("status") == "fail"]
    errors = [r for r in results if r.get("status") == "error"]

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(results),
        "passed": len(passed),
        "failed": len(failed),
        "errors": len(errors),
        "pass_rate": f"{(len(passed) / len(results) * 100):.1f}%" if results else "0%",
        "results": results,
    }

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Verification report saved to {report_file}")
    logger.info(f"Pass rate: {report['pass_rate']} ({len(passed)}/{len(results)})")

    return report_file


@flow(name="geometry-verification", description="Verify GLB geometry outputs meet quality standards", version="1.0")
async def geometry_verification_flow(config: GeometryConfig = GeometryConfig()):
    """
    Main flow: Scan GLB files → Verify each → Generate report
    """
    logger.info("Starting geometry verification flow...")

    # Step 1: Scan for GLB files
    glb_files = scan_glb_files(config.glb_source_dir)

    if not glb_files:
        logger.info("No GLB files found to verify")
        return {"status": "no_files", "verified": 0}

    # Step 2: Verify each file
    verification_tasks = [verify_glb_file(glb_file, config.max_file_size_mb) for glb_file in glb_files]

    results = await asyncio.gather(*verification_tasks)

    # Step 3: Generate report
    report_file = generate_verification_report(results, config.output_dir)

    logger.info("Geometry verification flow complete")

    return {"status": "complete", "total_files": len(results), "report_file": str(report_file)}


# Deployment
if __name__ == "__main__":
    asyncio.run(geometry_verification_flow())
