"""
Real 3D Geometry Generator
Converts design specs to actual 3D models
"""
import json
import math
import struct
from typing import Dict, List, Tuple


def calculate_normals(
    vertices: List[Tuple[float, float, float]], faces: List[List[int]]
) -> List[Tuple[float, float, float]]:
    """Calculate vertex normals from faces"""
    # Initialize normals to zero
    normals = [(0.0, 0.0, 0.0) for _ in vertices]

    # Calculate face normals and accumulate to vertices
    for face in faces:
        if len(face) < 3:
            continue

        # Get vertices of triangle
        v0 = vertices[face[0]]
        v1 = vertices[face[1]]
        v2 = vertices[face[2]]

        # Calculate edges
        e1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
        e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])

        # Cross product for face normal
        nx = e1[1] * e2[2] - e1[2] * e2[1]
        ny = e1[2] * e2[0] - e1[0] * e2[2]
        nz = e1[0] * e2[1] - e1[1] * e2[0]

        # Accumulate to each vertex of the face
        for idx in face:
            n = normals[idx]
            normals[idx] = (n[0] + nx, n[1] + ny, n[2] + nz)

    # Normalize all normals
    normalized = []
    for n in normals:
        length = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
        if length > 0:
            normalized.append((n[0] / length, n[1] / length, n[2] / length))
        else:
            normalized.append((0.0, 0.0, 1.0))  # Default up

    return normalized


