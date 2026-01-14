"""
Data & Storage Integrity Audit System
Ensures all design artifacts are stored and retrievable
"""
import json
import logging
import os
from datetime import datetime
from typing import Optional

from app.database import get_current_user, get_db
from app.models import ComplianceCheck, Evaluation, Iteration, Spec
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/audit/spec/{spec_id}")
async def audit_spec(
    spec_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Complete audit of a single spec with all artifacts"""
    spec = db.query(Spec).filter(Spec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")

    # Check database records
    iterations = db.query(Iteration).filter(Iteration.spec_id == spec_id).all()
    evaluations = db.query(Evaluation).filter(Evaluation.spec_id == spec_id).all()
    compliance = db.query(ComplianceCheck).filter(ComplianceCheck.spec_id == spec_id).all()

    # Check local file storage
    local_checks = {
        "spec_json_file": _check_local_file(f"data/specs/{spec_id}.json"),
        "preview_file": _check_preview_files(spec_id),
        "geometry_file": _check_geometry_files(spec_id),
        "evaluation_files": _check_evaluation_files(spec_id),
        "compliance_files": _check_compliance_files(spec_id),
    }

    # Verify URLs are accessible
    url_checks = {
        "preview_url": _verify_url(spec.preview_url),
        "geometry_url": _verify_url(spec.geometry_url),
    }

    # Build integrity report
    integrity = {
        "spec_id": spec_id,
        "database": {
            "spec_exists": True,
            "spec_json_valid": spec.spec_json is not None and isinstance(spec.spec_json, dict),
            "has_preview_url": spec.preview_url is not None,
            "has_geometry_url": spec.geometry_url is not None,
            "iterations_count": len(iterations),
            "evaluations_count": len(evaluations),
            "compliance_count": len(compliance),
        },
        "local_storage": local_checks,
        "url_accessibility": url_checks,
        "artifacts": {
            "spec_json": spec.spec_json is not None,
            "preview": spec.preview_url is not None or local_checks["preview_file"]["exists"],
            "geometry": spec.geometry_url is not None or local_checks["geometry_file"]["exists"],
            "evaluations": len(evaluations) > 0 or local_checks["evaluation_files"]["count"] > 0,
            "compliance": len(compliance) > 0 or local_checks["compliance_files"]["count"] > 0,
        },
        "audit_timestamp": datetime.now().isoformat(),
        "audited_by": current_user,
    }

    # Calculate completeness score
    total_checks = 10
    passed_checks = sum(
        [
            integrity["database"]["spec_json_valid"],
            integrity["database"]["has_preview_url"] or local_checks["preview_file"]["exists"],
            integrity["database"]["has_geometry_url"] or local_checks["geometry_file"]["exists"],
            len(iterations) > 0,
            len(evaluations) > 0,
            len(compliance) > 0,
            local_checks["spec_json_file"]["exists"],
            local_checks["preview_file"]["exists"],
            local_checks["geometry_file"]["exists"],
            url_checks["preview_url"] or url_checks["geometry_url"],
        ]
    )

    integrity["completeness_score"] = round((passed_checks / total_checks) * 100, 2)
    integrity["status"] = "PASS" if passed_checks >= 7 else "FAIL"

    return integrity


@router.get("/audit/user/{user_id}")
async def audit_user_data(
    user_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Audit all data for a specific user"""
    specs = db.query(Spec).filter(Spec.user_id == user_id).all()

    if not specs:
        return {
            "user_id": user_id,
            "total_specs": 0,
            "status": "NO_DATA",
            "message": "No specs found for this user",
        }

    audit_results = []
    for spec in specs:
        iterations = db.query(Iteration).filter(Iteration.spec_id == spec.id).count()
        evaluations = db.query(Evaluation).filter(Evaluation.spec_id == spec.id).count()
        compliance = db.query(ComplianceCheck).filter(ComplianceCheck.spec_id == spec.id).count()

        audit_results.append(
            {
                "spec_id": spec.id,
                "has_json": spec.spec_json is not None,
                "has_preview": spec.preview_url is not None,
                "has_geometry": spec.geometry_url is not None,
                "iterations": iterations,
                "evaluations": evaluations,
                "compliance": compliance,
                "created_at": spec.created_at.isoformat() if spec.created_at else None,
            }
        )

    summary = {
        "user_id": user_id,
        "total_specs": len(specs),
        "specs_with_json": sum(1 for r in audit_results if r["has_json"]),
        "specs_with_preview": sum(1 for r in audit_results if r["has_preview"]),
        "specs_with_geometry": sum(1 for r in audit_results if r["has_geometry"]),
        "total_iterations": sum(r["iterations"] for r in audit_results),
        "total_evaluations": sum(r["evaluations"] for r in audit_results),
        "total_compliance": sum(r["compliance"] for r in audit_results),
        "audit_timestamp": datetime.now().isoformat(),
        "audited_by": current_user,
    }

    return {
        "summary": summary,
        "specs": audit_results,
        "status": "PASS" if summary["specs_with_json"] == len(specs) else "INCOMPLETE",
    }


@router.get("/audit/storage")
async def audit_storage(
    current_user: str = Depends(get_current_user),
):
    """Audit all local storage directories"""
    storage_dirs = [
        "data/specs",
        "data/previews",
        "data/geometry_outputs",
        "data/evaluations",
        "data/compliance",
        "data/reports",
        "data/uploads",
    ]

    storage_audit = {}
    for dir_path in storage_dirs:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            storage_audit[dir_path] = {
                "exists": True,
                "file_count": len(files),
                "total_size_mb": _get_dir_size(dir_path),
                "sample_files": files[:5],
            }
        else:
            storage_audit[dir_path] = {
                "exists": False,
                "file_count": 0,
                "total_size_mb": 0,
            }

    return {
        "storage_audit": storage_audit,
        "audit_timestamp": datetime.now().isoformat(),
        "audited_by": current_user,
    }


@router.get("/audit/integrity")
async def audit_data_integrity(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(100, description="Number of specs to audit"),
):
    """Comprehensive data integrity audit across all specs"""
    specs = db.query(Spec).order_by(Spec.created_at.desc()).limit(limit).all()

    integrity_report = {
        "total_specs_audited": len(specs),
        "specs_with_complete_data": 0,
        "specs_with_missing_data": 0,
        "missing_artifacts": {
            "spec_json": 0,
            "preview_url": 0,
            "geometry_url": 0,
            "iterations": 0,
            "evaluations": 0,
            "compliance": 0,
        },
        "specs_by_status": {},
        "audit_timestamp": datetime.now().isoformat(),
        "audited_by": current_user,
    }

    for spec in specs:
        iterations = db.query(Iteration).filter(Iteration.spec_id == spec.id).count()
        evaluations = db.query(Evaluation).filter(Evaluation.spec_id == spec.id).count()
        compliance = db.query(ComplianceCheck).filter(ComplianceCheck.spec_id == spec.id).count()

        # Check completeness
        is_complete = all(
            [
                spec.spec_json is not None,
                spec.preview_url is not None,
                spec.geometry_url is not None,
            ]
        )

        if is_complete:
            integrity_report["specs_with_complete_data"] += 1
        else:
            integrity_report["specs_with_missing_data"] += 1

        # Track missing artifacts
        if spec.spec_json is None:
            integrity_report["missing_artifacts"]["spec_json"] += 1
        if spec.preview_url is None:
            integrity_report["missing_artifacts"]["preview_url"] += 1
        if spec.geometry_url is None:
            integrity_report["missing_artifacts"]["geometry_url"] += 1
        if iterations == 0:
            integrity_report["missing_artifacts"]["iterations"] += 1
        if evaluations == 0:
            integrity_report["missing_artifacts"]["evaluations"] += 1
        if compliance == 0:
            integrity_report["missing_artifacts"]["compliance"] += 1

        # Track by status
        status = spec.status or "unknown"
        integrity_report["specs_by_status"][status] = integrity_report["specs_by_status"].get(status, 0) + 1

    # Calculate integrity score
    total_possible = len(specs) * 6  # 6 artifacts per spec
    total_missing = sum(integrity_report["missing_artifacts"].values())
    integrity_report["integrity_score"] = (
        round(((total_possible - total_missing) / total_possible) * 100, 2) if total_possible > 0 else 0
    )
    integrity_report["status"] = "PASS" if integrity_report["integrity_score"] >= 80 else "NEEDS_ATTENTION"

    return integrity_report


@router.post("/audit/fix/{spec_id}")
async def fix_spec_integrity(
    spec_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Attempt to fix missing artifacts for a spec"""
    spec = db.query(Spec).filter(Spec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")

    fixes_applied = []

    # Fix missing spec_json from local file
    if spec.spec_json is None:
        local_file = f"data/specs/{spec_id}.json"
        if os.path.exists(local_file):
            with open(local_file, "r") as f:
                spec.spec_json = json.load(f)
            fixes_applied.append("Restored spec_json from local file")

    # Check for preview files
    if spec.preview_url is None:
        preview_files = _find_files_by_pattern(f"data/previews", spec_id)
        if preview_files:
            spec.preview_url = f"/local/previews/{preview_files[0]}"
            fixes_applied.append(f"Found preview file: {preview_files[0]}")

    # Check for geometry files
    if spec.geometry_url is None:
        geometry_files = _find_files_by_pattern(f"data/geometry_outputs", spec_id)
        if geometry_files:
            spec.geometry_url = f"/local/geometry/{geometry_files[0]}"
            fixes_applied.append(f"Found geometry file: {geometry_files[0]}")

    if fixes_applied:
        db.commit()

    return {
        "spec_id": spec_id,
        "fixes_applied": fixes_applied,
        "fixed_count": len(fixes_applied),
        "status": "FIXED" if fixes_applied else "NO_FIXES_NEEDED",
        "timestamp": datetime.now().isoformat(),
    }


# Helper functions
def _check_local_file(filepath: str) -> dict:
    """Check if a local file exists"""
    exists = os.path.exists(filepath)
    size = os.path.getsize(filepath) if exists else 0
    return {"exists": exists, "size_bytes": size, "path": filepath}


def _check_preview_files(spec_id: str) -> dict:
    """Check for preview files"""
    preview_dir = "data/previews"
    if not os.path.exists(preview_dir):
        return {"exists": False, "count": 0}

    files = [f for f in os.listdir(preview_dir) if spec_id in f and not f.endswith("_metadata.json")]
    return {"exists": len(files) > 0, "count": len(files), "files": files}


def _check_geometry_files(spec_id: str) -> dict:
    """Check for geometry files"""
    geometry_dir = "data/geometry_outputs"
    if not os.path.exists(geometry_dir):
        return {"exists": False, "count": 0}

    files = [f for f in os.listdir(geometry_dir) if spec_id in f and not f.endswith("_metadata.json")]
    return {"exists": len(files) > 0, "count": len(files), "files": files}


def _check_evaluation_files(spec_id: str) -> dict:
    """Check for evaluation files"""
    eval_dir = "data/evaluations"
    if not os.path.exists(eval_dir):
        return {"exists": False, "count": 0}

    files = [f for f in os.listdir(eval_dir) if spec_id in f]
    return {"exists": len(files) > 0, "count": len(files), "files": files}


def _check_compliance_files(spec_id: str) -> dict:
    """Check for compliance files"""
    compliance_dir = "data/compliance"
    if not os.path.exists(compliance_dir):
        return {"exists": False, "count": 0}

    files = [f for f in os.listdir(compliance_dir) if spec_id in f]
    return {"exists": len(files) > 0, "count": len(files), "files": files}


def _verify_url(url: Optional[str]) -> bool:
    """Verify if URL is accessible (basic check)"""
    if not url:
        return False
    # For local URLs, check file existence
    if url.startswith("/local/"):
        filepath = url.replace("/local/", "data/")
        return os.path.exists(filepath)
    # For external URLs, assume accessible (avoid network calls)
    return url.startswith("http")


def _get_dir_size(directory: str) -> float:
    """Get total size of directory in MB"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception:
        pass
    return round(total_size / (1024 * 1024), 2)


def _find_files_by_pattern(directory: str, pattern: str) -> list:
    """Find files matching pattern in directory"""
    if not os.path.exists(directory):
        return []
    return [f for f in os.listdir(directory) if pattern in f and not f.endswith("_metadata.json")]
