import asyncio
import copy
import uuid
from datetime import datetime

from app.database import get_current_user, get_db
from app.models import Iteration, Spec
from app.schemas import MessageResponse, ProviderSwitchRequest, SwitchChanged, SwitchRequest, SwitchResponse
from app.storage import get_signed_url, upload_to_bucket
from app.utils import create_iter_id, generate_glb_from_spec
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/switch", response_model=SwitchResponse)
async def switch(
    request: SwitchRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Load existing spec from DB
    spec = db.query(Spec).filter(Spec.spec_id == request.spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")

    # 2. Check for version conflicts (if client provides expected version)
    if hasattr(request, "expected_version") and request.expected_version:
        if spec.spec_version != request.expected_version:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Version conflict",
                    "current_version": spec.spec_version,
                    "expected_version": request.expected_version,
                    "message": "Spec was modified by another user. Please refresh and try again.",
                },
            )

    before_spec = copy.deepcopy(spec.spec_json)

    # 2. Determine target object ID
    target_object_id = None
    if request.target.object_id:
        target_object_id = request.target.object_id
    elif request.target.object_query:
        # TODO: Implement object query resolution
        raise HTTPException(status_code=400, detail="object_query not yet implemented")
    else:
        raise HTTPException(status_code=400, detail="Either object_id or object_query required")

    # 3. Find target object and apply updates
    objects = spec.spec_json.get("objects", [])
    target_found = False
    changes = []

    for obj in objects:
        if obj.get("id") == target_object_id:
            target_found = True

            # Apply material update
            if request.update.material:
                before_val = obj.get("material", "unknown")
                obj["material"] = request.update.material
                changes.append(
                    {
                        "field": "material",
                        "before": before_val,
                        "after": request.update.material,
                    }
                )

            # Apply color update
            if request.update.color_hex:
                before_val = obj.get("color_hex", "unknown")
                obj["color_hex"] = request.update.color_hex
                changes.append(
                    {
                        "field": "color_hex",
                        "before": before_val,
                        "after": request.update.color_hex,
                    }
                )

            # Apply texture update
            if request.update.texture_override:
                before_val = obj.get("texture_override", "unknown")
                obj["texture_override"] = request.update.texture_override
                changes.append(
                    {
                        "field": "texture_override",
                        "before": before_val,
                        "after": request.update.texture_override,
                    }
                )

            break

    if not target_found:
        raise HTTPException(status_code=400, detail=f"Target object {target_object_id} not found")

    if not changes:
        raise HTTPException(status_code=400, detail="No valid updates provided")

    # 4. Increment spec version and update DB
    spec.spec_version += 1
    spec.updated_at = datetime.utcnow()
    db.commit()

    # 5. Save iteration diff
    iter_id = create_iter_id()
    change_descriptions = [f"{c['field']} changed from {c['before']} to {c['after']}" for c in changes]
    feedback = request.note or f"Updated {target_object_id}: {', '.join(change_descriptions)}"

    iteration = Iteration(
        iter_id=iter_id,
        spec_id=request.spec_id,
        before_spec=before_spec,
        after_spec=spec.spec_json,
        feedback=feedback,
    )
    db.add(iteration)
    db.commit()

    # 6. Check if preview generation should be async (complex specs)
    spec_complexity = len(spec.spec_json.get("objects", []))

    if spec_complexity > 10:  # Async for complex specs
        status_id = str(uuid.uuid4())
        preview_status[status_id] = {"status": "processing"}

        # Start async preview generation
        asyncio.create_task(generate_preview_async(status_id, request.spec_id, spec.spec_version, spec.spec_json))

        return {
            "status_url": f"/api/v1/switch/status/{status_id}",
            "spec_id": request.spec_id,
            "iteration_id": iter_id,
            "message": "Preview generation started. Poll status_url for completion.",
        }
    else:
        # Synchronous preview generation
        preview_bytes = generate_glb_from_spec(spec.spec_json)
        preview_path = f"{request.spec_id}_v{spec.spec_version}.glb"
        await upload_to_bucket("previews", preview_path, preview_bytes)
        preview_url = await get_signed_url("previews", preview_path, expires=600)

    # 7. Return response
    primary_change = changes[0]  # Use first change for response
    return SwitchResponse(
        spec_id=request.spec_id,
        iteration_id=iter_id,
        updated_spec_json=spec.spec_json,
        preview_url=preview_url,
        changed=SwitchChanged(
            object_id=target_object_id,
            field=primary_change["field"],
            before=primary_change["before"],
            after=primary_change["after"],
        ),
        saved_at=spec.updated_at,
    )


# In-memory store for async preview status (use Redis in production)
preview_status = {}


async def generate_preview_async(status_id: str, spec_id: str, spec_version: int, spec_json: dict):
    """Background task for async preview generation"""
    try:
        # Simulate processing time for complex specs
        await asyncio.sleep(2)

        # Generate preview
        preview_bytes = generate_glb_from_spec(spec_json)
        preview_path = f"{spec_id}_v{spec_version}.glb"
        await upload_to_bucket("previews", preview_path, preview_bytes)
        preview_url = await get_signed_url("previews", preview_path, expires=600)

        # Update status with result
        preview_status[status_id] = {
            "status": "completed",
            "result": {
                "spec_id": spec_id,
                "preview_url": preview_url,
                "message": "Preview generation completed",
            },
        }
    except Exception as e:
        preview_status[status_id] = {"status": "failed", "error": str(e)}


@router.get("/status/{status_id}")
async def get_preview_status(status_id: str, current_user: str = Depends(get_current_user)):
    """Poll endpoint for async preview generation status"""
    if status_id not in preview_status:
        raise HTTPException(status_code=404, detail="Status ID not found")

    status = preview_status[status_id]

    if status["status"] == "completed":
        # Clean up and return result
        result = status["result"]
        del preview_status[status_id]
        return result
    elif status["status"] == "failed":
        error = status["error"]
        del preview_status[status_id]
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {error}")
    else:
        # Still processing
        return {"status": "processing", "message": "Preview generation in progress"}


@router.post("/provider", response_model=MessageResponse)
async def switch_provider(request: ProviderSwitchRequest, current_user: str = Depends(get_current_user)):
    if request.provider not in ["local", "yotta"]:
        raise HTTPException(status_code=400, detail="Invalid provider. Use 'local' or 'yotta'")

    return MessageResponse(message=f"Switched to {request.provider} provider for user {current_user}")
