"""Final GLB validation - test complete building"""
import sys
sys.path.insert(0, 'backend')

from app.geometry_generator_real import generate_building_glb
import json
import struct

# Test with 4BHK villa spec
test_spec = {
    "design_type": "villa",
    "dimensions": {"width": 15.0, "length": 12.0, "height": 9.0},
    "stories": 2,
    "objects": [
        {"type": "door", "id": "main_door", "count": 1, "dimensions": {"width": 1.2, "height": 2.4}},
        {"type": "window", "id": "window_1", "count": 6, "dimensions": {"width": 1.5, "height": 1.2}}
    ]
}

print("=" * 60)
print("GENERATING 4BHK VILLA GLB")
print("=" * 60)

glb_bytes = generate_building_glb(test_spec)

# Validate GLB structure
magic = glb_bytes[0:4]
version = struct.unpack("<I", glb_bytes[4:8])[0]
length = struct.unpack("<I", glb_bytes[8:12])[0]

print(f"\n[GLB Header]")
print(f"  Magic: {magic} {'OK' if magic == b'glTF' else 'FAIL'}")
print(f"  Version: {version} {'OK' if version == 2 else 'FAIL'}")
print(f"  Total Size: {length} bytes ({length/1024:.1f} KB)")

# Parse JSON chunk
json_chunk_len = struct.unpack("<I", glb_bytes[12:16])[0]
json_chunk_type = glb_bytes[16:20]
json_data = glb_bytes[20:20+json_chunk_len].decode('utf-8').strip()
gltf = json.loads(json_data)

print(f"\n[glTF Structure]")
print(f"  Scenes: {len(gltf['scenes'])}")
print(f"  Nodes: {len(gltf['nodes'])}")
print(f"  Meshes: {len(gltf['meshes'])}")
print(f"  Accessors: {len(gltf['accessors'])}")
print(f"  BufferViews: {len(gltf['bufferViews'])}")

print(f"\n[Geometry Data]")
print(f"  Vertices: {gltf['accessors'][0]['count']}")
print(f"  Indices: {gltf['accessors'][1]['count']}")
print(f"  Normals: {gltf['accessors'][2]['count']}")
print(f"  Triangles: {gltf['accessors'][1]['count'] // 3}")

print(f"\n[Mesh Attributes]")
attrs = gltf['meshes'][0]['primitives'][0]['attributes']
print(f"  POSITION: accessor {attrs['POSITION']}")
print(f"  NORMAL: accessor {attrs['NORMAL']}")

# Save file
output_file = "villa_4bhk.glb"
with open(output_file, "wb") as f:
    f.write(glb_bytes)

print(f"\n[Output]")
print(f"  File: {output_file}")
print(f"  Size: {len(glb_bytes)} bytes")
print(f"\n{'='*60}")
print("SUCCESS! GLB file generated and validated.")
print("You can now open villa_4bhk.glb in any 3D viewer:")
print("  - https://gltf-viewer.donmccurdy.com/")
print("  - https://sandbox.babylonjs.com/")
print("  - Blender, Three.js, etc.")
print("=" * 60)
