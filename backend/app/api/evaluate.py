from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import EvaluateRequest, EvaluateResponse
from app.database import get_current_user, get_db
from app.models import Evaluation, Spec
from app.utils import create_new_eval_id

router = APIRouter()

@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(
    request: EvaluateRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if spec exists
    spec = db.query(Spec).filter(Spec.spec_id == request.spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")
    
    # Save evaluation to DB
    eval_id = create_new_eval_id()
    evaluation = Evaluation(
        eval_id=eval_id,
        spec_id=request.spec_id,
        user_id=request.user_id,
        score=request.rating,
        notes=request.notes
    )
    db.add(evaluation)
    db.commit()
    
    return EvaluateResponse(
        ok=True,
        saved_id=eval_id
    )