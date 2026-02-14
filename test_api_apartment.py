"""Test exact 3BHK apartment spec from API"""
import sys
sys.path.insert(0, 'backend')

from app.geometry_generator_real import generate_real_glb
import struct

# Simulate what the LM would generate for "3BHK apartment with marble flooring and modern kitchen"
test_spec = {
    "design_type": "apartment",
    "dimensions": {
        "width": 12.0,
        "length": 10.0,
        "height": 9.0
    },
    "stories": 1,
    "objects": [
        {"type": "wall", "count": 4},
        {"type": "door", "count": 1},
        {"type": "window", "count": 6},
        {"type": "floor", "material": "marble", "count": 1},
        {"type": "kitchen", "style": "modern", "count": 1}
    ]
}

print("Generating 3BHK apartment (simulating API call)...")
glb_bytes = generate_real_glb(test_spec)

# Parse and check
json_chunk_len = struct.unpack("<I", glb_bytes[12:16])[0]
binary_offset = 20 + json_chunk_len + 8

# Check first 50 vertices
print("\nFirst 50 vertex Z-coordinates:")
z_coords = []
for i in range(min(50, 200)):
    offset = binary_offset + (i * 12) + 8  # +8 to get Z coordinate
    if offset + 4 <= len(glb_bytes):
        z = struct.unpack("<f", glb_bytes[offset:offset+4])[0]
        z_coords.append(z)

print(f"Min Z: {min(z_coords):.2f}")
print(f"Max Z: {max(z_coords):.2f}")
print(f"Z range: {max(z_coords) - min(z_coords):.2f}")

# Save file
with open("api_test_apartment.glb", "wb") as f:
    f.write(glb_bytes)

print(f"\nGenerated {len(glb_bytes)} bytes")
print("Saved to api_test_apartment.glb")

# Check if roof is flat or pitched
if max(z_coords) > 11.0:
    print("\nWARNING: Roof appears to be PITCHED (high Z values)")
    print("Expected max Z around 9.7 for flat roof")
else:
    print("\nOK: Roof appears to be FLAT")
