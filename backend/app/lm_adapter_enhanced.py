"""Enhanced Template Generator with Intelligent Prompt Parsing"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def parse_prompt_keywords(prompt: str) -> Dict[str, List[str]]:
    """Extract keywords from prompt"""
    prompt_lower = prompt.lower()
    keywords = {"rooms": [], "features": [], "furniture": []}

    room_patterns = {
        "conference": ["conference", "meeting room"],
        "open_layout": ["open layout", "open plan"],
        "workstation": ["workstation", "desk"],
        "reception": ["reception", "lobby"],
        "pantry": ["pantry", "kitchen", "break room"],
    }

    for room_type, patterns in room_patterns.items():
        if any(p in prompt_lower for p in patterns):
            keywords["rooms"].append(room_type)

    if "glass" in prompt_lower:
        keywords["features"].append("glass_walls")
    if "modern" in prompt_lower or "contemporary" in prompt_lower:
        keywords["features"].append("modern_design")

    return keywords


def generate_enhanced_commercial_office(prompt: str, params: dict) -> dict:
    """Generate comprehensive commercial office"""
    keywords = parse_prompt_keywords(prompt)
    width, length, height = 20, 30, 3.0

    objects = [
        {
            "id": "office_floor",
            "type": "floor",
            "material": "tile_ceramic",
            "color_hex": "#F5F5F5",
            "dimensions": {"width": width, "length": length},
        },
        {
            "id": "glass_facade",
            "type": "wall",
            "subtype": "exterior",
            "material": "glass_tempered",
            "color_hex": "#E0FFFF",
            "dimensions": {"width": width, "height": height},
        },
        {
            "id": "suspended_ceiling",
            "type": "ceiling",
            "material": "gypsum_board",
            "color_hex": "#FFFFFF",
            "dimensions": {"width": width, "length": length},
        },
    ]

    if "open" in keywords["rooms"] or "workstation" in keywords["rooms"]:
        objects.extend(
            [
                {
                    "id": "open_workstations",
                    "type": "furniture",
                    "subtype": "workstation",
                    "material": "laminate",
                    "color_hex": "#D3D3D3",
                    "count": 15,
                    "dimensions": {"width": 1.5, "depth": 0.8, "height": 0.75},
                },
                {
                    "id": "office_chairs",
                    "type": "furniture",
                    "subtype": "chair",
                    "material": "fabric",
                    "color_hex": "#000000",
                    "count": 15,
                    "dimensions": {"width": 0.6, "depth": 0.6, "height": 1.2},
                },
            ]
        )

    if "conference" in keywords["rooms"]:
        objects.extend(
            [
                {
                    "id": "conference_room_1",
                    "type": "room",
                    "subtype": "conference",
                    "material": "glass_partition",
                    "color_hex": "#E0E0E0",
                    "dimensions": {"width": 6, "length": 8, "height": height},
                },
                {
                    "id": "conference_table",
                    "type": "furniture",
                    "subtype": "table",
                    "material": "wood_oak",
                    "color_hex": "#8B4513",
                    "dimensions": {"width": 2.5, "length": 5, "height": 0.75},
                },
                {
                    "id": "conference_chairs",
                    "type": "furniture",
                    "subtype": "chair",
                    "material": "leather",
                    "color_hex": "#000000",
                    "count": 12,
                    "dimensions": {"width": 0.6, "depth": 0.6, "height": 1.0},
                },
            ]
        )

    objects.extend(
        [
            {
                "id": "reception_desk",
                "type": "furniture",
                "subtype": "reception",
                "material": "wood_oak",
                "color_hex": "#8B4513",
                "dimensions": {"width": 2.5, "depth": 1.0, "height": 1.1},
            },
            {
                "id": "pantry",
                "type": "room",
                "subtype": "pantry",
                "material": "tile_ceramic",
                "color_hex": "#FFFFFF",
                "dimensions": {"width": 4, "length": 3, "height": height},
            },
            {
                "id": "restroom_male",
                "type": "room",
                "subtype": "restroom",
                "material": "tile_ceramic",
                "color_hex": "#FFFFFF",
                "dimensions": {"width": 3, "length": 4, "height": height},
            },
            {
                "id": "restroom_female",
                "type": "room",
                "subtype": "restroom",
                "material": "tile_ceramic",
                "color_hex": "#FFFFFF",
                "dimensions": {"width": 3, "length": 4, "height": height},
            },
            {
                "id": "led_lighting",
                "type": "fixture",
                "subtype": "lighting",
                "material": "led",
                "color_hex": "#FFFFFF",
                "count": 30,
                "dimensions": {"width": 0.6, "length": 0.6, "height": 0.1},
            },
            {
                "id": "hvac_system",
                "type": "fixture",
                "subtype": "hvac",
                "material": "metal",
                "color_hex": "#C0C0C0",
                "count": 4,
                "dimensions": {"width": 1.0, "length": 1.0, "height": 0.5},
            },
        ]
    )

    return {
        "objects": objects,
        "design_type": "commercial_office",
        "style": params.get("style", "contemporary"),
        "dimensions": {"width": width, "length": length, "height": height},
        "estimated_cost": {"total": width * length * 30000, "currency": "INR"},
        "metadata": {"total_objects": len(objects), "rooms_included": keywords["rooms"]},
    }


def generate_enhanced_design_from_prompt(prompt: str, params: dict) -> dict:
    """Enhanced template with prompt analysis"""
    prompt_lower = prompt.lower()

    if any(word in prompt_lower for word in ["office", "commercial", "workspace"]):
        if any(word in prompt_lower for word in ["conference", "meeting", "open layout"]):
            logger.info("ENHANCED: Generating comprehensive commercial office")
            return generate_enhanced_commercial_office(prompt, params)

    from app.lm_adapter import generate_design_from_prompt

    return generate_design_from_prompt(prompt, params)
