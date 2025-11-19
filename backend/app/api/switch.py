"""
Switch endpoint with proper error handling and validation
"""

import asyncio
import copy
import logging
import uuid
from datetime import datetime
from typing import Optional

from app.database import get_current_user, get_db
from app.models import Iteration, Spec
from app.schemas import SwitchRequest, SwitchResponse, SwitchChanged
from app.storage import get_signed_url, upload_to_bucket
from app.utils import create_iter_id, generate_glb_from_spec
from app.error_handler import APIException
from app.schemas.error_schemas import ErrorCode
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/switch", response_model=SwitchResponse)
async def switch(
    request: SwitchRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Switch/update design spec properties with validation"""
    
    try:
        # 1. VALIDATE INPUT
        if not request.spec_id:
            raise APIException(
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
                message="spec_id is required",
                field_errors=[{"field": "spec_id"}]
            )
        
        if not request.target:
            raise APIException(
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
                message="target is required",
                field_errors=[{"field": "target"}]
            )
        
        if not request.target.object_id and not request.target.object_query:
            raise APIException(
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
                message="target must have object_id or object_query",
                field_errors=[{"field": "target.object_id or object_query"}]
            )
        
        if not request.update:
            raise APIException(
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
                message="update is required",
                field_errors=[{"field": "update"}]
            )
        
        # At least one property to update
        has_update = (
            hasattr(request.update, "material") and request.update.material or
            hasattr(request.update, "color_hex") and request.update.color_hex or
            hasattr(request.update, "texture_override") and request.update.texture_override
        )
        
        if not has_update:
            raise APIException(
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
                message="At least one property must be updated (material, color_hex, or texture_override)"
            )
        
        # 2. LOAD SPEC
        try:
            spec = db.query(Spec).filter(Spec.spec_id == request.spec_id).first()
            
            if not spec:
                raise APIException(
                    status_code=404,
                    error_code=ErrorCode.NOT_FOUND,
                    message=f"Spec '{request.spec_id}' not found",
                    details={"spec_id": request.spec_id}
                )
        
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Database error loading spec: {str(e)}", exc_info=True)
            raise APIException(
                status_code=500,
                error_code=ErrorCode.DATABASE_ERROR,
                message="Failed to load spec"
            )
        
        # 3. CHECK VERSION CONFLICT (Optional optimistic locking)
        if hasattr(request, "expected_version") and request.expected_version:
            if spec.spec_version != request.expected_version:
                raise APIException(
                    status_code=409,
                    error_code=ErrorCode.CONFLICT,
                    message="Spec was modified by another user",
                    details={
                        "current_version": spec.spec_version,
                        "expected_version": request.expected_version,
                        "conflict_type": "version_mismatch"
                    }
                )
        
        # 4. FIND TARGET OBJECT
        before_spec = copy.deepcopy(spec.spec_json)
        target_object_id = request.target.object_id
        objects = spec.spec_json.get("objects", [])
        
        if not objects:
            raise APIException(
                status_code=400,
                error_code=ErrorCode.INVALID_INPUT,
                message="Spec has no objects to update"
            )
        
        target_found = False
        target_obj = None
        
        for obj in objects:
            if obj.get("id") == target_object_id:
                target_found = True
                target_obj = obj
                break
        
        if not target_found:
            raise APIException(
                status_code=400,
                error_code=ErrorCode.NOT_FOUND,
                message=f"Target object '{target_object_id}' not found in spec",
                details={
                    "target_object_id": target_object_id,
                    "available_objects": [obj.get("id") for obj in objects]
                }
            )
        
        # 5. APPLY UPDATES
        changes = []
        
        try:
            if request.update.material:
                before_val = target_obj.get("material", "unknown")
                target_obj["material"] = request.update.material
                changes.append({
                    "field": "material",
                    "before": before_val,
                    "after": request.update.material
                })
                logger.debug(f"Updated material: {before_val} → {request.update.material}")
            
            if request.update.color_hex:
                # Validate hex color format
                if not isinstance(request.update.color_hex, str) or not request.update.color_hex.startswith("#"):
                    raise APIException(
                        status_code=400,
                        error_code=ErrorCode.VALIDATION_ERROR,
                        message="Invalid color format, must be hex (e.g., #FF8C00)"
                    )
                before_val = target_obj.get("color_hex", "unknown")
                target_obj["color_hex"] = request.update.color_hex
                changes.append({
                    "field": "color_hex",
                    "before": before_val,
                    "after": request.update.color_hex
                })
            
            if request.update.texture_override:
                before_val = target_obj.get("texture_override", "unknown")
                target_obj["texture_override"] = request.update.texture_override
                changes.append({
                    "field": "texture_override",
                    "before": before_val,
                    "after": request.update.texture_override
                })
        
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Error applying updates: {str(e)}", exc_info=True)
            raise APIException(
                status_code=400,
                error_code=ErrorCode.INVALID_INPUT,
                message="Failed to apply updates"
            )
        
        # 6. SAVE TO DATABASE
        try:
            spec.spec_version += 1
            spec.updated_at = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error saving updates: {str(e)}", exc_info=True)
            raise APIException(
                status_code=500,
                error_code=ErrorCode.DATABASE_ERROR,
                message="Failed to save changes"
            )
        
        # 7. SAVE ITERATION
        try:
            iter_id = create_iter_id()
            change_descriptions = [
                f"{c['field']} changed from {c['before']} to {c['after']}"
                for c in changes
            ]
            feedback = request.note or f"Updated {target_object_id}: {', '.join(change_descriptions)}"
            
            iteration = Iteration(
                iter_id=iter_id,
                spec_id=request.spec_id,
                before_spec=before_spec,
                after_spec=spec.spec_json,
                feedback=feedback
            )
            
            db.add(iteration)
            db.commit()
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving iteration: {str(e)}", exc_info=True)
            # Don't fail entire request, just warn
        
        # 8. GENERATE PREVIEW
        preview_url = None
        try:
            spec_complexity = len(spec.spec_json.get("objects", []))
            
            if spec_complexity > 10:
                logger.info("Complex spec, would use async preview (simplified for demo)")
            
            preview_bytes = generate_glb_from_spec(spec.spec_json)
            preview_path = f"{request.spec_id}_v{spec.spec_version}.glb"
            
            await upload_to_bucket("previews", preview_path, preview_bytes)
            preview_url = await get_signed_url("previews", preview_path, expires=600)
        
        except Exception as e:
            logger.warning(f"Preview generation failed: {str(e)}")
            # Allow switch to succeed even if preview fails
        
        # 9. RETURN RESPONSE
        primary_change = changes[0] if changes else {"field": "unknown", "before": "unknown", "after": "unknown"}
        
        return SwitchResponse(
            spec_id=request.spec_id,
            iteration_id=iter_id,
            updated_spec_json=spec.spec_json,
            preview_url=preview_url or "",
            changed=SwitchChanged(
                object_id=target_object_id,
                field=primary_change["field"],
                before=primary_change["before"],
                after=primary_change["after"]
            ),
            saved_at=spec.updated_at,
            spec_version=spec.spec_version
        )
    
    except APIException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in switch: {str(e)}", exc_info=True)
        raise APIException(
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Unexpected error during switch operation"
        )