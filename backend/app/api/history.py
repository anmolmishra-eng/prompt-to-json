from typing import Optional

from app.database import get_current_user, get_db
from app.models import Evaluation, Iteration, Spec
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/history/{spec_id}")
async def get_spec_history(
    spec_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(
        50, description="Maximum number of iterations to return"
    ),
):
    """Get complete history for a specific spec including iterations and evaluations"""

    # Get the spec
    spec = db.query(Spec).filter(Spec.spec_id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")

    # Get iterations
    iterations = (
        db.query(Iteration)
        .filter(Iteration.spec_id == spec_id)
        .order_by(Iteration.ts.desc())
        .limit(limit)
        .all()
    )

    # Get evaluations
    evaluations = (
        db.query(Evaluation)
        .filter(Evaluation.spec_id == spec_id)
        .order_by(Evaluation.ts.desc())
        .limit(limit)
        .all()
    )

    return {
        "spec_id": spec_id,
        "spec": {
            "spec_id": spec.spec_id,
            "user_id": spec.user_id,
            "project_id": spec.project_id,
            "prompt": spec.prompt,
            "spec_json": spec.spec_json,
            "spec_version": spec.spec_version,
            "created_at": spec.created_at,
            "updated_at": spec.updated_at,
        },
        "iterations": [
            {
                "iter_id": iter.iter_id,
                "before_spec": iter.before_spec,
                "after_spec": iter.after_spec,
                "feedback": iter.feedback,
                "timestamp": iter.ts,
            }
            for iter in iterations
        ],
        "evaluations": [
            {
                "eval_id": eval.eval_id,
                "user_id": eval.user_id,
                "score": eval.score,
                "notes": eval.notes,
                "timestamp": eval.ts,
            }
            for eval in evaluations
        ],
        "total_iterations": len(iterations),
        "total_evaluations": len(evaluations),
    }


@router.get("/history")
async def get_user_history(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(20, description="Maximum number of specs to return"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
):
    """Get history of all specs for the current user"""

    query = db.query(Spec).filter(Spec.user_id == current_user)

    if project_id:
        query = query.filter(Spec.project_id == project_id)

    specs = query.order_by(Spec.updated_at.desc()).limit(limit).all()

    return {
        "user_id": current_user,
        "specs": [
            {
                "spec_id": spec.spec_id,
                "project_id": spec.project_id,
                "prompt": spec.prompt,
                "spec_version": spec.spec_version,
                "created_at": spec.created_at,
                "updated_at": spec.updated_at,
            }
            for spec in specs
        ],
        "total_specs": len(specs),
    }
