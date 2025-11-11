from app.api.evaluate import evaluate
from app.api.generate import generate
from app.api.iterate import iterate
from app.database import get_current_user, get_db
from app.schemas import CoreRunRequest, EvaluateRequest, GenerateRequest, IterateRequest
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/run")
async def core_run(
    request: CoreRunRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    outputs = {}

    for step in request.pipeline:
        if step == "generate":
            generate_req = GenerateRequest(**request.input)
            res = await generate(generate_req, current_user, db)
            outputs["generate"] = res.dict()
        elif step == "evaluate":
            evaluate_req = EvaluateRequest(**request.input)
            res = await evaluate(evaluate_req, current_user, db)
            outputs["evaluate"] = res.dict()
        elif step == "iterate":
            iterate_req = IterateRequest(**request.input)
            res = await iterate(iterate_req, current_user, db)
            outputs["iterate"] = res.dict()
        elif step == "store":
            # Store or finalize step (placeholder)
            outputs["store"] = {"ok": True}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown step: {step}")

    return outputs  # aggregated outputs


@router.get("/status")
async def core_status(current_user: str = Depends(get_current_user)):
    return {"message": "Core services operational", "user": current_user}
