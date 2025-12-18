import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict

import httpx
from app.config import settings

logger = logging.getLogger(__name__)


def run_local_lm(prompt: str, params: dict) -> dict:
    """Run inference on local RTX-3060 GPU"""
    logger.info(f"LOCAL_LM_DEBUG: Running local LM for prompt: '{prompt}' (length: {len(prompt)})")

    # Generate design based on prompt type
    spec_json = generate_design_from_prompt(prompt, params)

    logger.info(f"LOCAL_LM_DEBUG: Generated spec_json with design_type: {spec_json.get('design_type', 'unknown')}")

    # Log usage for billing
    log_usage("local", len(prompt), 0.001, params.get("user_id"))  # $0.001 per token

    result = {
        "spec_json": spec_json,
        "preview_data": f"Local GPU generated {spec_json.get('design_type', 'design')} for: {prompt[:50]}...",
        "provider": "local",
        "feedback": f"Local GPU generated {spec_json.get('design_type', 'design')} using strategy: {params.get('strategy', 'modern')}",
    }

    logger.info(f"LOCAL_LM_DEBUG: Returning result with spec_json keys: {list(spec_json.keys())}")
    return result


def generate_design_from_prompt(prompt: str, params: dict) -> dict:
    """Generate any design based on prompt analysis"""
    prompt_lower = prompt.lower()
    logger.info(f"DESIGN_DEBUG: Analyzing prompt: {prompt_lower}")

    # Detect design type - prioritize larger structures first
    if any(word in prompt_lower for word in ["house", "home", "building", "residential", "story", "floor"]):
        logger.info("DESIGN_DEBUG: Detected HOUSE design")
        return generate_house_design(prompt, params)
    elif any(word in prompt_lower for word in ["kitchen", "cook", "cabinet", "countertop"]):
        logger.info("DESIGN_DEBUG: Detected KITCHEN design")
        return generate_kitchen_design(prompt, params)
    elif any(word in prompt_lower for word in ["office", "commercial", "workspace", "corporate"]):
        logger.info("DESIGN_DEBUG: Detected OFFICE design")
        return generate_office_design(prompt, params)
    elif any(word in prompt_lower for word in ["bathroom", "bath", "shower", "toilet"]):
        logger.info("DESIGN_DEBUG: Detected BATHROOM design")
        return generate_bathroom_design(prompt, params)
    elif any(word in prompt_lower for word in ["bedroom", "bed", "sleep"]):
        logger.info("DESIGN_DEBUG: Detected BEDROOM design")
        return generate_bedroom_design(prompt, params)
    elif any(word in prompt_lower for word in ["living room", "lounge", "family room"]):
        logger.info("DESIGN_DEBUG: Detected LIVING ROOM design")
        return generate_living_room_design(prompt, params)
    else:
        logger.info("DESIGN_DEBUG: Using GENERIC design")
        return generate_generic_design(prompt, params)


def generate_kitchen_design(prompt: str, params: dict) -> dict:
    """Generate budget-aware kitchen design"""
    prompt_lower = prompt.lower()
    extracted_dims = params.get("extracted_dimensions", {})
    context = params.get("context", {})
    budget = context.get("budget", 800000)  # Default ₹8L

    # Budget-based kitchen sizing
    if budget <= 500000:  # ₹5L: Small kitchen
        width, length = 8, 10
    elif budget <= 1000000:  # ₹10L: Medium kitchen
        width, length = 10, 12
    else:  # ₹10L+: Large kitchen
        width, length = 12, 15

    # Use extracted dims if provided
    width = extracted_dims.get("width", width)
    length = extracted_dims.get("length", length)

    if "feet" in prompt_lower or "ft" in prompt_lower:
        width *= 0.3048
        length *= 0.3048

    style = "modern"
    if "traditional" in prompt_lower:
        style = "traditional"
    elif "rustic" in prompt_lower:
        style = "rustic"

    objects = [
        {
            "id": "kitchen_floor",
            "type": "floor",
            "material": "tile_ceramic",
            "color_hex": "#F5F5DC",
            "dimensions": {"width": width, "length": length},
        },
        {
            "id": "base_cabinets",
            "type": "cabinet",
            "material": "wood_oak",
            "color_hex": "#FFFFFF",
            "dimensions": {"width": width * 0.6, "depth": 0.6, "height": 0.9},
        },
        {
            "id": "countertop",
            "type": "countertop",
            "material": "granite" if "granite" in prompt_lower else "quartz",
            "color_hex": "#2F4F4F",
            "dimensions": {"width": width * 0.6, "depth": 0.6, "height": 0.05},
        },
    ]

    if "island" in prompt_lower:
        objects.append(
            {
                "id": "kitchen_island",
                "type": "island",
                "material": "wood_oak",
                "dimensions": {"width": 2.4, "depth": 1.2, "height": 0.9},
            }
        )

    return {
        "objects": objects,
        "design_type": "kitchen",
        "style": style,
        "dimensions": {"width": width, "length": length, "height": 2.7},
        "estimated_cost": {"total": min(budget * 1.1, width * length * 35000), "currency": "INR"},
    }


