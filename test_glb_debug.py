"""Debug GLB generation"""
import sys
sys.path.insert(0, 'backend')

from app.geometry_generator_real import generate_building_glb
import struct

# Test spec for 4BHK villa
test_spec = {
    "design_type": "villa",
    "dimensions": {"width": 15.0, "length": 12.0, "height": 9.0},
    "stories": 2,
    "objects": [
        {"type": "door", "id": "main_door", "count": 1, "dimensions": {"width": 1.2, "height": 2.4}},
        {"type": "window", "id": "window_1", "count": 8, "dimensions": {"width": 1.5, "height": 1.2}}
    ]
}

print("Generating GLB...")
try:
    glb_bytes = generate_building_glb(test_spec)
    print(f"[OK] Generated {len(glb_bytes)} bytes")

    # Parse GLB header
    magic = glb_bytes[0:4]
    version = struct.unpack("<I", glb_bytes[4:8])[0]
    length = struct.unpack("<I", glb_bytes[8:12])[0]

    print(f"[OK] Magic: {magic} (should be b'glTF')")
    print(f"[OK] Version: {version} (should be 2)")
    print(f"[OK] Length: {length} bytes")

    # Save to file
    with open("test_output.glb", "wb") as f:
        f.write(glb_bytes)
    print("[OK] Saved to test_output.glb")

    # Check JSON chunk
    json_chunk_len = struct.unpack("<I", glb_bytes[12:16])[0]
    json_chunk_type = glb_bytes[16:20]
    print(f"[OK] JSON chunk: {json_chunk_len} bytes, type: {json_chunk_type}")

    # Parse JSON
    import json
    json_data = glb_bytes[20:20+json_chunk_len].decode('utf-8').strip()
    gltf = json.loads(json_data)
    print(f"[OK] Parsed glTF JSON")
    print(f"  - Vertices: {gltf['accessors'][0]['count']}")
    print(f"  - Indices: {gltf['accessors'][1]['count']}")
    if len(gltf['accessors']) > 2:
        print(f"  - Normals: {gltf['accessors'][2]['count']}")
    print(f"  - Attributes: {gltf['meshes'][0]['primitives'][0]['attributes']}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
