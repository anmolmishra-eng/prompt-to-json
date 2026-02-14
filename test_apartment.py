"""Test 3BHK apartment generation"""
import sys
sys.path.insert(0, 'backend')

from app.geometry_generator_real import generate_building_glb

test_spec = {
    "design_type": "apartment",
    "dimensions": {"width": 12.0, "length": 10.0, "height": 9.0},
    "stories": 1,
    "objects": [
        {"type": "door", "count": 1},
        {"type": "window", "count": 4}
    ]
}

print("Generating 3BHK apartment GLB...")
glb_bytes = generate_building_glb(test_spec)

with open("apartment_3bhk.glb", "wb") as f:
    f.write(glb_bytes)

print(f"Generated {len(glb_bytes)} bytes")
print("Saved to apartment_3bhk.glb")
print("\nThe building should have:")
print("  - Flat foundation at Z=0 to Z=0.5")
print("  - Walls from Z=0.5 to Z=9.5")
print("  - FLAT roof at Z=9.5 to Z=9.7")
print("\nView from TOP to see the flat roof")
print("View from SIDE to see the building profile")
