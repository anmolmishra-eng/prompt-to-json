import logging

from app.api.evaluate import evaluate
from app.api.generate import generate
from app.api.iterate import iterate

logger = logging.getLogger(__name__)
from typing import Any, Dict, List

from app.database import get_current_user, get_db
from app.schemas import EvaluateRequest, GenerateRequest, IterateRequest
from app.schemas.core import CoreRunRequest as OldCoreRunRequest
from pydantic import BaseModel


# Use the correct schema for pipeline execution
class CoreRunRequest(BaseModel):
    pipeline: List[str]
    input: Dict[str, Any]


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

    try:
        for step in request.pipeline:
            if step == "generate":
                # Ensure required fields are present
                if "user_id" not in request.input or "prompt" not in request.input:
                    raise HTTPException(
                        status_code=400, detail="Generate step requires 'user_id' and 'prompt' in input"
                    )

                generate_req = GenerateRequest(**request.input)
                res = await generate(generate_req, current_user, db)
                outputs["generate"] = res.dict()

                # Store spec_id for subsequent steps
                if "spec_id" not in request.input:
                    request.input["spec_id"] = res.spec_id

            elif step == "evaluate":
                # Ensure required fields are present
                if "spec_id" not in request.input or "user_id" not in request.input:
                    raise HTTPException(
                        status_code=400, detail="Evaluate step requires 'spec_id' and 'user_id' in input"
                    )

                # Set default rating if not provided
                if "rating" not in request.input:
                    request.input["rating"] = 5

                evaluate_req = EvaluateRequest(**request.input)
                res = await evaluate(evaluate_req, current_user, db)
                outputs["evaluate"] = res.dict()

            elif step == "iterate":
                # Ensure required fields are present
                if "spec_id" not in request.input or "user_id" not in request.input:
                    raise HTTPException(
                        status_code=400, detail="Iterate step requires 'spec_id' and 'user_id' in input"
                    )

                # Set default strategy if not provided
                if "strategy" not in request.input:
                    request.input["strategy"] = "auto_optimize"

                iterate_req = IterateRequest(**request.input)
                res = await iterate(iterate_req, current_user, db)
                outputs["iterate"] = res.dict()

            elif step == "store":
                # Store or finalize step (placeholder)
                outputs["store"] = {"ok": True, "message": "Design stored successfully"}

            else:
                raise HTTPException(status_code=400, detail=f"Unknown step: {step}")

        return outputs  # aggregated outputs

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@router.get("/status")
async def core_status(current_user: str = Depends(get_current_user)):
    return {"message": "Core services operational", "user": current_user}
