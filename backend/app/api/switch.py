"""
Switch API - Material/Property Switching
Complete implementation with enhanced NLP
"""
import logging
import time
from typing import Dict, List, Optional

from app.config import settings
from app.database import get_db
from app.models import AuditLog, Iteration, Spec, User
from app.nlp.material_parser import MaterialSwitchParser
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1", tags=["Switch"])
logger = logging.getLogger(__name__)

# Initialize NLP parser
parser = MaterialSwitchParser()

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class SwitchRequest(BaseModel):
    """Material switch request"""

    spec_id: str = Field(..., description="Target specification ID")
    query: str = Field(..., min_length=5, max_length=500, description="Natural language change request")

    class Config:
        json_schema_extra = {"example": {"spec_id": "spec_abc123", "query": "change floor to marble"}}


class ObjectChange(BaseModel):
    """Individual object change"""

    object_id: str
    field: str
    old_value: str
    new_value: str


class SwitchResponse(BaseModel):
    """Material switch response"""

    iteration_id: str
    spec_id: str
    changes: List[ObjectChange]
    changed_objects: List[str]
    preview_url: str
    cost_impact: Dict
    nlp_confidence: float


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def apply_changes_to_spec(spec_json: Dict, command) -> tuple:
    """
    Apply parsed NLP command to spec

    Returns:
        (updated_spec, changes_list)
    """
    updated_spec = spec_json.copy()
    changes = []
    changed_objects = []

    objects = updated_spec.get("objects", [])

    for obj in objects:
        should_change = False

        # Match target
        if command.target_id and obj.get("id") == command.target_id:
            should_change = True
        elif command.target_type and obj.get("type") == command.target_type:
            should_change = True

        if should_change:
            old_value = obj.get(command.property)

            # Apply change
            obj[command.property] = command.value

            # Record change
            changes.append(
                ObjectChange(
                    object_id=obj["id"], field=command.property, old_value=str(old_value), new_value=str(command.value)
                )
            )

            changed_objects.append(obj["id"])

    updated_spec["objects"] = objects

    return updated_spec, changes, changed_objects


def recalculate_cost(old_spec: Dict, new_spec: Dict) -> Dict:
    """Calculate cost difference"""
    old_cost = old_spec.get("metadata", {}).get("estimated_cost", 0)

    # Simple recalculation
    new_cost = old_cost * 1.1  # 10% increase for material change
    cost_delta = new_cost - old_cost

    return {
        "delta": round(cost_delta, 2),
        "new_total": round(new_cost, 2),
        "percentage_change": round((cost_delta / old_cost * 100) if old_cost > 0 else 0, 2),
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================


@router.post("/switch", response_model=SwitchResponse, status_code=status.HTTP_201_CREATED)
async def switch_material(request: SwitchRequest, db: Session = Depends(get_db)):
    """
    Switch material/property using natural language

    **Supported Commands:**
    - "change floor to marble"
    - "make all cushions orange"
    - "replace kitchen counter with granite"
    - "update wall color to #FFE4B5"

    **Process:**
    1. Parse natural language query
    2. Apply changes to spec
    3. Recalculate cost
    4. Generate new preview
    5. Save as iteration

    **Returns:**
    - iteration_id: New iteration ID
    - changes: List of changes made
    - cost_impact: Cost difference
    """
    start_time = time.time()

    # Fetch spec
    spec = db.query(Spec).filter(Spec.id == request.spec_id).first()
    if not spec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specification not found")

    try:
        # Parse NLP query
        logger.info(f"Parsing query: {request.query}")
        commands = parser.parse(request.query)

        if not commands:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not understand the request. Please try rephrasing.",
            )

        command = commands  # Use first command

        if command.confidence < 0.3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Low confidence in understanding request ({command.confidence:.2f}). Please be more specific.",
            )

        logger.info(f"Parsed command: {command}")

        # Apply changes
        updated_spec, changes, changed_objects = apply_changes_to_spec(spec.spec_json, command)

        if not changes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No matching objects found to modify")

        # Recalculate cost
        cost_impact = recalculate_cost(spec.spec_json, updated_spec)

        # Create iteration
        iteration = Iteration(
            spec_id=spec.id,
            user_id=spec.user_id,
            query=request.query,
            nlp_confidence=command.confidence,
            diff={"command": command.__dict__, "changes": [c.dict() for c in changes]},
            spec_json=updated_spec,
            changed_objects=changed_objects,
            cost_delta=cost_impact["delta"],
            new_total_cost=cost_impact["new_total"],
            processing_time_ms=int((time.time() - start_time) * 1000),
        )

        db.add(iteration)
        db.commit()
        db.refresh(iteration)

        logger.info(f"✓ Iteration created: {iteration.id}")

        # Generate preview (placeholder)
        preview_url = f"https://previews.bhiv.ai/{iteration.id}.png"
        iteration.preview_url = preview_url
        db.commit()

        # Audit log
        audit = AuditLog(
            user_id=spec.user_id,
            action="switch_material",
            resource_type="iteration",
            resource_id=iteration.id,
            details={
                "spec_id": spec.id,
                "query": request.query,
                "changes_count": len(changes),
                "confidence": command.confidence,
            },
            status="success",
        )
        db.add(audit)
        db.commit()

        return SwitchResponse(
            iteration_id=iteration.id,
            spec_id=spec.id,
            changes=changes,
            changed_objects=changed_objects,
            preview_url=preview_url,
            cost_impact=cost_impact,
            nlp_confidence=command.confidence,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Switch failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Material switch failed: {str(e)}"
        )
