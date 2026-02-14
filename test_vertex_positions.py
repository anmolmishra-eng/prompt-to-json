"""Analyze vertex positions in generated GLB"""
import sys
sys.path.insert(0, 'backend')

from app.geometry_generator_real import generate_building_glb
import struct

test_spec = {
    "design_type": "villa",
    "dimensions": {"width": 15.0, "length": 12.0, "height": 9.0},
    "stories": 2,
    "objects": []
}

print("Generating GLB...")
glb_bytes = generate_building_glb(test_spec)

# Parse to get binary data offset
json_chunk_len = struct.unpack("<I", glb_bytes[12:16])[0]
binary_offset = 20 + json_chunk_len + 8  # header + json + binary chunk header

# Read first 20 vertices
print("\nFirst 20 vertices (X, Y, Z):")
for i in range(20):
    offset = binary_offset + (i * 12)
    x, y, z = struct.unpack("<fff", glb_bytes[offset:offset+12])
    print(f"  V{i:3d}: ({x:7.2f}, {y:7.2f}, {z:7.2f})")

print("\nExpected structure:")
print("  Foundation: 8 vertices at Z=0 to Z=0.5")
print("  Front wall: 8 vertices along X-axis (Y=0)")
print("  Back wall: 8 vertices along X-axis (Y=12)")
print("  Left wall: 8 vertices along Y-axis (X=0)")
print("  Right wall: 8 vertices along Y-axis (X=15)")
