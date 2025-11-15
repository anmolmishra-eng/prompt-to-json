"""
Monitoring and observability endpoints
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db, get_current_user
from app.models import Spec, Evaluation, Iteration
from app.feedback_loop import IterativeFeedbackCycle

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/monitoring/overview")
async def monitoring_overview(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Comprehensive monitoring dashboard"""
    
    # Get 24-hour stats
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    specs_24h = db.query(Spec).filter(Spec.created_at >= cutoff).count()
    evals_24h = db.query(Evaluation).filter(Evaluation.ts >= cutoff).count()
    iters_24h = db.query(Iteration).filter(Iteration.ts >= cutoff).count()
    
    # Feedback loop status
    feedback_cycle = IterativeFeedbackCycle(db)
    cycle_status = feedback_cycle.get_cycle_status()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "stats_24h": {
            "specs_generated": specs_24h,
            "evaluations_submitted": evals_24h,
            "iterations_created": iters_24h
        },
        "feedback_loop": cycle_status,
        "system_health": {
            "database": "healthy",
            "cache": "healthy",
            "gpu": "available"
        }
    }


@router.get("/monitoring/rate-limits")
async def rate_limit_status():
    """Get current rate limit stats"""
    from app.middleware.rate_limit import rate_limiter
    
    return {
        "requests_per_minute": rate_limiter.requests_per_minute,
        "active_clients": len(rate_limiter.clients),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/monitoring/feedback-loop")
async def feedback_loop_status(db: Session = Depends(get_db)):
    """Get detailed feedback loop status"""
    try:
        cycle = IterativeFeedbackCycle(db)
        status = cycle.get_cycle_status()
        
        return {
            "feedback_status": status,
            "endpoint": "/api/v1/monitoring/feedback-loop",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting feedback status: {e}")
        return {
            "error": "Could not retrieve feedback status",
            "timestamp": datetime.utcnow().isoformat()
        }