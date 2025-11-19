"""
Evaluate endpoint with proper error handling and feedback loop integration
"""

import logging
from datetime import datetime
from app.database import get_current_user, get_db
from app.models import Spec, Evaluation
from app.schemas import EvaluateRequest, EvaluateResponse
from app.utils import create_new_eval_id, log_audit_event
from app.error_handler import APIException
from app.schemas.error_schemas import ErrorCode
from app.feedback_loop import IterativeFeedbackCycle
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(
    request: EvaluateRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Evaluate design spec and integrate with feedback loop"""
    
    try:
        # 1. VALIDATE INPUT
        if not request.spec_id:
            raise APIException(
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
                message="spec_id is required",
                field_errors=[{"field": "spec_id", "message": "Cannot be empty"}]
            )
        
        if not request.user_id:
            raise APIException(
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
                message="user_id is required",
                field_errors=[{"field": "user_id", "message": "Cannot be empty"}]
            )
        
        if request.rating is None:
            raise APIException(
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
                message="rating is required",
                field_errors=[{"field": "rating", "message": "Cannot be null"}]
            )
        
        if not (0 <= request.rating <= 5):
            raise APIException(
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
                message="Rating must be between 0 and 5",
                field_errors=[{
                    "field": "rating",
                    "message": "Must be between 0 and 5",
                    "value": request.rating
                }]
            )
        
        # 2. VERIFY SPEC EXISTS
        spec = db.query(Spec).filter(Spec.spec_id == request.spec_id).first()
        if not spec:
            raise APIException(
                status_code=404,
                error_code=ErrorCode.NOT_FOUND,
                message=f"Spec {request.spec_id} not found",
                details={"spec_id": request.spec_id}
            )
        
        # 3. SAVE EVALUATION
        try:
            eval_id = create_new_eval_id()
            evaluation = Evaluation(
                eval_id=eval_id,
                spec_id=request.spec_id,
                user_id=request.user_id,
                score=request.rating,
                notes=request.notes,
                ts=datetime.utcnow()
            )
            
            db.add(evaluation)
            db.commit()
            db.refresh(evaluation)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error while saving evaluation: {str(e)}", exc_info=True)
            raise APIException(
                status_code=500,
                error_code=ErrorCode.DATABASE_ERROR,
                message="Failed to save evaluation",
                details={"error": str(e)[:100]}
            )
        
        # 4. INTEGRATE WITH FEEDBACK LOOP
        feedback_result = None
        training_triggered = False
        
        try:
            feedback_cycle = IterativeFeedbackCycle(db)
            
            feedback_result = await feedback_cycle.process_evaluation_feedback(
                user_id=request.user_id,
                spec_id=request.spec_id,
                rating=request.rating,
                notes=request.notes or ""
            )
            
            training_triggered = feedback_result.get("training_triggered", False)
            
            if training_triggered:
                logger.info("🔄 RL training triggered from accumulated feedback")
            
        except Exception as e:
            logger.warning(f"Feedback loop integration failed (non-blocking): {str(e)}")
            # Don't fail the evaluation if feedback loop fails
        
        # 5. LOG AUDIT EVENT
        try:
            log_audit_event(
                "spec_evaluated",
                request.user_id,
                {
                    "spec_id": request.spec_id,
                    "eval_id": eval_id,
                    "rating": request.rating,
                    "has_notes": bool(request.notes),
                    "training_triggered": training_triggered
                }
            )
        except Exception as e:
            logger.warning(f"Audit logging failed (non-blocking): {str(e)}")
        
        logger.info(f"Evaluation saved: {eval_id}, Training triggered: {training_triggered}")
        
        # 6. RETURN RESPONSE
        response_data = {
            "ok": True,
            "saved_id": eval_id,
            "message": "Evaluation recorded successfully",
            "timestamp": evaluation.ts.isoformat()
        }
        
        # Include feedback loop status if available
        if feedback_result:
            response_data["training_triggered"] = training_triggered
            response_data["training_data_collected"] = feedback_result.get("training_stats", {}).get("total_feedback", 0)
        
        return EvaluateResponse(**response_data)
    
    except APIException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in evaluate: {str(e)}", exc_info=True)
        raise APIException(
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Unexpected error during evaluation"
        )