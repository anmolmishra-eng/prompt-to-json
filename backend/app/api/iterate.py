from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import IterateRequest, IterateResponse
from app.lm_adapter import lm_run
from app.database import get_current_user, get_db
from app.models import Iteration, Spec
from app.utils import create_iter_id, spec_json_to_prompt
import copy

router = APIRouter()

@router.post("/iterate", response_model=IterateResponse)
async def iterate(
    request: IterateRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Load current spec
    spec = db.query(Spec).filter(Spec.spec_id == request.spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")
    
    before_spec = copy.deepcopy(spec.spec_json)
    
    # Call LM to improve spec (strategy influences prompt)
    base_prompt = spec_json_to_prompt(before_spec)
    strategy_prompt = f"{base_prompt}\nStrategy: {request.strategy}"
    
    result = await lm_run(strategy_prompt, {"strategy": request.strategy})
    after_spec = result["spec_json"]
    feedback_text = result.get("feedback", "Improved as per strategy.")
    
    # Save iteration
    iter_id = create_iter_id()
    iteration = Iteration(
        iter_id=iter_id,
        spec_id=request.spec_id,
        before_spec=before_spec,
        after_spec=after_spec,
        feedback=feedback_text
    )
    db.add(iteration)
    
    # Update spec in DB
    spec.spec_version += 1
    spec.spec_json = after_spec
    db.commit()
    
    return IterateResponse(
        before=before_spec,
        after=after_spec,
        feedback=feedback_text
    )