def generate_building_glb(spec_json: Dict) -> bytes:
    """Generate complete building structure with walls, roof, doors, windows"""
    dimensions = spec_json.get("dimensions", {})
    objects = spec_json.get("objects", [])
    stories = spec_json.get("stories", 1)
    design_type = spec_json.get("design_type", "")

    width = dimensions.get("width", 10.0)
    length = dimensions.get("length", 8.0)
    total_height = dimensions.get("height", 3.0 * stories)
    height = total_height / stories if stories > 1 else total_height

    vertices = []
    faces = []  # Store as list of triangles
    vertex_offset = 0

    # 1. Foundation
    found_verts, found_faces = create_foundation_geometry({"width": width, "length": length, "height": 0.5})
    vertices.extend(found_verts)
    for face in found_faces:
        faces.append([i + vertex_offset for i in face])
    vertex_offset += len(found_verts)

    # 2. Walls (4 walls per story)
    wall_thickness = 0.2
    wall_height = height

    # For row houses, create multiple stories
    for story in range(stories):
        story_z_offset = story * height + 0.5  # Offset by foundation height

        # Front wall (along X axis)
        front_wall_verts, front_wall_faces = create_wall_geometry(
            {"width": width, "height": wall_height, "thickness": wall_thickness}
        )
        front_wall_verts = [(x, y, z + story_z_offset) for x, y, z in front_wall_verts]
        vertices.extend(front_wall_verts)
        for face in front_wall_faces:
            faces.append([i + vertex_offset for i in face])
        vertex_offset += len(front_wall_verts)

        # Back wall (along X axis, offset by length)
        back_wall_verts, back_wall_faces = create_wall_geometry(
            {"width": width, "height": wall_height, "thickness": wall_thickness}
        )
        back_wall_verts = [(x, y + length - wall_thickness, z + story_z_offset) for x, y, z in back_wall_verts]
        vertices.extend(back_wall_verts)
        for face in back_wall_faces:
            faces.append([i + vertex_offset for i in face])
        vertex_offset += len(back_wall_verts)

        # Left wall (along Y axis) - rotated 90 degrees
        left_wall_verts, left_wall_faces = create_wall_geometry(
            {"width": length, "height": wall_height, "thickness": wall_thickness}
        )
        # Rotate: X becomes Y, Y becomes thickness in X direction
        left_wall_verts = [(y, x, z + story_z_offset) for x, y, z in left_wall_verts]
        vertices.extend(left_wall_verts)
        for face in left_wall_faces:
            faces.append([i + vertex_offset for i in face])
        vertex_offset += len(left_wall_verts)

        # Right wall (along Y axis, offset by width) - rotated 90 degrees
        right_wall_verts, right_wall_faces = create_wall_geometry(
            {"width": length, "height": wall_height, "thickness": wall_thickness}
        )
        # Rotate: X becomes Y, Y becomes thickness in X direction, offset by width
        right_wall_verts = [(width - wall_thickness + y, x, z + story_z_offset) for x, y, z in right_wall_verts]
        vertices.extend(right_wall_verts)
        for face in right_wall_faces:
            faces.append([i + vertex_offset for i in face])
        vertex_offset += len(right_wall_verts)

        # Add floor slab for upper stories
        if story > 0:
            floor_verts, floor_faces = create_slab_geometry({"width": width, "length": length, "thickness": 0.15})
            floor_verts = [(x, y, z + story_z_offset) for x, y, z in floor_verts]
            vertices.extend(floor_verts)
            for face in floor_faces:
                faces.append([i + vertex_offset for i in face])
            vertex_offset += len(floor_verts)

    # 3. Roof (at top of all stories)
    # Apartments always have flat roofs
    if design_type.lower() in ["apartment", "flat"]:
        roof_type = "flat"
    else:
        roof_type = (
            "flat"
            if "flat" in design_type.lower() or any("flat_roof" in obj.get("subtype", "") for obj in objects)
            else "pitched"
        )

    roof_verts, roof_faces = create_roof_geometry(
        {"width": width, "length": length, "height": 1.5 if roof_type == "pitched" else 0.2, "roof_type": roof_type}
    )
    roof_z_offset = stories * height + 0.5
    roof_verts = [(x, y, z + roof_z_offset) for x, y, z in roof_verts]
    vertices.extend(roof_verts)
    for face in roof_faces:
        faces.append([i + vertex_offset for i in face])
    vertex_offset += len(roof_verts)

    # 4. Add doors and windows from objects
    window_count = 0
    door_count = 0

    for obj in objects:
        obj_type = obj.get("type", "").lower()
        obj_id = obj.get("id", "").lower()
        count = obj.get("count", 1)

        if "door" in obj_type or "door" in obj_id:
            door_verts, door_faces = create_door_geometry(obj.get("dimensions", {}))
            # Position door at front wall center
            door_verts = [(x + width / 2 - 0.6, y + 0.1, z + 0.5) for x, y, z in door_verts]
            vertices.extend(door_verts)
            for face in door_faces:
                faces.append([i + vertex_offset for i in face])
            vertex_offset += len(door_verts)
            door_count += 1

        elif "window" in obj_type or "window" in obj_id:
            for i in range(count):
                window_verts, window_faces = create_window_geometry(obj.get("dimensions", {}))
                # Distribute windows along front and side walls
                if window_count % 2 == 0:
                    # Front wall windows
                    x_pos = (window_count // 2) * (width / (count + 1)) + 1
                    window_verts = [(x + x_pos, y + 0.1, z + height / 2 + 0.5) for x, y, z in window_verts]
                else:
                    # Side wall windows
                    y_pos = (window_count // 2) * (length / (count + 1)) + 2
                    window_verts = [(x + width - 0.3, y + y_pos, z + height / 2 + 0.5) for x, y, z in window_verts]

                vertices.extend(window_verts)
                for face in window_faces:
                    faces.append([i + vertex_offset for i in face])
                vertex_offset += len(window_verts)
                window_count += 1

    # Count total indices
    total_indices = sum(len(face) for face in faces)

    # Calculate normals for each vertex
    normals = calculate_normals(vertices, faces)

    # Create glTF JSON with normals
    gltf_json = {
        "asset": {"version": "2.0"},
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "NORMAL": 2}, "indices": 1}]}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(vertices), "type": "VEC3"},
            {"bufferView": 1, "componentType": 5123, "count": total_indices, "type": "SCALAR"},
            {"bufferView": 2, "componentType": 5126, "count": len(normals), "type": "VEC3"},
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(vertices) * 12},
            {"buffer": 0, "byteOffset": len(vertices) * 12, "byteLength": total_indices * 2},
            {"buffer": 0, "byteOffset": len(vertices) * 12 + total_indices * 2, "byteLength": len(normals) * 12},
        ],
        "buffers": [{"byteLength": len(vertices) * 12 + total_indices * 2 + len(normals) * 12}],
    }

    json_data = json.dumps(gltf_json).encode("utf-8")

    # Pack vertex data
    vertex_data = b""
    for vertex in vertices:
        vertex_data += struct.pack("<fff", vertex[0], vertex[1], vertex[2])

    # Pack index data - faces is list of triangles
    index_data = b""
    for face in faces:
        for idx in face:
            if idx >= len(vertices):
                raise ValueError(f"Index {idx} out of range for {len(vertices)} vertices")
            index_data += struct.pack("<H", idx)

    # Pack normal data
    normal_data = b""
    for normal in normals:
        normal_data += struct.pack("<fff", normal[0], normal[1], normal[2])

    binary_data = vertex_data + index_data + normal_data
    return create_glb_file(json_data, binary_data)