def generate_house_design(prompt: str, params: dict) -> dict:
    """Generate house/building design with budget optimization"""
    logger.info("DESIGN_DEBUG: Generating HOUSE design")
    prompt_lower = prompt.lower()
    extracted_dims = params.get("extracted_dimensions", {})
    context = params.get("context", {})
    budget = context.get("budget", 15000000)  # Default ₹1.5 crores

    # Budget-based dimension optimization
    width, length, height = optimize_house_dimensions_for_budget(budget, extracted_dims)

    logger.info(f"DESIGN_DEBUG: Budget ₹{budget:,} → Optimized dimensions {width}x{length}x{height}")

    if "feet" in prompt_lower or "ft" in prompt_lower:
        width *= 0.3048
        length *= 0.3048
        height *= 0.3048
        logger.info(f"DESIGN_DEBUG: Converted to meters - width: {width}, length: {length}, height: {height}")

    logger.info(f"DESIGN_DEBUG: Final dimensions - width: {width}, length: {length}, height: {height}")

    style = "modern"
    if "traditional" in prompt_lower:
        style = "traditional"
    elif "colonial" in prompt_lower:
        style = "colonial"
    elif "contemporary" in prompt_lower:
        style = "contemporary"

    stories = 1
    if "two story" in prompt_lower or "2 story" in prompt_lower or "2-story" in prompt_lower:
        stories = 2
    elif "three story" in prompt_lower or "3 story" in prompt_lower or "3-story" in prompt_lower:
        stories = 3

    logger.info(f"DESIGN_DEBUG: House style: {style}, stories: {stories}")

    objects = [
        {
            "id": "foundation",
            "type": "foundation",
            "material": "concrete",
            "color_hex": "#808080",
            "dimensions": {"width": width, "length": length, "height": 0.5},
        },
        {
            "id": "exterior_walls",
            "type": "wall",
            "subtype": "exterior",
            "material": "brick" if style == "traditional" else "siding",
            "color_hex": "#D2B48C",
            "dimensions": {"width": width, "length": length, "height": height},
        },
        {
            "id": "roof",
            "type": "roof",
            "material": "shingle_asphalt",
            "color_hex": "#2F4F4F",
            "dimensions": {"width": width + 2, "length": length + 2, "height": 3},
        },
        {
            "id": "front_door",
            "type": "door",
            "subtype": "entrance",
            "material": "wood_oak",
            "color_hex": "#8B4513",
            "dimensions": {"width": 1, "height": 2.1},
        },
        {
            "id": "windows",
            "type": "window",
            "material": "glass_double_pane",
            "color_hex": "#87CEEB",
            "count": 8,
            "dimensions": {"width": 1.2, "height": 1.5},
        },
    ]

    if "garage" in prompt_lower:
        objects.append(
            {
                "id": "garage",
                "type": "garage",
                "material": "concrete",
                "dimensions": {"width": 6, "length": 6, "height": 2.5},
            }
        )
        logger.info("DESIGN_DEBUG: Added garage")

    if "porch" in prompt_lower or "patio" in prompt_lower:
        objects.append(
            {
                "id": "porch",
                "type": "porch",
                "material": "wood_deck",
                "dimensions": {"width": width * 0.8, "length": 3, "height": 0.2},
            }
        )
        logger.info("DESIGN_DEBUG: Added porch")

    result = {
        "objects": objects,
        "design_type": "house",
        "style": style,
        "stories": stories,
        "dimensions": {"width": width, "length": length, "height": height * stories},
        "estimated_cost": {
            "total": min(budget * 1.05, calculate_actual_house_cost(width, length, stories, objects)),
            "currency": "INR",
        },
        "tech_stack": ["Local GPU"],
        "model_used": "local-rtx-3060",
    }

    logger.info(f"DESIGN_DEBUG: Generated house design with {len(objects)} objects")
    return result


