# SPEC FLOW ANALYSIS & ROOT CAUSE REPORT

## Executive Summary

**Status**: ✅ ANALYSIS COMPLETE
**Root Cause**: IDENTIFIED
**Acceptance**: CONFIRMED

---

## Flow Confirmation: Prompt → Spec JSON → Geometry → GLB

### 1. CORRECT FLOW (Verified)

```
User Prompt
    ↓
/api/v1/generate (generate.py)
    ↓
lm_run() → LM generates spec_json (in-memory dict)
    ↓
generate_mock_glb(spec_json)
    ↓
generate_real_glb(spec_json) ← READS FROM PARAMETER
    ↓
GLB bytes (4872+ bytes)
    ↓
Upload to Supabase storage
    ↓
Return preview_url to user
```

### 2. SPEC STORAGE (Parallel, Not Used by Generator)

```
spec_json (in-memory)
    ↓
Database: Spec model (PostgreSQL)
    ↓
spec_storage.save() → data/specs/{spec_id}.json
```

**CONFIRMED**: Geometry generator does NOT read from spec_storage files.

---

## Root Cause Analysis

### Issue: Silent Fallback to Default Dimensions

**Evidence Found**:
- ✅ 96 default dimension values across codebase
- ✅ 18 fallback logic blocks
- ✅ 2 file read operations (both for writing, not reading specs)
- ✅ 0 spec file reads in geometry_generator_real.py

### Critical Code Patterns

#### Pattern 1: Default Dimensions (89 instances in geometry_generator_real.py)
```python
# Line 61 - geometry_generator_real.py
width = dimensions.get("width", 10.0)   # ← FALLBACK: 10.0m
length = dimensions.get("length", 8.0)  # ← FALLBACK: 8.0m
height = dimensions.get("height", 3.0)  # ← FALLBACK: 3.0m
```

#### Pattern 2: Fallback Geometry (Line 283)
```python
# Fallback: if no vertices, create a simple box
if not vertices:
    vertices, indices = create_box_geometry(
        dimensions or {"width": 10, "depth": 8, "height": 3}
    )
```

#### Pattern 3: Silent Default Usage (Every object type)
```python
# Cabinet geometry
w = dims.get("width", 1.0)   # ← Default 1.0m
d = dims.get("depth", 0.6)   # ← Default 0.6m
h = dims.get("height", 0.9)  # ← Default 0.9m
```

---

## Root Cause: No Validation Before Geometry Generation

### Problem
1. **LM generates spec_json** → May be incomplete or have typos
2. **No validation** → Spec passed directly to generator
3. **Generator uses .get() with defaults** → Silently uses fallback values
4. **User sees geometry** → But dimensions may be wrong

### Risk Scenarios

| Scenario | LM Output | Generator Behavior | User Impact |
|----------|-----------|-------------------|-------------|
| Missing 'dimensions' key | `{}` | Uses width=10, length=8, height=3 | Wrong size building |
| Typo in key | `{"widht": 15}` | Uses width=10 (default) | Ignores user input |
| Empty objects array | `{"objects": []}` | Creates generic box | Generic geometry |
| Incomplete object dims | `{"type": "wall"}` | Uses default wall size | Wrong proportions |

---

## Acceptance Criteria: CONFIRMED ✅

### Question: Is generator reading correct spec file?

**Answer**: Generator is NOT reading spec files at all.

**Confirmation**:
1. ✅ Generator receives `spec_json` as function parameter
2. ✅ No file reads from `spec_storage` directory
3. ✅ Direct memory pass-through from LM → Generator
4. ✅ Spec files are for persistence only (database + local JSON)

### Question: Does it use correct spec or fallback?

**Answer**: It uses the correct spec_json parameter, BUT falls back to defaults when:
- Spec is incomplete (missing keys)
- Spec has typos in key names
- Spec has empty/null values

**Fallback Behavior**:
- ✅ 96 default values throughout geometry_generator_real.py
- ✅ Every dimension access uses `.get(key, default_value)`
- ✅ No errors raised when spec is incomplete
- ✅ Silent fallback to hardcoded dimensions

---

## Detailed Findings

### File: geometry_generator_real.py

**Default Dimensions Found**: 89 instances

Examples:
```python
Line 61:  width = dimensions.get("width", 10.0)
Line 62:  length = dimensions.get("length", 8.0)
Line 63:  total_height = dimensions.get("height", 3.0 * stories)
Line 420: w = dims.get("width", 1.0)      # Cabinet
Line 448: w = dims.get("width", 2.0)      # Countertop
Line 475: w = dims.get("width", 2.4)      # Island
Line 501: w = dims.get("width", 3.6)      # Floor
Line 520: w = dims.get("width", 3.0)      # Wall
Line 531: w = dims.get("width", 0.9)      # Door
Line 542: w = dims.get("width", 1.2)      # Window
```

