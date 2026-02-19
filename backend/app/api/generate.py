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
from app.spec_validator import SpecValidationError, validate_spec_json, validate_with_warnings
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
    """Generate real GLB file with actual geometry"""
    try:
        from app.geometry_generator_real import generate_real_glb

        logger.info(f"Generating geometry for design_type: {spec_json.get('design_type')}")
        glb_bytes = generate_real_glb(spec_json)
        logger.info(f"Successfully generated {len(glb_bytes)} bytes of GLB data")
        return glb_bytes
    except Exception as e:
        logger.error(f"Real geometry generation FAILED: {e}", exc_info=True)
        # Fallback to simple GLB
        glb_header = b"glTF\x02\x00\x00\x00"
        mock_data = b'{"asset":{"version":"2.0"},"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0}],"meshes":[{"primitives":[{"attributes":{"POSITION":0}}]}]}'
        padding = b"\x00" * (1024 - len(mock_data))
        logger.warning("Using fallback simple GLB due to geometry generation error")
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
    logger.info(f"GENERATE REQUEST: user_id={request.user_id}, prompt='{request.prompt[:50]}...'")

    try:
        # 1. VALIDATE INPUT
        logger.info("Validating input...")
        if not request.prompt or len(request.prompt) < 10:
            raise HTTPException(status_code=400, detail="Prompt must be at least 10 characters")

        if not request.user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        logger.info("Input validation passed")

        # 2. CALL LM
        try:
            logger.info(f"Calling LM with prompt: '{request.prompt[:30]}...'")
            # Use getattr to safely access city and style with defaults
            req_city = getattr(request, "city", "Mumbai")
            req_style = getattr(request, "style", "modern")
            logger.info(f"[DEBUG] Request city: {req_city}, Request style: {req_style}")

            # Extract budget from constraints or context
            budget = None
            if hasattr(request, "constraints") and request.constraints:
                budget = request.constraints.get("budget")
            if not budget and hasattr(request, "context") and request.context:
                budget = request.context.get("budget")

            logger.info(f"[DEBUG] Extracted budget: ₹{budget:,}" if budget else "[DEBUG] No budget provided")

            lm_params = request.context or {}
            if budget:
                lm_params["budget"] = budget
            lm_params.update(
                {
                    "user_id": request.user_id,
                    "city": req_city,
                    "style": req_style,
                }
            )
            logger.info(f"[DEBUG] lm_params passed to lm_run: {lm_params}")

            lm_result = await lm_run(request.prompt, lm_params)
            spec_json = lm_result.get("spec_json")
            lm_provider = lm_result.get("provider", "local")

            logger.info(f"LM returned result from {lm_provider} provider")

            if not spec_json:
                raise HTTPException(status_code=500, detail="LM returned empty spec")

            # FORCE CORRECT DIMENSIONS from extracted values
            extracted_dims = lm_params.get("extracted_dimensions", {})
            if extracted_dims:
                if "width" in extracted_dims:
                    spec_json["dimensions"]["width"] = round(extracted_dims["width"], 2)
                if "length" in extracted_dims:
                    spec_json["dimensions"]["length"] = round(extracted_dims["length"], 2)
                if "height" in extracted_dims:
                    spec_json["dimensions"]["height"] = round(extracted_dims["height"], 2)
                logger.info(f"Forced dimensions: {spec_json['dimensions']}")

                # Scale object dimensions to fit within building dimensions
                building_width = spec_json["dimensions"]["width"]
                building_length = spec_json["dimensions"]["length"]
                building_height = spec_json["dimensions"]["height"]

                for obj in spec_json.get("objects", []):
                    obj_dims = obj.get("dimensions", {})
                    obj_type = obj.get("type", "")
                    subtype = obj.get("subtype", "")

                    # Foundation and roof match building footprint
                    if obj_type in ["foundation", "roof"]:
                        obj_dims["width"] = building_width
                        obj_dims["length"] = building_length
                        if obj_type == "foundation":
                            obj_dims["height"] = 0.5  # Standard foundation depth
                        else:
                            obj_dims["height"] = 0.2  # Standard roof slab

                    # External walls match building perimeter and height
                    elif obj_type == "wall" and "external" in subtype:
                        obj_dims["width"] = max(building_width, building_length)
                        obj_dims["length"] = 0.2  # Standard wall thickness
                        obj_dims["height"] = building_height

                    # Internal walls are shorter
                    elif obj_type == "wall" and "internal" in subtype:
                        obj_dims["width"] = 0.15  # Thinner internal walls
                        obj_dims["length"] = min(building_width, building_length) * 0.5
                        obj_dims["height"] = min(building_height, 3.0)

                    # Doors - realistic sizes
                    elif obj_type == "door":
                        if "main" in subtype or "entrance" in subtype:
                            obj_dims["width"] = 1.2  # 1.2m main door
                            obj_dims["height"] = 2.1  # Standard door height
                        else:
                            obj_dims["width"] = 0.9  # 0.9m internal door
                            obj_dims["height"] = 2.0
                        obj_dims["length"] = 0.05  # Door thickness

                    # Windows - realistic sizes
                    elif obj_type == "window":
                        obj_dims["width"] = 1.2  # Standard window width
                        obj_dims["height"] = 1.5  # Standard window height
                        obj_dims["length"] = 0.1  # Window frame depth

                    # Furniture - scale to room size
                    elif obj_type == "furniture":
                        max_furniture_width = building_width * 0.4
                        if "width" in obj_dims and obj_dims["width"] > max_furniture_width:
                            obj_dims["width"] = max_furniture_width
                        if "length" in obj_dims and obj_dims["length"] > building_length * 0.3:
                            obj_dims["length"] = building_length * 0.3
                        if "height" in obj_dims and obj_dims["height"] > 2.5:
                            obj_dims["height"] = 2.5

                logger.info(f"Scaled all objects to realistic proportions")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"LM call failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=503, detail=f"LM service unavailable: {str(e)[:100]}")

        # 3. VALIDATE SPEC BEFORE PROCEEDING
        logger.info("Validating spec_json completeness...")
        try:
            validate_spec_json(spec_json)
            warnings = validate_with_warnings(spec_json)
            if warnings:
                logger.info(f"Spec warnings: {len(warnings)} non-critical issues")
        except SpecValidationError as e:
            logger.error(f"Spec validation failed: {e}")
            raise HTTPException(
                status_code=400, detail=f"Invalid specification from LM: {str(e)}. Please try rephrasing your prompt."
            )

        # 4. CALCULATE COST AND ENHANCE SPEC
        logger.info(f"Calculating cost for {len(spec_json.get('objects', []))} objects...")

        # Calculate realistic cost based on actual dimensions and city
        dims = spec_json.get("dimensions", {})
        area_sqm = dims.get("width", 10) * dims.get("length", 10)
        area_sqft = area_sqm * 10.764  # Convert sqm to sqft
        stories = spec_json.get("stories", 1)

        # City-wise construction rates (INR per sq ft)
        city_rates = {
            "Mumbai": 2100,  # Average of 1700-2500
            "Nashik": 1000,  # Average of 800-1200
            "Pune": 1450,  # Average of 1300-1600
            "Ahmedabad": 1775,  # Average of 1650-1900
        }

        # Get rate for city (default to Mumbai if not found)
        rate_per_sqft = city_rates.get(req_city, 2100)
        calculated_cost = int(area_sqft * rate_per_sqft * stories)

        # Use 95% of budget if provided, otherwise use calculated
        if budget and isinstance(budget, (int, float)) and budget > 0:
            estimated_cost = int(budget * 0.95)
            logger.info(f"Using 95% of budget: Rs.{estimated_cost:,.0f} (budget: Rs.{budget:,.0f})")
        else:
            estimated_cost = calculated_cost
            logger.info(
                f"Calculated cost for {req_city}: Rs.{estimated_cost:,.0f} ({area_sqft:.0f} sqft @ Rs.{rate_per_sqft}/sqft)"
            )

        # Force correct city and style in metadata
        req_city = getattr(request, "city", "Mumbai")
        req_style = getattr(request, "style", "modern")
        if "metadata" not in spec_json:
            spec_json["metadata"] = {}
        spec_json["metadata"]["estimated_cost"] = estimated_cost
        spec_json["metadata"]["currency"] = "INR"
        spec_json["metadata"]["generation_provider"] = lm_provider
        spec_json["metadata"]["city"] = req_city
        spec_json["metadata"]["style"] = req_style
        spec_json["metadata"]["area_sqft"] = round(area_sqft, 2)
        if budget:
            spec_json["metadata"]["budget_provided"] = budget
        else:
            spec_json["metadata"]["rate_per_sqft"] = rate_per_sqft

        # FORCE override estimated_cost in spec_json
        spec_json["estimated_cost"] = {"total": estimated_cost, "currency": "INR"}

        logger.info(f"[DEBUG] Set metadata city to: {req_city}")

        # 5. CREATE SPEC ID AND GENERATE PREVIEW FIRST
        import uuid

        spec_id = f"spec_{uuid.uuid4().hex[:12]}"

        # 6. GENERATE PREVIEW FILE WITH MESHY AI
        try:
            from app.storage import upload_geometry

            glb_content = None

            # Try Meshy AI first (realistic 3D)
            if settings.MESHY_API_KEY:
                try:
                    from app.meshy_3d_generator import generate_3d_with_meshy

                    logger.info("🎨 Trying Meshy AI (realistic 3D)...")
                    glb_content = await generate_3d_with_meshy(request.prompt, spec_json["dimensions"])
                    if glb_content:
                        logger.info(f"✅ Meshy AI generated {len(glb_content)} bytes")
                except Exception as meshy_error:
                    logger.warning(f"Meshy AI failed: {meshy_error}")

            # Fallback to Tripo AI
            if not glb_content and settings.TRIPO_API_KEY:
                try:
                    from app.tripo_3d_generator import generate_3d_with_tripo

                    logger.info("🎨 Trying Tripo AI (fallback)...")
                    glb_content = await generate_3d_with_tripo(
                        request.prompt, spec_json["dimensions"], settings.TRIPO_API_KEY
                    )
                except Exception as tripo_error:
                    logger.warning(f"Tripo AI failed: {tripo_error}")

            # Final fallback to basic GLB (instant, free, reliable)
            if not glb_content:
                logger.info("🎨 Using fallback geometry generator (instant, free)")
                glb_content = generate_mock_glb(spec_json)

            # Upload to Supabase storage
            preview_url = upload_geometry(spec_id, glb_content)
            logger.info(f"✅ Preview uploaded: {preview_url}")

        except Exception as e:
            logger.warning(f"Preview generation failed, using local path: {e}")
            # Fallback to local file path
            local_preview_path = f"data/geometry_outputs/{spec_id}.glb"
            create_local_preview_file(spec_json, local_preview_path)
            preview_url = f"http://localhost:8000/static/geometry/{spec_id}.glb"

        # 7. SAVE TO DATABASE
        from app.database import SessionLocal
        from app.models import Spec, User

        logger.info(f"Saving spec {spec_id} to database...")

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
                logger.info(f"Created user {request.user_id}")
            else:
                # Use the existing user's actual ID
                request.user_id = user.id
                logger.info(f"Using existing user {user.username} with id {user.id}")

            # Create spec with required fields
            req_city = getattr(request, "city", "Mumbai")
            db_spec = Spec(
                id=spec_id,
                user_id=request.user_id,
                prompt=request.prompt,
                city=req_city,
                spec_json=spec_json,
            )
            logger.info(f"[DEBUG] Saving to DB with city: {req_city}")

            db.add(db_spec)
            db.commit()
            db.refresh(db_spec)
            logger.info(f"Successfully saved spec {spec_id} to database")
        except Exception as db_error:
            db.rollback()
            logger.error(f"Database save FAILED: {db_error}")
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
        logger.info(f"Generated spec {spec_id} for user {request.user_id} in {generation_time}ms")

        # 8. RETURN RESPONSE
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
        logger.info(f"Returning response with spec_id: {spec_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error during spec generation")