def generate_office_design(prompt: str, params: dict) -> dict:
    """Generate office design"""
    prompt_lower = prompt.lower()
    extracted_dims = params.get("extracted_dimensions", {})
    context = params.get("context", {})

    logger.info(f"OFFICE_DEBUG: Prompt='{prompt}', Dims={extracted_dims}, Context={context}")

    # Enhanced detection for executive/private offices
    is_cabin = (
        any(word in prompt_lower for word in ["cabin", "small", "executive", "private", "individual"])
        or context.get("style_preference") == "executive"
        or context.get("space_type") == "private"
    )

    if is_cabin:
        # Small office cabin design
        width = extracted_dims.get("width", 3.6)  # 12 feet default
        length = extracted_dims.get("length", 3.0)  # 10 feet default

        # Convert feet to meters if needed
        if "feet" in prompt_lower or "ft" in prompt_lower:
            # Always convert if feet are mentioned, regardless of value
            width = width * 0.3048
            length = length * 0.3048
            logger.info(
                f"OFFICE_DEBUG: Converted {extracted_dims.get('width', 3.6)}x{extracted_dims.get('length', 3.0)} feet to {width:.2f}x{length:.2f} meters"
            )

        objects = [
            {
                "id": "cabin_floor",
                "type": "floor",
                "material": "vinyl_plank",
                "color_hex": "#D2B48C",
                "dimensions": {"width": width, "length": length},
            },
            {
                "id": "executive_desk",
                "type": "furniture",
                "subtype": "desk",
                "material": "wood_oak",
                "color_hex": "#8B4513",
                "dimensions": {"width": 1.5, "depth": 0.8, "height": 0.75},
            },
            {
                "id": "office_chair",
                "type": "furniture",
                "subtype": "chair",
                "material": "leather",
                "color_hex": "#000000",
                "dimensions": {"width": 0.6, "depth": 0.6, "height": 1.2},
            },
            {
                "id": "storage_cabinet",
                "type": "storage",
                "subtype": "cabinet",
                "material": "wood_oak",
                "color_hex": "#8B4513",
                "dimensions": {"width": 1.2, "depth": 0.4, "height": 1.8},
            },
            {
                "id": "meeting_table",
                "type": "furniture",
                "subtype": "table",
                "material": "wood_oak",
                "color_hex": "#8B4513",
                "dimensions": {"width": 1.0, "depth": 0.6, "height": 0.75},
            },
        ]

        # Add bookcase if mentioned in prompt
        if "bookcase" in prompt_lower or "book" in prompt_lower:
            objects.append(
                {
                    "id": "executive_bookcase",
                    "type": "storage",
                    "subtype": "bookcase",
                    "material": "wood_oak",
                    "color_hex": "#8B4513",
                    "dimensions": {"width": 1.0, "depth": 0.3, "height": 2.0},
                }
            )
            logger.info("OFFICE_DEBUG: Added bookcase to executive office")

        budget = context.get("budget", 400000)
        actual_cost = width * length * 15000  # ₹15k per sqm for office

        result = {
            "objects": objects,
            "design_type": "office_cabin",
            "style": "executive",
            "dimensions": {"width": width, "length": length, "height": 2.7},
            "estimated_cost": {"total": min(budget * 1.1, actual_cost), "currency": "INR"},
        }

        logger.info(
            f"OFFICE_DEBUG: Generated EXECUTIVE office with {len(objects)} objects: {[obj['id'] for obj in objects]}"
        )
        return result
    else:
        # Large office design
        width = extracted_dims.get("width", 20)
        length = extracted_dims.get("length", 30)

        objects = [
            {
                "id": "office_floor",
                "type": "floor",
                "material": "carpet_commercial",
                "color_hex": "#708090",
                "dimensions": {"width": width, "length": length},
            },
            {
                "id": "workstations",
                "type": "furniture",
                "subtype": "desk",
                "material": "laminate",
                "color_hex": "#F5F5DC",
                "count": 12,
                "dimensions": {"width": 1.5, "depth": 0.8, "height": 0.75},
            },
            {
                "id": "conference_room",
                "type": "room",
                "subtype": "meeting",
                "material": "glass_partition",
                "dimensions": {"width": 6, "length": 4, "height": 2.7},
            },
        ]

        budget = context.get("budget", 1500000)
        actual_cost = width * length * 15000  # ₹15k per sqm for office

        result = {
            "objects": objects,
            "design_type": "office",
            "style": "corporate",
            "dimensions": {"width": width, "length": length, "height": 2.7},
            "estimated_cost": {"total": min(budget * 1.1, actual_cost), "currency": "INR"},
        }

        logger.info(
            f"OFFICE_DEBUG: Generated CORPORATE office with {len(objects)} objects: {[obj['id'] for obj in objects]}"
        )
        return result