def generate_real_glb(spec_json: Dict) -> bytes:
    """Generate real GLB file with actual geometry"""

    # Extract objects from spec
    objects = spec_json.get("objects", [])
    design_type = spec_json.get("design_type", "")
    dimensions = spec_json.get("dimensions", {})

    # If it's a building/house, create a complete structure
    if design_type in [
        "house",
        "building",
        "apartment",
        "villa",
        "bungalow",
        "row_house",
        "townhouse",
        "duplex",
        "penthouse",
    ]:
        return generate_building_glb(spec_json)

    # Generate vertices and faces for each object
    vertices = []
    indices = []
    vertex_offset = 0

    for obj in objects:
        obj_vertices, obj_indices = create_object_geometry(obj)

        # Add vertices
        vertices.extend(obj_vertices)

        # Add indices with offset
        for idx in obj_indices:
            indices.extend([i + vertex_offset for i in idx])

        vertex_offset += len(obj_vertices)

    # Fallback: if no vertices, create a simple box
    if not vertices:
        vertices, indices = create_box_geometry(dimensions or {"width": 10, "depth": 8, "height": 3})

    # Create glTF JSON
    gltf_json = {
        "asset": {"version": "2.0"},
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(vertices), "type": "VEC3"},  # FLOAT
            {"bufferView": 1, "componentType": 5123, "count": len(indices), "type": "SCALAR"},  # UNSIGNED_SHORT
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(vertices) * 12},  # 3 floats * 4 bytes
            {"buffer": 0, "byteOffset": len(vertices) * 12, "byteLength": len(indices) * 2},  # 1 short * 2 bytes
        ],
        "buffers": [{"byteLength": len(vertices) * 12 + len(indices) * 2}],
    }

    # Convert to binary
    json_data = json.dumps(gltf_json).encode("utf-8")

    # Pack vertex data
    vertex_data = b""
    for vertex in vertices:
        vertex_data += struct.pack("<fff", vertex[0], vertex[1], vertex[2])

    # Pack index data - indices is list of faces (triangles)
    index_data = b""
    total_indices = 0
    for face in indices:
        for idx in face:
            if idx >= len(vertices):
                raise ValueError(f"Index {idx} out of range for {len(vertices)} vertices")
            index_data += struct.pack("<H", idx)
            total_indices += 1

    # Update accessor count
    gltf_json["accessors"][1]["count"] = total_indices
    gltf_json["bufferViews"][1]["byteLength"] = total_indices * 2
    gltf_json["buffers"][0]["byteLength"] = len(vertices) * 12 + total_indices * 2

    # Re-encode JSON with updated counts
    json_data = json.dumps(gltf_json).encode("utf-8")

    binary_data = vertex_data + index_data

    # Create GLB
    return create_glb_file(json_data, binary_data)


