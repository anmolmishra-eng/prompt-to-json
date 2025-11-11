import logging

from app.database import get_current_user, get_db
from app.lm_adapter import lm_run
from app.models import Spec
from app.schemas import GenerateRequest, GenerateResponse
from app.storage import get_signed_url, upload_to_bucket
from app.utils import create_new_spec_id, generate_glb_from_spec, log_audit_event
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Call LM to generate spec JSON (and preview data)
    lm_params = request.context or {}
    lm_params["user_id"] = request.user_id
    lm_result = await lm_run(request.prompt, params=lm_params)
    spec_json = lm_result["spec_json"]

    # 2. Save spec to DB with new spec_id
    spec_id = create_new_spec_id()
    new_spec = Spec(
        spec_id=spec_id,
        user_id=request.user_id,
        prompt=request.prompt,
        project_id=request.project_id,
        spec_json=spec_json,
    )
    db.add(new_spec)
    db.commit()
    db.refresh(new_spec)

    # 3. Generate preview (e.g., from spec_json) and upload
    preview_bytes = generate_glb_from_spec(spec_json)
    await upload_to_bucket("previews", f"{spec_id}.glb", preview_bytes)
    preview_url = await get_signed_url("previews", f"{spec_id}.glb", expires=600)

    # 4. Log audit event
    log_audit_event(
        "spec_generated",
        request.user_id,
        {
            "spec_id": spec_id,
            "project_id": request.project_id,
            "prompt_length": len(request.prompt),
        },
    )

    logger.info(f"Generated spec {spec_id} for user {request.user_id}")

    # 5. Return response
    return GenerateResponse(
        spec_id=spec_id,
        spec_json=spec_json,
        preview_url=preview_url,
        created_at=new_spec.created_at,
    )