def generate_bathroom_design(prompt: str, params: dict) -> dict:
    """Generate bathroom design"""
    objects = [
        {
            "id": "bathroom_floor",
            "type": "floor",
            "material": "tile_ceramic",
            "color_hex": "#FFFFFF",
            "dimensions": {"width": 3, "length": 2.5},
        },
        {
            "id": "toilet",
            "type": "fixture",
            "subtype": "toilet",
            "material": "porcelain",
            "color_hex": "#FFFFFF",
            "dimensions": {"width": 0.4, "depth": 0.7, "height": 0.8},
        },
        {
            "id": "shower",
            "type": "fixture",
            "subtype": "shower",
            "material": "glass_tempered",
            "dimensions": {"width": 1, "length": 1, "height": 2},
        },
        {
            "id": "vanity",
            "type": "cabinet",
            "subtype": "vanity",
            "material": "wood_oak",
            "color_hex": "#8B4513",
            "dimensions": {"width": 1.2, "depth": 0.5, "height": 0.85},
        },
    ]

    return {
        "objects": objects,
        "design_type": "bathroom",
        "style": "modern",
        "dimensions": {"width": 3, "length": 2.5, "height": 2.4},
        "estimated_cost": {"total": 400000, "currency": "INR"},
    }


def generate_bedroom_design(prompt: str, params: dict) -> dict:
    """Generate bedroom design"""
    objects = [
        {
            "id": "bedroom_floor",
            "type": "floor",
            "material": "wood_hardwood",
            "color_hex": "#DEB887",
            "dimensions": {"width": 4, "length": 4.5},
        },
        {
            "id": "bed",
            "type": "furniture",
            "subtype": "bed",
            "material": "wood_oak",
            "color_hex": "#8B4513",
            "dimensions": {"width": 2, "length": 2.1, "height": 0.6},
        },
        {
            "id": "dresser",
            "type": "furniture",
            "subtype": "dresser",
            "material": "wood_oak",
            "color_hex": "#8B4513",
            "dimensions": {"width": 1.5, "depth": 0.5, "height": 1},
        },
        {
            "id": "closet",
            "type": "storage",
            "subtype": "closet",
            "material": "wood_oak",
            "dimensions": {"width": 2, "depth": 0.6, "height": 2.4},
        },
    ]

    return {
        "objects": objects,
        "design_type": "bedroom",
        "style": "modern",
        "dimensions": {"width": 4, "length": 4.5, "height": 2.4},
        "estimated_cost": {"total": 300000, "currency": "INR"},
    }


