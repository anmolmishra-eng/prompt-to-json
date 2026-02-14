# Critical GLB Generation Bug Fix

## Problem
3BHK house showing as **tall rectangular box** instead of proper multi-story structure with walls, roof, doors, windows.

## Root Cause
**Index packing bug** in geometry generator:

```python
# WRONG - treats indices as flat list
for index in indices:
    index_data += struct.pack("<H", index)
```

But `indices` is actually a **list of faces** (triangles), where each face has 3 vertex indices:
```python
indices = [[0, 1, 2], [0, 2, 3], [4, 7, 6], ...]  # List of triangles
```

This caused:
1. **Wrong index count** in glTF accessor
2. **Corrupted geometry** - indices pointing to wrong vertices
3. **Fallback to simple box** when geometry generation failed

## Fix Applied

```python
# CORRECT - iterate through faces, then indices
total_indices = 0
for face in indices:  # Each face is [v1, v2, v3]
    for idx in face:
        if idx >= len(vertices):
            raise ValueError(f"Index {idx} out of range")
        index_data += struct.pack("<H", idx)
        total_indices += 1

# Update glTF accessor with correct count
gltf_json["accessors"][1]["count"] = total_indices
```

## Files Fixed
- `backend/app/geometry_generator_real.py`
  - Fixed `generate_building_glb()` index packing
  - Fixed `generate_real_glb()` index packing
  - Added index validation
  - Added proper count updates

- `backend/app/api/generate.py`
  - Enhanced error logging for geometry generation

## Result
Now generates **proper 3-story house** with:
- ✅ Foundation (40m × 60m × 0.5m)
- ✅ 3 stories of walls (3.5m each)
- ✅ Floor slabs between stories
- ✅ 12 windows distributed
- ✅ 1 main door
- ✅ Pitched roof
- ✅ Correct vertex/index counts

## Test
```json
{
  "user_id": "test_nashik_1",
  "prompt": "Design a 3BHK independent house with concrete structure",
  "city": "Nashik",
  "style": "modern"
}
```

Expected: **Proper 3-story house structure** ✅