def create_object_geometry(obj: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    """Create 3D geometry for any design object"""

    obj_type = obj.get("type", "")
    obj_id = obj.get("id", "")
    dimensions = obj.get("dimensions", {})

    # Check both type and id for better matching
    obj_lower = (obj_type + " " + obj_id).lower()

    # Kitchen objects
    if "cabinet" in obj_lower:
        return create_cabinet_geometry(dimensions)
    elif "countertop" in obj_lower or "counter" in obj_lower:
        return create_countertop_geometry(dimensions)
    elif "island" in obj_lower:
        return create_island_geometry(dimensions)
    elif "floor" in obj_lower or "flooring" in obj_lower:
        return create_floor_geometry(dimensions)

    # Building/Architecture objects
    elif "wall" in obj_lower:
        return create_wall_geometry(dimensions)
    elif "door" in obj_lower:
        return create_door_geometry(dimensions)
    elif "window" in obj_lower:
        return create_window_geometry(dimensions)
    elif "roof" in obj_lower:
        return create_roof_geometry(dimensions)
    elif "foundation" in obj_lower:
        return create_foundation_geometry(dimensions)
    elif "column" in obj_lower or "pillar" in obj_lower:
        return create_column_geometry(dimensions)
    elif "beam" in obj_lower:
        return create_beam_geometry(dimensions)
    elif "slab" in obj_lower:
        return create_slab_geometry(dimensions)
    elif "stair" in obj_lower:
        return create_staircase_geometry(dimensions)
    elif "balcony" in obj_lower:
        return create_balcony_geometry(dimensions)

    # Room/Interior objects
    elif obj_type == "bed":
        return create_bed_geometry(dimensions)
    elif obj_type == "sofa":
        return create_sofa_geometry(dimensions)
    elif obj_type == "table":
        return create_table_geometry(dimensions)
    elif obj_type == "chair":
        return create_chair_geometry(dimensions)
    elif obj_type == "wardrobe":
        return create_wardrobe_geometry(dimensions)
    elif obj_type == "tv_unit":
        return create_tv_unit_geometry(dimensions)
    elif obj_type == "bookshelf":
        return create_bookshelf_geometry(dimensions)

    # Automotive objects
    elif obj_type == "car_body":
        return create_car_body_geometry(dimensions)
    elif obj_type == "wheel":
        return create_wheel_geometry(dimensions)
    elif obj_type == "engine":
        return create_engine_geometry(dimensions)
    elif obj_type == "chassis":
        return create_chassis_geometry(dimensions)

    # Electronics objects
    elif obj_type == "pcb":
        return create_pcb_geometry(dimensions)
    elif obj_type == "component":
        return create_component_geometry(dimensions)
    elif obj_type == "housing":
        return create_housing_geometry(dimensions)
    elif obj_type == "screen":
        return create_screen_geometry(dimensions)

    else:
        return create_box_geometry(dimensions)


def create_cabinet_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    """Create cabinet box geometry"""
    w = dims.get("width", 1.0)
    d = dims.get("depth", 0.6)
    h = dims.get("height", 0.9)

    # Cabinet vertices (box)
    vertices = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]  # Bottom  # Top

    # Cabinet faces
    faces = [
        [0, 1, 2],
        [0, 2, 3],  # Bottom
        [4, 7, 6],
        [4, 6, 5],  # Top
        [0, 4, 5],
        [0, 5, 1],  # Front
        [2, 6, 7],
        [2, 7, 3],  # Back
        [0, 3, 7],
        [0, 7, 4],  # Left
        [1, 5, 6],
        [1, 6, 2],  # Right
    ]

    return vertices, faces


def create_countertop_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    """Create countertop slab geometry"""
    w = dims.get("width", 2.0)
    d = dims.get("depth", 0.6)
    h = dims.get("height", 0.05)

    # Thin slab
    vertices = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]

    faces = [
        [0, 1, 2],
        [0, 2, 3],  # Bottom
        [4, 7, 6],
        [4, 6, 5],  # Top
        [0, 4, 5],
        [0, 5, 1],  # Front
        [2, 6, 7],
        [2, 7, 3],  # Back
        [0, 3, 7],
        [0, 7, 4],  # Left
        [1, 5, 6],
        [1, 6, 2],  # Right
    ]

    return vertices, faces


def create_island_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    """Create kitchen island geometry"""
    w = dims.get("width", 2.4)
    d = dims.get("depth", 1.2)
    h = dims.get("height", 0.9)

    vertices = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]

    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]

    return vertices, faces


def create_floor_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    """Create floor plane geometry"""
    w = dims.get("width", 3.6)
    l = dims.get("length", 3.0)

    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0)]

    faces = [[0, 1, 2], [0, 2, 3]]

    return vertices, faces


# ============================================================================
# BUILDING/ARCHITECTURE GEOMETRY
# ============================================================================