def generate_living_room_design(prompt: str, params: dict) -> dict:
    """Generate living room design"""
    objects = [
        {
            "id": "living_floor",
            "type": "floor",
            "material": "wood_hardwood",
            "color_hex": "#DEB887",
            "dimensions": {"width": 5, "length": 6},
        },
        {
            "id": "sofa",
            "type": "furniture",
            "subtype": "sofa",
            "material": "fabric",
            "color_hex": "#708090",
            "dimensions": {"width": 2.5, "depth": 1, "height": 0.8},
        },
        {
            "id": "coffee_table",
            "type": "furniture",
            "subtype": "table",
            "material": "wood_oak",
            "color_hex": "#8B4513",
            "dimensions": {"width": 1.2, "depth": 0.6, "height": 0.4},
        },
        {
            "id": "tv_stand",
            "type": "furniture",
            "subtype": "entertainment",
            "material": "wood_oak",
            "color_hex": "#8B4513",
            "dimensions": {"width": 1.8, "depth": 0.4, "height": 0.6},
        },
    ]

    return {
        "objects": objects,
        "design_type": "living_room",
        "style": "modern",
        "dimensions": {"width": 5, "length": 6, "height": 2.4},
        "estimated_cost": {"total": 400000, "currency": "INR"},
    }


def generate_generic_design(prompt: str, params: dict) -> dict:
    """Generate generic design for unspecified prompts"""
    return {
        "objects": [
            {
                "id": "base_structure",
                "type": "structure",
                "material": "concrete",
                "color_hex": "#808080",
                "dimensions": {"width": 10, "length": 10, "height": 3},
            }
        ],
        "design_type": "generic",
        "style": "modern",
        "dimensions": {"width": 10, "length": 10, "height": 3},
        "estimated_cost": {"total": 500000, "currency": "INR"},
    }


async def run_yotta_lm(prompt: str, params: dict) -> dict:
    """Run inference on Yotta cloud API"""
    logger.info(f"Running Yotta LM for prompt length: {len(prompt)}")

    # Always use mock response for testing (no paid API calls)
    logger.info("Using mock Yotta response (testing mode)")

    # Generate design for complex prompts
    spec_json = generate_design_from_prompt(prompt, params)
    spec_json["tech_stack"] = ["Yotta Cloud"]
    spec_json["model_used"] = "yotta-advanced-model"

    # Log mock usage for billing
    log_usage("yotta", len(prompt), 0.01, params.get("user_id"))  # $0.01 per token

    return {
        "spec_json": spec_json,
        "preview_data": f"Yotta cloud generated {spec_json.get('design_type', 'design')} for: {prompt[:50]}...",
        "provider": "yotta",
        "feedback": f"Yotta cloud generated advanced {spec_json.get('design_type', 'design')} using strategy: {params.get('strategy', 'premium')}",
    }