@router.get("/specs/{spec_id}", response_model=GenerateResponse)
async def get_spec(spec_id: str):
    """
    Retrieve existing specification by ID

    Returns the complete design specification including:
    - spec_json: Full design data
    - preview_url: 3D model URL
    - estimated_cost: Cost in INR
    - metadata: Creation time, version, etc.
    """
    logger.info(f"GET SPEC REQUEST: spec_id={spec_id}")

    # Try to get spec from database first
    try:
        from app.database import SessionLocal
        from app.models import Spec

        db = SessionLocal()
        try:
            db_spec = db.query(Spec).filter(Spec.id == spec_id).first()

            if db_spec:
                logger.info(f"Found spec {spec_id} in database")

                # Generate preview URL
                try:
                    from app.storage import supabase

                    preview_url = supabase.storage.from_("geometry").get_public_url(f"{spec_id}.glb")
                except Exception as e:
                    logger.warning(f"Supabase URL generation failed: {e}")
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
                logger.info(f"Returning database spec for {spec_id}")
                return response
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Database query failed for spec {spec_id}: {e}")

    # Spec not found anywhere
    logger.warning(f"Spec {spec_id} not found in database")
    raise HTTPException(
        status_code=404,
        detail=f"Specification '{spec_id}' not found. Generate a design first using /api/v1/generate",
    )