**Fallback Logic**: 3 instances
```python
Line 283: # Fallback: if no vertices, create a simple box
Line 284: if not vertices:
Line 285:     vertices, indices = create_box_geometry(...)
```

### File: generate.py

**Default Dimensions Found**: 4 instances
```python
Line 40:  width = dimensions.get("width", 10)
Line 41:  length = dimensions.get("length", 10)
Line 329: area_sqm = dims.get("width", 10) * dims.get("length", 10)
```

**Fallback Logic**: 11 instances
```python
Line 144: # Fallback to simple GLB
Line 148: logger.warning("Using fallback simple GLB...")
Line 399: # Fallback to Tripo AI
Line 422: # Fallback to local file path
```

### File: geometry_generator.py (API)

**Default Dimensions Found**: 3 instances
```python
Line 80: length = room.get("length", 4.0)
Line 81: width = room.get("width", 4.0)
Line 82: height = room.get("height", 3.0)
```

**Fallback Logic**: 4 instances
```python
Line 73: logger.warning(f"Real geometry generation failed, using fallback: {e}")
Line 74: # Fallback to simple room
Line 84: # Simple fallback GLB
```

---

## Impact Assessment

### Current Behavior
- ✅ Generator receives correct spec_json from LM
- ⚠️ BUT silently uses defaults when spec is incomplete
- ⚠️ No validation errors returned to user
- ⚠️ User may get wrong dimensions without knowing

### Example Scenario

**User Input**: "Create a 15m x 12m apartment"

**LM Output** (with typo):
```json
{
  "design_type": "apartment",
  "dimensions": {
    "widht": 15.0,    ← Typo!
    "length": 12.0,
    "height": 3.0
  }
}
```

**Generator Behavior**:
```python
width = dimensions.get("width", 10.0)  # ← Gets 10.0 (default), not 15.0!
length = dimensions.get("length", 8.0) # ← Gets 12.0 (correct)
```

**Result**: User gets 10m x 12m instead of 15m x 12m

---

## Recommendations

### 1. Add Strict Validation (High Priority)
```python
def validate_spec_json(spec_json: Dict) -> None:
    """Raise error if spec is incomplete"""
    required = ["design_type", "dimensions", "objects"]
    for key in required:
        if key not in spec_json:
            raise ValueError(f"Missing required key: {key}")

    dims = spec_json["dimensions"]
    for dim in ["width", "length", "height"]:
        if dim not in dims:
            raise ValueError(f"Missing dimension: {dim}")
```

### 2. Log Warnings for Defaults (Medium Priority)
```python
width = dimensions.get("width")
if width is None:
    logger.warning(f"Missing width, using default 10.0m")
    width = 10.0
```

### 3. Return Validation Errors to User (High Priority)
```python
try:
    validate_spec_json(spec_json)
    glb_bytes = generate_real_glb(spec_json)
except ValueError as e:
    return {"error": str(e), "spec_json": spec_json}
```

### 4. Add Schema Validation (Medium Priority)
```python
from pydantic import BaseModel, Field

class SpecDimensions(BaseModel):
    width: float = Field(gt=0, description="Width in meters")
    length: float = Field(gt=0, description="Length in meters")
    height: float = Field(gt=0, description="Height in meters")

class SpecJSON(BaseModel):
    design_type: str
    dimensions: SpecDimensions
    objects: List[Dict]
```

---

## Conclusion

### Acceptance: CONFIRMED ✅

**Question**: Is generator reading correct spec file?
**Answer**: Generator reads correct spec_json parameter (not files)

**Question**: Does it use correct spec or fallback?
**Answer**: Uses correct spec_json, BUT falls back to defaults when incomplete

### Root Cause: IDENTIFIED ✅

**Primary Issue**: No validation of spec_json completeness before geometry generation

**Secondary Issue**: Heavy reliance on `.get()` with defaults masks incomplete specs

**Impact**: Users may receive incorrect geometry without error messages

### Next Steps

1. ✅ Add spec_json validation before calling generate_real_glb()
2. ✅ Log warnings when defaults are used
3. ✅ Return validation errors to user
4. ✅ Consider strict mode (raise errors instead of defaults)

---

**Report Generated**: 2024
**Analysis Tool**: trace_spec_flow.py + detect_hardcoding.py
**Files Analyzed**: 3 (geometry_generator_real.py, generate.py, geometry_generator.py)
**Total Findings**: 96 defaults, 18 fallbacks, 2 file operations