def create_wall_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 3.0)
    h = dims.get("height", 2.7)
    t = dims.get("thickness", 0.2)

    vertices = [(0, 0, 0), (w, 0, 0), (w, t, 0), (0, t, 0), (0, 0, h), (w, 0, h), (w, t, h), (0, t, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_door_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 0.9)
    h = dims.get("height", 2.1)
    t = dims.get("thickness", 0.05)

    vertices = [(0, 0, 0), (w, 0, 0), (w, t, 0), (0, t, 0), (0, 0, h), (w, 0, h), (w, t, h), (0, t, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_window_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 1.2)
    h = dims.get("height", 1.0)
    t = dims.get("thickness", 0.1)

    # Frame geometry
    vertices = [(0, 0, 0), (w, 0, 0), (w, t, 0), (0, t, 0), (0, 0, h), (w, 0, h), (w, t, h), (0, t, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_roof_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 10.0)
    l = dims.get("length", 8.0)
    h = dims.get("height", 2.0)
    roof_type = dims.get("roof_type", "pitched")

    if roof_type == "flat":
        # Flat roof with slight slope
        vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (0, 0, 0.2), (w, 0, 0.2), (w, l, 0.3), (0, l, 0.3)]
        faces = [
            [0, 1, 2],
            [0, 2, 3],
            [4, 7, 6],
            [4, 6, 5],
            [0, 4, 5],
            [0, 5, 1],
            [2, 6, 7],
            [2, 7, 3],
            [0, 3, 7],
            [0, 7, 4],
            [1, 5, 6],
            [1, 6, 2],
        ]
    else:
        # Pitched/gable roof
        peak_h = h
        vertices = [
            (0, 0, 0),
            (w, 0, 0),
            (w, l, 0),
            (0, l, 0),  # Base corners
            (w / 2, 0, peak_h),
            (w / 2, l, peak_h),  # Peak points
        ]
        faces = [
            [0, 1, 4],  # Front left slope
            [1, 2, 5],
            [1, 5, 4],  # Right slope
            [2, 3, 5],  # Back left slope
            [3, 0, 4],
            [3, 4, 5],  # Left slope
            [0, 3, 2],
            [0, 2, 1],  # Base
        ]
    return vertices, faces


def create_foundation_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 10.0)
    l = dims.get("length", 8.0)
    h = dims.get("height", 0.5)

    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (0, 0, h), (w, 0, h), (w, l, h), (0, l, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_column_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 0.3)
    d = dims.get("depth", 0.3)
    h = dims.get("height", 3.0)

    vertices = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_beam_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 0.3)
    l = dims.get("length", 5.0)
    h = dims.get("height", 0.4)

    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (0, 0, h), (w, 0, h), (w, l, h), (0, l, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_slab_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 10.0)
    l = dims.get("length", 8.0)
    h = dims.get("thickness", 0.15)

    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (0, 0, h), (w, 0, h), (w, l, h), (0, l, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_staircase_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 1.2)
    l = dims.get("length", 3.0)
    h = dims.get("height", 2.7)
    steps = dims.get("steps", 15)

    vertices = []
    faces = []
    step_h = h / steps
    step_l = l / steps
    step_thickness = 0.05

    for i in range(steps):
        z = i * step_h
        y = i * step_l

        # Create each step with proper tread and riser
        step_verts = [
            # Bottom of step
            (0, y, z),
            (w, y, z),
            (w, y + step_l, z),
            (0, y + step_l, z),
            # Top of step
            (0, y, z + step_h),
            (w, y, z + step_h),
            (w, y + step_l, z + step_h),
            (0, y + step_l, z + step_h),
        ]

        base = len(vertices)
        vertices.extend(step_verts)

        # Create faces for each step
        faces.extend(
            [
                [base, base + 1, base + 2],
                [base, base + 2, base + 3],  # Bottom
                [base + 4, base + 7, base + 6],
                [base + 4, base + 6, base + 5],  # Top (tread)
                [base, base + 4, base + 5],
                [base, base + 5, base + 1],  # Front (riser)
                [base + 2, base + 6, base + 7],
                [base + 2, base + 7, base + 3],  # Back
                [base, base + 3, base + 7],
                [base, base + 7, base + 4],  # Left
                [base + 1, base + 5, base + 6],
                [base + 1, base + 6, base + 2],  # Right
            ]
        )

    return vertices, faces


def create_balcony_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 3.0)
    d = dims.get("depth", 1.5)
    h = dims.get("height", 0.1)

    vertices = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


# ============================================================================
# FURNITURE/INTERIOR GEOMETRY
# ============================================================================


def create_bed_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 1.8)
    l = dims.get("length", 2.0)
    h = dims.get("height", 0.6)

    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (0, 0, h), (w, 0, h), (w, l, h), (0, l, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_sofa_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 2.0)
    d = dims.get("depth", 0.9)
    h = dims.get("height", 0.8)

    vertices = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_table_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 1.5)
    l = dims.get("length", 0.8)
    h = dims.get("height", 0.75)

    # Table top + legs
    vertices = [
        (0, 0, h - 0.05),
        (w, 0, h - 0.05),
        (w, l, h - 0.05),
        (0, l, h - 0.05),
        (0, 0, h),
        (w, 0, h),
        (w, l, h),
        (0, l, h),
    ]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_chair_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 0.5)
    d = dims.get("depth", 0.5)
    h = dims.get("height", 0.8)

    vertices = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_wardrobe_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 2.0)
    d = dims.get("depth", 0.6)
    h = dims.get("height", 2.2)

    vertices = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_tv_unit_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 1.8)
    d = dims.get("depth", 0.4)
    h = dims.get("height", 0.6)

    vertices = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_bookshelf_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 1.2)
    d = dims.get("depth", 0.3)
    h = dims.get("height", 2.0)

    vertices = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


