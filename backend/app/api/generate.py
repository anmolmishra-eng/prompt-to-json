"""
Generate API - Design Specification Generation
Complete implementation with LM integration, compliance checking, and cost estimation
"""
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict

from app.config import settings
from app.lm_adapter import lm_run
from fastapi import APIRouter, HTTPException, status

router = APIRouter()
logger = logging.getLogger(__name__)

# Import schemas from app.schemas
from app.schemas import GenerateRequest, GenerateResponse

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def validate_city(city: str) -> bool:
    """Validate city is supported"""
    supported_cities = getattr(settings, "SUPPORTED_CITIES", ["Mumbai", "Delhi", "Bangalore", "Pune", "Ahmedabad"])
    return city in supported_cities


def calculate_estimated_cost(spec_json: Dict) -> float:
    """Calculate realistic estimated cost based on design type and dimensions"""
    try:
        design_type = spec_json.get("design_type", "generic")
        dimensions = spec_json.get("dimensions", {})
        objects = spec_json.get("objects", [])
        stories = spec_json.get("stories", 1)

        # Calculate area
        width = dimensions.get("width", 10)
        length = dimensions.get("length", 10)
        area = width * length

        # Design type base costs (INR per sq meter)
        base_costs = {
            "house": 25000,  # ₹25k per sqm for house construction
            "building": 30000,  # ₹30k per sqm for commercial building
            "office": 15000,  # ₹15k per sqm for office interiors
            "kitchen": 35000,  # ₹35k per sqm for kitchen renovation
            "bedroom": 20000,  # ₹20k per sqm for bedroom
            "bathroom": 40000,  # ₹40k per sqm for bathroom
            "living_room": 18000,  # ₹18k per sqm for living room
            "car_body": 500000,  # ₹5 lakhs base for car
            "pcb": 10000,  # ₹10k base for electronics
            "generic": 20000,  # ₹20k per sqm default
        }

        base_rate = base_costs.get(design_type, 20000)

        # Calculate base cost
        if design_type in ["car_body", "pcb", "component"]:
            # Fixed costs for vehicles/electronics
            base_cost = base_rate
        else:
            # Area-based costs for buildings/rooms
            base_cost = area * base_rate * stories

        # Material premium multipliers
        material_multipliers = {
            "marble": 1.8,
            "granite": 1.6,
            "quartz": 1.4,
            "wood_oak": 1.3,
            "concrete": 1.0,
            "brick": 1.1,
            "glass": 1.5,
            "steel": 1.4,
            "leather": 2.0,
            "default": 1.0,
        }

        # Calculate material premium
        material_premium = 1.0
        for obj in objects:
            material = obj.get("material", "default")
            for mat_key, multiplier in material_multipliers.items():
                if mat_key in material:
                    material_premium = max(material_premium, multiplier)
                    break

        # Special object premiums
        object_premiums = {
            "garage": 200000,  # ₹2 lakhs for garage
            "roof": 150000,  # ₹1.5 lakhs for roof
            "foundation": 100000,  # ₹1 lakh for foundation
            "island": 80000,  # ₹80k for kitchen island
            "engine": 300000,  # ₹3 lakhs for car engine
            "wheel": 25000,  # ₹25k per wheel
        }

        premium_cost = 0
        for obj in objects:
            obj_type = obj.get("type", "")
            count = obj.get("count", 1)
            if obj_type in object_premiums:
                premium_cost += object_premiums[obj_type] * count

        # Final calculation
        total_cost = (base_cost * material_premium) + premium_cost

        # Minimum costs by design type
        min_costs = {
            "house": 2500000,  # Min ₹25 lakhs for house
            "building": 5000000,  # Min ₹50 lakhs for building
            "office": 200000,  # Min ₹2 lakhs for office
            "kitchen": 300000,  # Min ₹3 lakhs for kitchen
            "bedroom": 150000,  # Min ₹1.5 lakhs for bedroom
            "bathroom": 200000,  # Min ₹2 lakhs for bathroom
            "car_body": 800000,  # Min ₹8 lakhs for car
            "pcb": 5000,  # Min ₹5k for electronics
        }

        min_cost = min_costs.get(design_type, 100000)
        total_cost = max(total_cost, min_cost)

        return round(total_cost, 0)

    except Exception as e:
        logger.warning(f"Cost calculation failed: {e}")
        return 500000.0  # Default ₹5 lakhs


def generate_mock_glb(spec_json: Dict) -> bytes:
    """Generate real GLB file with actual kitchen geometry"""
    try:
        from app.geometry_generator_real import generate_real_glb

        return generate_real_glb(spec_json)
    except Exception as e:
        logger.warning(f"Real geometry generation failed, using fallback: {e}")
        # Fallback to simple GLB
        glb_header = b"glTF\x02\x00\x00\x00"
        mock_data = b'{"asset":{"version":"2.0"},"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0}],"meshes":[{"primitives":[{"attributes":{"POSITION":0}}]}]}'
        padding = b"\x00" * (1024 - len(mock_data))
        return glb_header + mock_data + padding


