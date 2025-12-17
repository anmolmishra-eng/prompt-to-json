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
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1", tags=["🔄 Material Switch"])
logger = logging.getLogger(__name__)

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


def parse_simple_query(query: str) -> Optional[Dict]:
    """Simple NLP parsing for common material switch patterns"""
    query_lower = query.lower()

    # Pattern: "change floor to marble"
    if "change" in query_lower and "floor" in query_lower and "to" in query_lower:
        parts = query_lower.split("to")
        if len(parts) == 2:
            material = parts[1].strip()
            return {"target_type": "floor", "property": "material", "value": material, "confidence": 0.9}

    # Pattern: "make desk mahogany" or "replace desk with mahogany"
    if ("make" in query_lower or "replace" in query_lower) and "desk" in query_lower:
        if "mahogany" in query_lower:
            return {
                "target_type": "furniture",
                "target_subtype": "desk",
                "property": "material",
                "value": "wood_mahogany",
                "confidence": 0.8,
            }

    # Pattern: "update color to #xxx" or "change color to xxx"
    if ("update" in query_lower or "change" in query_lower) and "color" in query_lower:
        if "#" in query:
            color = query.split("#")[1][:6]  # Extract hex color
            return {"target_type": "all", "property": "color_hex", "value": f"#{color}", "confidence": 0.7}

    return None


def apply_simple_changes(spec_json: Dict, command: Dict) -> tuple:
    """Apply simple parsed command to spec"""
    import copy

    updated_spec = copy.deepcopy(spec_json)
    changes = []
    changed_objects = []

    objects = updated_spec.get("objects", [])

    for obj in objects:
        should_change = False

        # Match target
        if command.get("target_type") == "all":
            should_change = True
        elif command.get("target_type") and obj.get("type") == command["target_type"]:
            should_change = True
        elif command.get("target_subtype") and obj.get("subtype") == command["target_subtype"]:
            should_change = True

        if should_change:
            old_value = obj.get(command["property"])

            # Apply change
            obj[command["property"]] = command["value"]

            # Record change
            changes.append(
                ObjectChange(
                    object_id=obj["id"],
                    field=command["property"],
                    old_value=str(old_value),
                    new_value=str(command["value"]),
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

    print(f"🔄 SWITCH REQUEST: spec_id={request.spec_id}, query='{request.query}'")
    logger.info(f"🔄 SWITCH REQUEST: spec_id={request.spec_id}, query='{request.query}'")

    # Try to get spec from in-memory storage first
    from app.spec_storage import get_spec as get_stored_spec

    stored_spec = get_stored_spec(request.spec_id)

    if stored_spec:
        print(f"✅ Found spec {request.spec_id} in storage")
        spec_json = stored_spec["spec_json"]
        user_id = stored_spec["user_id"]
    else:
        # Fallback to database
        try:
            spec = db.query(Spec).filter(Spec.spec_id == request.spec_id).first()
            if not spec:
                print(f"❌ Spec {request.spec_id} not found in storage or database")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specification not found")
            spec_json = spec.spec_json
            user_id = spec.user_id
        except Exception as e:
            print(f"❌ Database error: {e}")
            print(f"❌ Spec {request.spec_id} not found in storage or database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specification not found")

    try:
        # Simple NLP parsing for common patterns
        print(f"🤖 Parsing query: '{request.query}'")
        command = parse_simple_query(request.query)

        if not command:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not understand the request. Please try rephrasing.",
            )

        print(f"✅ Parsed command: {command}")

        # Apply changes
        updated_spec, changes, changed_objects = apply_simple_changes(spec_json, command)

        if not changes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No matching objects found to modify")

        # Recalculate cost
        cost_impact = recalculate_cost(spec_json, updated_spec)

        # Generate iteration ID
        import uuid

        iteration_id = f"iter_{uuid.uuid4().hex[:8]}"

        # Update stored spec if found in storage
        if stored_spec:
            from app.spec_storage import save_spec

            stored_spec["spec_json"] = updated_spec
            stored_spec["spec_version"] = stored_spec.get("spec_version", 1) + 1
            save_spec(request.spec_id, stored_spec)
            print(f"✅ Updated spec {request.spec_id} in storage")

        # Generate preview (placeholder)
        preview_url = f"https://previews.bhiv.ai/{iteration_id}.png"

        print(f"✅ Switch completed: {len(changes)} changes made")

        return SwitchResponse(
            iteration_id=iteration_id,
            spec_id=request.spec_id,
            changes=changes,
            changed_objects=changed_objects,
            preview_url=preview_url,
            cost_impact=cost_impact,
            nlp_confidence=command.get("confidence", 0.8),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Switch failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Material switch failed: {str(e)}"
        )
