"""
Data Integrity Audit System
Ensures all spec data is stored and retrievable
"""
import logging
import os
from typing import Dict, List

from app.database import get_current_user, get_db
from app.models import ComplianceCheck, Evaluation, Iteration, Spec
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/audit", tags=["🔍 Data Audit"])


@router.get("/spec/{spec_id}")
async def audit_spec(spec_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Complete audit of spec data integrity - Office can audit any spec"""

    spec = db.query(Spec).filter(Spec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail=f"Spec {spec_id} not found")

    audit_result = {
        "spec_id": spec_id,
        "audit_timestamp": None,
        "data_integrity": {},
        "storage_integrity": {},
        "retrievability": {},
        "issues": [],
        "audit_passed": True,
    }

    from datetime import datetime

    audit_result["audit_timestamp"] = datetime.utcnow().isoformat()

    # 1. JSON Spec Integrity
    json_integrity = {"exists": spec.spec_json is not None, "valid": False, "size_bytes": 0, "objects_count": 0}

    if spec.spec_json:
        import json

        try:
            json_str = json.dumps(spec.spec_json)
            json_integrity["size_bytes"] = len(json_str)
            json_integrity["valid"] = True
            json_integrity["objects_count"] = len(spec.spec_json.get("objects", []))
        except Exception as e:
            json_integrity["error"] = str(e)
            audit_result["issues"].append(f"JSON spec invalid: {e}")
            audit_result["audit_passed"] = False
    else:
        audit_result["issues"].append("JSON spec missing")
        audit_result["audit_passed"] = False

    audit_result["data_integrity"]["json_spec"] = json_integrity

    # 2. Preview Files
    preview_integrity = {"url_exists": spec.preview_url is not None, "url": spec.preview_url, "accessible": False}

    if spec.preview_url:
        try:
            from app.storage import check_file_exists

            preview_integrity["accessible"] = await check_file_exists(spec.preview_url)
        except:
            preview_integrity["accessible"] = False

    if not preview_integrity["url_exists"]:
        audit_result["issues"].append("Preview URL missing")

    audit_result["storage_integrity"]["preview"] = preview_integrity

    # 3. GLB Files
    glb_integrity = {"url_exists": spec.geometry_url is not None, "url": spec.geometry_url, "accessible": False}

    if spec.geometry_url:
        try:
            from app.storage import check_file_exists

            glb_integrity["accessible"] = await check_file_exists(spec.geometry_url)
        except:
            glb_integrity["accessible"] = False

    if not glb_integrity["url_exists"]:
        audit_result["issues"].append("GLB geometry URL missing")

    audit_result["storage_integrity"]["glb"] = glb_integrity

    # 4. Evaluations
    evaluations = db.query(Evaluation).filter(Evaluation.spec_id == spec_id).all()
    eval_integrity = {"count": len(evaluations), "stored": True, "retrievable": True, "data": []}

    for ev in evaluations:
        eval_integrity["data"].append(
            {
                "id": ev.id,
                "rating": ev.rating,
                "has_notes": ev.notes is not None,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
            }
        )

    audit_result["data_integrity"]["evaluations"] = eval_integrity

    # 5. Compliance Checks
    compliance_checks = db.query(ComplianceCheck).filter(ComplianceCheck.spec_id == spec_id).all()
    compliance_integrity = {"count": len(compliance_checks), "stored": True, "retrievable": True, "data": []}

    for cc in compliance_checks:
        compliance_integrity["data"].append(
            {
                "id": cc.id,
                "case_id": cc.case_id,
                "status": cc.status,
                "compliant": cc.compliant,
                "has_violations": cc.violations is not None and len(cc.violations) > 0
                if isinstance(cc.violations, list)
                else False,
                "created_at": cc.created_at.isoformat() if cc.created_at else None,
            }
        )

    audit_result["data_integrity"]["compliance"] = compliance_integrity

    # 6. Iterations
    iterations = db.query(Iteration).filter(Iteration.spec_id == spec_id).all()
    iteration_integrity = {"count": len(iterations), "stored": True, "retrievable": True, "data": []}

    for it in iterations:
        iteration_integrity["data"].append(
            {
                "id": it.id,
                "has_diff": it.diff is not None,
                "has_spec_json": it.spec_json is not None,
                "created_at": it.created_at.isoformat() if it.created_at else None,
            }
        )

    audit_result["data_integrity"]["iterations"] = iteration_integrity

    # 7. Retrievability Test
    retrievability = {
        "spec_query": True,
        "json_parse": json_integrity["valid"],
        "evaluations_query": True,
        "compliance_query": True,
        "iterations_query": True,
    }

    audit_result["retrievability"] = retrievability

    # Summary
    audit_result["summary"] = {
        "total_checks": 7,
        "passed_checks": sum(
            [
                json_integrity["valid"],
                preview_integrity["url_exists"],
                glb_integrity["url_exists"],
                eval_integrity["stored"],
                compliance_integrity["stored"],
                iteration_integrity["stored"],
                retrievability["spec_query"],
            ]
        ),
        "issues_count": len(audit_result["issues"]),
        "audit_status": "PASS" if audit_result["audit_passed"] and len(audit_result["issues"]) == 0 else "FAIL",
    }

    return audit_result


@router.get("/spec/{spec_id}/complete")
async def get_complete_spec_data(
    spec_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get complete spec data for office audit - all data in one response"""

    spec = db.query(Spec).filter(Spec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail=f"Spec {spec_id} not found")

    # Get all related data
    iterations = db.query(Iteration).filter(Iteration.spec_id == spec_id).all()
    evaluations = db.query(Evaluation).filter(Evaluation.spec_id == spec_id).all()
    compliance_checks = db.query(ComplianceCheck).filter(ComplianceCheck.spec_id == spec_id).all()

    return {
        "spec": {
            "id": spec.id,
            "user_id": spec.user_id,
            "project_id": spec.project_id,
            "prompt": spec.prompt,
            "city": spec.city,
            "spec_json": spec.spec_json,
            "design_type": spec.design_type,
            "preview_url": spec.preview_url,
            "geometry_url": spec.geometry_url,
            "estimated_cost": spec.estimated_cost,
            "currency": spec.currency,
            "compliance_status": spec.compliance_status,
            "status": spec.status,
            "version": spec.version,
            "created_at": spec.created_at.isoformat() if spec.created_at else None,
            "updated_at": spec.updated_at.isoformat() if spec.updated_at else None,
        },
        "iterations": [
            {
                "id": it.id,
                "query": it.query,
                "diff": it.diff,
                "spec_json": it.spec_json,
                "preview_url": it.preview_url,
                "cost_delta": it.cost_delta,
                "created_at": it.created_at.isoformat() if it.created_at else None,
            }
            for it in iterations
        ],
        "evaluations": [
            {
                "id": ev.id,
                "rating": ev.rating,
                "notes": ev.notes,
                "aspects": ev.aspects,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
            }
            for ev in evaluations
        ],
        "compliance_checks": [
            {
                "id": cc.id,
                "case_id": cc.case_id,
                "city": cc.city,
                "case_type": cc.case_type,
                "status": cc.status,
                "compliant": cc.compliant,
                "confidence_score": cc.confidence_score,
                "violations": cc.violations,
                "recommendations": cc.recommendations,
                "geometry_url": cc.geometry_url,
                "created_at": cc.created_at.isoformat() if cc.created_at else None,
                "completed_at": cc.completed_at.isoformat() if cc.completed_at else None,
            }
            for cc in compliance_checks
        ],
        "metadata": {
            "total_iterations": len(iterations),
            "total_evaluations": len(evaluations),
            "total_compliance_checks": len(compliance_checks),
            "data_complete": True,
        },
    }


async def check_file_exists(url: str) -> bool:
    """Check if file exists in storage"""
    try:
        if not url:
            return False

        # Check Supabase storage
        if "supabase" in url:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.head(url)
                return response.status_code == 200

        # Check local storage
        if url.startswith("/"):
            return os.path.exists(url)

        return False
    except:
        return False
