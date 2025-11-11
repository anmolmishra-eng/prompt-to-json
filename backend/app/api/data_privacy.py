import logging

from app.database import get_current_user, get_db
from app.models import Evaluation, Iteration, RLHFFeedback, RLHFPreferences, Spec
from app.storage import supabase
from app.utils import log_audit_event
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/data/{user_id}/export")
async def export_user_data(
    user_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """GDPR-style data export - get all user data"""

    # Only allow users to export their own data or admin access
    if current_user != user_id and current_user != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    # Collect all user data
    specs = db.query(Spec).filter(Spec.user_id == user_id).all()
    evaluations = db.query(Evaluation).filter(Evaluation.user_id == user_id).all()
    iterations = db.query(Iteration).join(Spec).filter(Spec.user_id == user_id).all()
    rlhf_feedback = db.query(RLHFFeedback).filter(RLHFFeedback.user_id == user_id).all()
    rlhf_preferences = (
        db.query(RLHFPreferences).filter(RLHFPreferences.user_id == user_id).all()
    )

    # Format export data
    export_data = {
        "user_id": user_id,
        "export_timestamp": "2025-11-11T00:00:00Z",
        "data": {
            "specs": [
                {
                    "spec_id": spec.spec_id,
                    "prompt": spec.prompt,
                    "spec_json": spec.spec_json,
                    "project_id": spec.project_id,
                    "created_at": spec.created_at.isoformat(),
                    "updated_at": spec.updated_at.isoformat(),
                }
                for spec in specs
            ],
            "evaluations": [
                {
                    "eval_id": eval.eval_id,
                    "spec_id": eval.spec_id,
                    "score": eval.score,
                    "notes": eval.notes,
                    "timestamp": eval.ts.isoformat(),
                }
                for eval in evaluations
            ],
            "iterations": [
                {
                    "iter_id": iter.iter_id,
                    "spec_id": iter.spec_id,
                    "feedback": iter.feedback,
                    "timestamp": iter.ts.isoformat(),
                }
                for iter in iterations
            ],
            "rlhf_data": {
                "feedback_count": len(rlhf_feedback),
                "preferences_count": len(rlhf_preferences),
            },
        },
    }

    # Log export request
    log_audit_event("data_export", user_id, {"exported_by": current_user})

    return export_data


@router.delete("/data/{user_id}")
async def delete_user_data(
    user_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """GDPR-style data deletion - wipe all user designs and data"""

    # Only allow users to delete their own data or admin access
    if current_user != user_id and current_user != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        # Get all user specs for file cleanup
        specs = db.query(Spec).filter(Spec.user_id == user_id).all()
        spec_ids = [spec.spec_id for spec in specs]

        # Delete from database (cascading deletes will handle related records)
        db.query(RLHFFeedback).filter(RLHFFeedback.user_id == user_id).delete()
        db.query(RLHFPreferences).filter(RLHFPreferences.user_id == user_id).delete()
        db.query(Evaluation).filter(Evaluation.user_id == user_id).delete()

        # Delete iterations for user specs
        for spec_id in spec_ids:
            db.query(Iteration).filter(Iteration.spec_id == spec_id).delete()

        # Delete specs
        db.query(Spec).filter(Spec.user_id == user_id).delete()

        # Delete files from Supabase storage
        deleted_files = []
        for spec_id in spec_ids:
            try:
                # Delete preview files
                supabase.storage.from_("previews").remove([f"{spec_id}.glb"])
                # Delete geometry files
                supabase.storage.from_("geometry").remove([f"{spec_id}.stl"])
                deleted_files.append(spec_id)
            except Exception as e:
                logger.warning(f"Failed to delete files for spec {spec_id}: {e}")

        db.commit()

        # Log deletion (this will be the last audit log for this user)
        log_audit_event(
            "data_deletion",
            user_id,
            {
                "deleted_by": current_user,
                "specs_deleted": len(spec_ids),
                "files_deleted": len(deleted_files),
            },
        )

        return {
            "message": "User data successfully deleted",
            "user_id": user_id,
            "specs_deleted": len(spec_ids),
            "files_deleted": len(deleted_files),
            "deleted_at": "2025-11-11T00:00:00Z",
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete user data for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Data deletion failed")


@router.post("/auth/refresh")
async def refresh_token(current_user: str = Depends(get_current_user)):
    """Refresh JWT token for short-lived token strategy"""
    from app.utils import create_access_token

    # Create new token with fresh expiration
    new_token = create_access_token({"sub": current_user})

    # Log token refresh
    log_audit_event("token_refresh", current_user, {"new_token_issued": True})

    return {
        "access_token": new_token,
        "token_type": "bearer",
        "expires_in": 3600,  # 1 hour
    }