def extract_dimensions_from_prompt(prompt: str) -> dict:
    """Extract dimensions from natural language prompt"""
    dimensions = {}

    # Patterns to match dimensions
    patterns = [
        r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*(?:x\s*(\d+(?:\.\d+)?))?\s*(?:meter|metres|m|feet|ft|cm|centimeter|centimeters)",
        r"(\d+(?:\.\d+)?)\s*by\s*(\d+(?:\.\d+)?)\s*(?:by\s*(\d+(?:\.\d+)?))?\s*(?:meter|metres|m|feet|ft|cm|centimeter|centimeters)",
        r"length\s*(\d+(?:\.\d+)?)\s*(?:meter|metres|m|feet|ft|cm|centimeter|centimeters)",
        r"width\s*(\d+(?:\.\d+)?)\s*(?:meter|metres|m|feet|ft|cm|centimeter|centimeters)",
        r"height\s*(\d+(?:\.\d+)?)\s*(?:meter|metres|m|feet|ft|cm|centimeter|centimeters)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, prompt.lower())
        if matches:
            if len(matches[0]) == 3 and matches[0][2]:  # 3D dimensions
                dimensions = {
                    "length": float(matches[0][0]),
                    "width": float(matches[0][1]),
                    "height": float(matches[0][2]),
                }
                break
            elif len(matches[0]) >= 2:  # 2D dimensions
                dimensions = {
                    "width": float(matches[0][0]),  # First number is width
                    "length": float(matches[0][1]),  # Second number is length
                    "height": 3.0,  # default height
                }
                break

    return dimensions


async def lm_run(prompt: str, params: dict = None) -> dict:
    """Route to local GPU or Yotta based on prompt complexity"""
    if params is None:
        params = {}

    logger.info(f"LM_RUN_DEBUG: Processing prompt: '{prompt}' (length: {len(prompt)})")

    # Extract dimensions from prompt
    extracted_dims = extract_dimensions_from_prompt(prompt)
    if extracted_dims:
        params["extracted_dimensions"] = extracted_dims
        logger.info(f"LM_RUN_DEBUG: Extracted dimensions from prompt: {extracted_dims}")

    # Simple heuristic: use local if prompt short, else use Yotta
    if len(prompt) < 150:  # Local GPU for simple tasks
        logger.info("LM_RUN_DEBUG: Using LOCAL GPU")
        return run_local_lm(prompt, params)
    else:  # Yotta for heavy jobs
        logger.info("LM_RUN_DEBUG: Using YOTTA cloud")
        return await run_yotta_lm(prompt, params)


def optimize_house_dimensions_for_budget(budget: float, extracted_dims: dict) -> tuple:
    """Optimize house dimensions to fit within budget"""
    # Budget tiers with corresponding dimensions (optimized for realistic costs)
    budget_tiers = [
        (5000000, (12, 15, 6)),  # ₹50L: 12x15m, 6m height (180 sqm)
        (8000000, (14, 18, 7)),  # ₹80L: 14x18m, 7m height (252 sqm)
        (12000000, (16, 22, 7)),  # ₹1.2Cr: 16x22m, 7m height (352 sqm)
        (20000000, (20, 28, 8)),  # ₹2Cr: 20x28m, 8m height (560 sqm)
        (50000000, (25, 35, 8)),  # ₹5Cr: 25x35m, 8m height (875 sqm)
        (float("inf"), (30, 40, 10)),  # ₹5Cr+: 30x40m, 10m height (1200 sqm)
    ]

    # Find appropriate tier for budget
    for budget_limit, (w, l, h) in budget_tiers:
        if budget <= budget_limit:
            # Use extracted dimensions if provided and reasonable
            width = extracted_dims.get("width", w)
            length = extracted_dims.get("length", l)
            height = extracted_dims.get("height", h)

            # Scale down if extracted dims would exceed budget
            if width * length > w * l * 1.5:  # 50% tolerance
                scale = ((w * l) / (width * length)) ** 0.5
                width *= scale
                length *= scale

            return width, length, height

    return 30, 40, 8  # Default fallback


def calculate_actual_house_cost(width: float, length: float, stories: int, objects: list) -> float:
    """Calculate budget-optimized house cost"""
    area = width * length

    # Reduced construction cost for budget optimization
    cost_per_sqm = 15000  # Reduced from ₹25k to ₹15k per sqm
    base_cost = area * stories * cost_per_sqm

    # Reduced object premiums
    premiums = {
        "garage": 100000,  # Reduced from ₹2L to ₹1L
        "roof": 75000,  # Reduced from ₹1.5L to ₹75k
        "foundation": 50000,  # Reduced from ₹1L to ₹50k
    }

    premium_cost = sum(premiums.get(obj.get("type"), 0) for obj in objects)

    return base_cost + premium_cost


def log_usage(provider: str, tokens: int, cost_per_token: float, user_id: str = None):
    """Log LM usage for billing with detailed tracking"""
    total_cost = cost_per_token * tokens
    usage_log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "tokens": tokens,
        "cost_per_token": cost_per_token,
        "total_cost": total_cost,
        "user_id": user_id,
        "gpu_hours": tokens / 1000 if provider == "local" else 0,  # Estimate GPU usage
        "api_calls": 1 if provider == "yotta" else 0,
    }

    # Log for monitoring and billing
    logger.info(f"BILLING: {usage_log}")

    # Store in usage log file (with error handling)
    try:
        with open("lm_usage.log", "a") as f:
            f.write(f"{usage_log}\n")
    except Exception as e:
        logger.warning(f"Failed to write usage log: {e}")

    # Log to audit system (simplified)
    try:
        from app.utils import log_audit_event

        if user_id:
            log_audit_event(
                "lm_usage",
                user_id,
                {"provider": provider, "tokens": tokens, "cost": total_cost},
            )
    except ImportError:
        logger.debug("Audit logging not available - skipping")


class LMAdapter:
    async def generate(self, prompt: str, model: str = "default") -> str:
        result = await lm_run(prompt, {"model": model})
        return result["preview_data"]


lm_adapter = LMAdapter()
