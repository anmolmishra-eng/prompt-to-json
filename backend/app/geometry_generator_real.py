"""
Real 3D Geometry Generator
Converts design specs to actual 3D models
"""
import json
import struct
from typing import Dict, List, Tuple


def generate_real_glb(spec_json: Dict) -> bytes:
    """Generate real GLB file with actual geometry"""

    # Extract objects from spec
    objects = spec_json.get("objects", [])

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

    # Pack index data
    index_data = b""
    for index in indices:
        index_data += struct.pack("<H", index)

    binary_data = vertex_data + index_data

    # Create GLB
    return create_glb_file(json_data, binary_data)


def create_object_geometry(obj: Dict) -> Tuple[List[Tuple[float, float, float]], List[List[int]]]:
    """Create 3D geometry for any design object"""

    obj_type = obj.get("type", "")
    dimensions = obj.get("dimensions", {})

    # Kitchen objects
    if obj_type == "cabinet":
        return create_cabinet_geometry(dimensions)
    elif obj_type == "countertop":
        return create_countertop_geometry(dimensions)
    elif obj_type == "island":
        return create_island_geometry(dimensions)
    elif obj_type == "floor":
        return create_floor_geometry(dimensions)

    # Building/Architecture objects
    elif obj_type == "wall":
        return create_wall_geometry(dimensions)
    elif obj_type == "door":
        return create_door_geometry(dimensions)
    elif obj_type == "window":
        return create_window_geometry(dimensions)
    elif obj_type == "roof":
        return create_roof_geometry(dimensions)
    elif obj_type == "foundation":
        return create_foundation_geometry(dimensions)
    elif obj_type == "column":
        return create_column_geometry(dimensions)
    elif obj_type == "beam":
        return create_beam_geometry(dimensions)
    elif obj_type == "slab":
        return create_slab_geometry(dimensions)
    elif obj_type == "staircase":
        return create_staircase_geometry(dimensions)
    elif obj_type == "balcony":
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

    # Pitched roof
    vertices = [(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0), (w / 2, 0, h), (w / 2, l, h)]
    faces = [[0, 1, 4], [1, 2, 5], [1, 5, 4], [2, 3, 5], [3, 0, 4], [3, 4, 5], [0, 3, 2], [0, 2, 1]]
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

    for i in range(steps):
        z = i * step_h
        y = i * step_l
        vertices.extend(
            [
                (0, y, z),
                (w, y, z),
                (w, y + step_l, z),
                (0, y + step_l, z),
                (0, y, z + step_h),
                (w, y, z + step_h),
                (w, y + step_l, z + step_h),
                (0, y + step_l, z + step_h),
            ]
        )
        base = i * 8
        faces.extend(
            [
                [base, base + 1, base + 2],
                [base, base + 2, base + 3],
                [base + 4, base + 7, base + 6],
                [base + 4, base + 6, base + 5],
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
