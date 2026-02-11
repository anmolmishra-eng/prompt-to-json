"""
Demo Runner - Generate demo assets for all cities
"""
import json
import os
from datetime import datetime

from demo_prompts import DEMO_PROMPTS

OUTPUT_DIR = "demo_assets"


def generate_demo_specs():
    """Generate demo spec JSON files"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    demo_data = {
        "generated_at": datetime.now().isoformat(),
        "total_prompts": sum(len(prompts) for prompts in DEMO_PROMPTS.values()),
        "cities": {},
    }

    for city, prompts in DEMO_PROMPTS.items():
        city_specs = []

        for i, prompt in enumerate(prompts, 1):
            spec_id = f"demo_{city.lower()}_{i}"

            # Generate basic spec structure
            spec = {
                "spec_id": spec_id,
                "prompt": prompt,
                "city": city,
                "building_type": extract_building_type(prompt),
                "floors": extract_floors(prompt),
                "units": extract_units(prompt),
                "plot_area": 1000,
                "timestamp": datetime.now().isoformat(),
            }

            # Save individual spec
            spec_file = f"{OUTPUT_DIR}/{spec_id}.json"
            with open(spec_file, "w") as f:
                json.dump(spec, f, indent=2)

            city_specs.append(spec)
            print(f"Generated: {spec_id}")

        demo_data["cities"][city] = {
            "count": len(prompts),
            "specs": city_specs,
        }

    # Save summary
    summary_file = f"{OUTPUT_DIR}/demo_summary.json"
    with open(summary_file, "w") as f:
        json.dump(demo_data, f, indent=2)

    print(f"\nDemo assets generated: {OUTPUT_DIR}/")
    print(f"Total specs: {demo_data['total_prompts']}")
    return demo_data


def extract_building_type(prompt):
    """Extract building type from prompt"""
    prompt_lower = prompt.lower()
    if "apartment" in prompt_lower or "bhk" in prompt_lower:
        return "residential_apartment"
    elif "villa" in prompt_lower or "house" in prompt_lower:
        return "residential_villa"
    elif "office" in prompt_lower or "commercial" in prompt_lower:
        return "commercial_office"
    elif "tower" in prompt_lower or "building" in prompt_lower:
        return "residential_tower"
    elif "resort" in prompt_lower or "hotel" in prompt_lower:
        return "hospitality"
    elif "school" in prompt_lower:
        return "educational"
    elif "hospital" in prompt_lower:
        return "healthcare"
    else:
        return "mixed_use"


def extract_floors(prompt):
    """Extract number of floors from prompt"""
    import re

    match = re.search(r"(\d+)\s*floor", prompt.lower())
    if match:
        return int(match.group(1))
    return 3  # Default


def extract_units(prompt):
    """Extract number of units from prompt"""
    import re

    match = re.search(r"(\d+)\s*(bhk|bedroom|unit|cottage|classroom|bed)", prompt.lower())
    if match:
        return int(match.group(1))
    return 1  # Default


if __name__ == "__main__":
    generate_demo_specs()