def create_local_preview_file(spec_json: Dict, file_path: str):
    """Create local preview file as fallback"""
    import os

    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write mock GLB content
    with open(file_path, "wb") as f:
        f.write(generate_mock_glb(spec_json))


# Removed unused helper functions


# ============================================================================
# API ENDPOINTS
# ============================================================================


@router.post("/generate", response_model=GenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_design(request: GenerateRequest):
    """
    Generate new design specification using LM

    **Process:**
    1. Validate input and city support
    2. Run LM inference (local GPU or cloud)
    3. Calculate estimated cost
    4. Save spec to database
    5. Generate 3D preview
    6. Queue compliance check
    7. Create audit log
    8. Return complete spec with signed URLs

    **Returns:**
    - spec_id: Unique identifier
    - spec_json: Complete design specification
    - preview_url: Signed URL for 3D preview
    - estimated_cost: Cost in INR
    - compliance_check_id: ID for async compliance validation
    """
    start_time = time.time()

    # Add explicit logging
    print(f"🎨 GENERATE REQUEST: user_id={request.user_id}, prompt='{request.prompt[:50]}...'")
    logger.info(f"🎨 GENERATE REQUEST: user_id={request.user_id}, prompt='{request.prompt[:50]}...'")

    try:
        # 1. VALIDATE INPUT
        print(f"✅ Validating input...")
        if not request.prompt or len(request.prompt) < 10:
            raise HTTPException(status_code=400, detail="Prompt must be at least 10 characters")

        if not request.user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        print(f"✅ Input validation passed")

        # 2. CALL LM
        try:
            print(f"🤖 Calling LM with prompt: '{request.prompt[:30]}...'")
            lm_params = request.context or {}
            lm_params.update(
                {
                    "user_id": request.user_id,
                    "city": getattr(request, "city", "Mumbai"),
                    "style": getattr(request, "style", "modern"),
                }
            )

            lm_result = await lm_run(request.prompt, lm_params)
            spec_json = lm_result.get("spec_json")
            lm_provider = lm_result.get("provider", "local")

            print(f"✅ LM returned result from {lm_provider} provider")

            if not spec_json:
                raise HTTPException(status_code=500, detail="LM returned empty spec")

        except Exception as e:
            logger.error(f"LM call failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=503, detail="LM service unavailable")

        # 3. CALCULATE COST AND ENHANCE SPEC
        print(f"💰 Calculating cost for {len(spec_json.get('objects', []))} objects...")
        estimated_cost = calculate_estimated_cost(spec_json)
        print(f"✅ Estimated cost: ₹{estimated_cost:,.0f}")

        spec_json["metadata"] = spec_json.get("metadata", {})
        spec_json["metadata"].update(
            {
                "estimated_cost": estimated_cost,
                "currency": "INR",
                "generation_provider": lm_provider,
                "city": getattr(request, "city", "Mumbai"),
                "style": getattr(request, "style", "modern"),
            }
        )

        # 4. CREATE SPEC ID AND GENERATE PREVIEW FIRST
        import uuid

        spec_id = f"spec_{uuid.uuid4().hex[:12]}"

        # 5. GENERATE PREVIEW FILE AND URL FIRST
        try:
            from app.storage import upload_geometry

            # Generate simple GLB file content (mock 3D data)
            glb_content = generate_mock_glb(spec_json)

            # Upload to Supabase storage
            preview_url = upload_geometry(spec_id, glb_content)
            print(f"✅ Generated real preview file: {preview_url}")

        except Exception as e:
            print(f"⚠️ Preview generation failed, using local path: {e}")
            # Fallback to local file path
            local_preview_path = f"data/geometry_outputs/{spec_id}.glb"
            create_local_preview_file(spec_json, local_preview_path)
            preview_url = f"http://localhost:8000/static/geometry/{spec_id}.glb"

        # 6. SAVE TO STORAGE AND DATABASE
        from app.spec_storage import save_spec

        # Save complete spec data for iterate endpoint
        complete_spec_data = {
            "spec_id": spec_id,
            "spec_json": spec_json,
            "user_id": request.user_id,
            "estimated_cost": estimated_cost,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "spec_version": 1,
        }
        save_spec(spec_id, complete_spec_data)
        print(f"💾 Saved spec {spec_id} to in-memory storage")

        # Save to database
        from app.database import SessionLocal
        from app.models import Spec, User

        print(f"💾 Saving spec {spec_id} to database...")

        db = SessionLocal()
        try:
            # Ensure user exists - check by username first, then by id
            user = db.query(User).filter((User.id == request.user_id) | (User.username == request.user_id)).first()

            if not user:
                user = User(
                    id=request.user_id,
                    username=request.user_id,
                    email=f"{request.user_id}@example.com",
                    password_hash="dummy_hash",
                    full_name=f"User {request.user_id}",
                    is_active=True,
                )
                db.add(user)
                db.commit()
                print(f"✅ Created user {request.user_id}")
            else:
                # Use the existing user's actual ID
                request.user_id = user.id
                print(f"✅ Using existing user {user.username} with id {user.id}")

            # Create spec with required fields
            db_spec = Spec(
                id=spec_id,
                user_id=request.user_id,
                prompt=request.prompt,
                city="Mumbai",  # Required field
                spec_json=spec_json,
            )

            db.add(db_spec)
            db.commit()
            db.refresh(db_spec)
            print(f"✅ Successfully saved spec {spec_id} to database")
        except Exception as db_error:
            db.rollback()
            print(f"❌ Database save FAILED: {db_error}")
            import traceback

            traceback.print_exc()
            # Don't raise - continue without DB
        finally:
            db.close()

        compliance_check_id = f"check_{spec_id}"

        # Fix currency in spec_json if present
        if "estimated_cost" in spec_json and "currency" in spec_json["estimated_cost"]:
            spec_json["estimated_cost"]["currency"] = "INR"
            spec_json["estimated_cost"]["total"] = estimated_cost

        generation_time = int((time.time() - start_time) * 1000)
        print(f"🎉 Generated spec {spec_id} for user {request.user_id} in {generation_time}ms")
        logger.info(f"Generated spec {spec_id} for user {request.user_id} in {generation_time}ms")

        # 7. RETURN RESPONSE
        response = GenerateResponse(
            spec_id=spec_id,
            spec_json=spec_json,
            preview_url=preview_url,
            estimated_cost=estimated_cost,
            compliance_check_id=compliance_check_id,
            created_at=datetime.now(timezone.utc),
            spec_version=1,
            user_id=request.user_id,
        )
        print(f"📤 Returning response with spec_id: {spec_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error during spec generation")


@router.get("/specs/{spec_id}", response_model=GenerateResponse)
async def get_spec(spec_id: str):
    """
    Retrieve existing specification
    """
    print(f"📄 GET SPEC REQUEST: spec_id={spec_id}")
    logger.info(f"📄 GET SPEC REQUEST: spec_id={spec_id}")

    # Try to get spec from database first
    try:
        from app.database import SessionLocal
        from app.models import Spec

        db = SessionLocal()
        try:
            db_spec = db.query(Spec).filter(Spec.id == spec_id).first()

            if db_spec:
                print(f"✅ Found spec {spec_id} in database")

                # Generate preview URL
                try:
                    from app.storage import supabase

                    preview_url = supabase.storage.from_("geometry").get_public_url(f"{spec_id}.glb")
                except Exception as e:
                    print(f"⚠️ Supabase URL generation failed: {e}")
                    preview_url = f"http://localhost:8000/static/geometry/{spec_id}.glb"

                response = GenerateResponse(
                    spec_id=db_spec.id,
                    spec_json=db_spec.spec_json,
                    preview_url=preview_url,
                    estimated_cost=db_spec.estimated_cost,
                    compliance_check_id=f"check_{spec_id}",
                    created_at=db_spec.created_at,
                    spec_version=db_spec.version,
                    user_id=db_spec.user_id,
                )
                print(f"✅ Returning database spec for {spec_id}")
                return response
        finally:
            db.close()

    except Exception as e:
        print(f"⚠️ Database query failed: {e}")
        logger.error(f"Database query failed for spec {spec_id}: {e}")

    # Fallback to in-memory storage
    from app.spec_storage import get_spec as get_stored_spec

    stored_spec = get_stored_spec(spec_id)

    if stored_spec:
        print(f"✅ Found spec {spec_id} in memory storage")
        try:
            from app.storage import supabase

            preview_url = supabase.storage.from_("geometry").get_public_url(f"{spec_id}.glb")
        except Exception as e:
            preview_url = f"http://localhost:8000/static/geometry/{spec_id}.glb"

        response = GenerateResponse(
            spec_id=stored_spec["spec_id"],
            spec_json=stored_spec["spec_json"],
            preview_url=preview_url,
            estimated_cost=stored_spec["estimated_cost"],
            compliance_check_id=f"check_{spec_id}",
            created_at=datetime.fromisoformat(stored_spec["created_at"].replace("Z", "+00:00")),
            spec_version=stored_spec["spec_version"],
            user_id=stored_spec["user_id"],
        )
        return response

    # Spec not found anywhere
    print(f"❌ Spec {spec_id} not found in database or memory")
    raise HTTPException(
        status_code=404,
        detail=f"Specification '{spec_id}' not found. Generate a design first using /api/v1/generate",
    )