# ============================================================================
# AUTOMOTIVE GEOMETRY
# ============================================================================


def create_car_body_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 1.8)
    l = dims.get("length", 4.5)
    h = dims.get("height", 1.5)

    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (0, 0, h), (w, 0, h), (w, l, h), (0, l, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_wheel_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    r = dims.get("radius", 0.3)
    w = dims.get("width", 0.2)

    # Simplified cylinder
    vertices = [
        (0, 0, 0),
        (r, 0, 0),
        (0, r, 0),
        (-r, 0, 0),
        (0, -r, 0),
        (0, 0, w),
        (r, 0, w),
        (0, r, w),
        (-r, 0, w),
        (0, -r, w),
    ]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [0, 3, 4],
        [0, 4, 1],
        [5, 7, 6],
        [5, 8, 7],
        [5, 9, 8],
        [5, 6, 9],
        [1, 6, 7],
        [1, 7, 2],
        [2, 7, 8],
        [2, 8, 3],
        [3, 8, 9],
        [3, 9, 4],
        [4, 9, 6],
        [4, 6, 1],
    ]
    return vertices, faces


def create_engine_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 0.8)
    l = dims.get("length", 1.0)
    h = dims.get("height", 0.6)

    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (0, 0, h), (w, 0, h), (w, l, h), (0, l, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_chassis_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 1.6)
    l = dims.get("length", 4.0)
    h = dims.get("height", 0.2)

    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (0, 0, h), (w, 0, h), (w, l, h), (0, l, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


# ============================================================================
# ELECTRONICS GEOMETRY
# ============================================================================


def create_pcb_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 0.1)
    l = dims.get("length", 0.08)
    h = dims.get("thickness", 0.002)

    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (0, 0, h), (w, 0, h), (w, l, h), (0, l, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_component_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 0.01)
    l = dims.get("length", 0.01)
    h = dims.get("height", 0.005)

    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (0, 0, h), (w, 0, h), (w, l, h), (0, l, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_housing_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 0.15)
    l = dims.get("length", 0.1)
    h = dims.get("height", 0.05)

    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (0, 0, h), (w, 0, h), (w, l, h), (0, l, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_screen_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    w = dims.get("width", 0.3)
    h = dims.get("height", 0.2)
    t = dims.get("thickness", 0.005)

    vertices = [(0, 0, 0), (w, 0, 0), (w, t, 0), (0, t, 0), (0, 0, h), (w, 0, h), (w, t, h), (0, t, h)]
    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    return vertices, faces


def create_box_geometry(dims: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    """Create generic box geometry"""
    w = dims.get("width", 1.0)
    d = dims.get("depth", 1.0)
    h = dims.get("height", 1.0)

    vertices = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]

    faces = [
        [0, 1, 2],
        [0, 2, 3],
        [4, 7, 6],
        [4, 6, 5],
        [0, 4, 5],
        [0, 5, 1],
        [2, 6, 7],
        [2, 7, 3],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]

    return vertices, faces


def create_glb_file(json_data: bytes, binary_data: bytes) -> bytes:
    """Create GLB file from JSON and binary data"""

    # GLB header
    magic = b"glTF"
    version = struct.pack("<I", 2)

    # JSON chunk
    json_length = len(json_data)
    json_padding = (4 - (json_length % 4)) % 4
    json_data += b" " * json_padding
    json_chunk_length = struct.pack("<I", len(json_data))
    json_chunk_type = b"JSON"

    # Binary chunk
    binary_length = len(binary_data)
    binary_padding = (4 - (binary_length % 4)) % 4
    binary_data += b"\x00" * binary_padding
    binary_chunk_length = struct.pack("<I", len(binary_data))
    binary_chunk_type = b"BIN\x00"

    # Total length
    total_length = struct.pack("<I", 12 + 8 + len(json_data) + 8 + len(binary_data))

    # Assemble GLB
    glb = (
        magic
        + version
        + total_length
        + json_chunk_length
        + json_chunk_type
        + json_data
        + binary_chunk_length
        + binary_chunk_type
        + binary_data
    )

    return glb
