"""Verify all wall positions"""
import sys
sys.path.insert(0, 'backend')

from app.geometry_generator_real import generate_building_glb
import struct

test_spec = {
    "design_type": "villa",
    "dimensions": {"width": 15.0, "length": 12.0, "height": 9.0},
    "stories": 1,  # Single story for easier analysis
    "objects": []
}

print("Generating GLB...")
glb_bytes = generate_building_glb(test_spec)

# Parse to get binary data offset
json_chunk_len = struct.unpack("<I", glb_bytes[12:16])[0]
binary_offset = 20 + json_chunk_len + 8

# Read vertices
vertices = []
for i in range(50):  # Read first 50 vertices
    offset = binary_offset + (i * 12)
    x, y, z = struct.unpack("<fff", glb_bytes[offset:offset+12])
    vertices.append((x, y, z))

print("\nFoundation (vertices 0-7):")
for i in range(8):
    print(f"  V{i}: {vertices[i]}")

print("\nFront Wall (vertices 8-15) - should be along X-axis at Y=0:")
for i in range(8, 16):
    print(f"  V{i}: {vertices[i]}")

print("\nBack Wall (vertices 16-23) - should be along X-axis at Y~12:")
for i in range(16, 24):
    print(f"  V{i}: {vertices[i]}")

print("\nLeft Wall (vertices 24-31) - should be along Y-axis at X=0:")
for i in range(24, 32):
    print(f"  V{i}: {vertices[i]}")

print("\nRight Wall (vertices 32-39) - should be along Y-axis at X~15:")
for i in range(32, 40):
    print(f"  V{i}: {vertices[i]}")
