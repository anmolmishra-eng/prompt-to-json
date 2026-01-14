# Fix for GET /api/v1/reports/{spec_id} 404 Error

## Problem Analysis

The error occurred because:
```
GET /api/v1/reports/spec_test123 → 404 "Spec not found"
```

The endpoint was returning a generic 404 error without helpful information about:
- Why the spec wasn't found
- What specs are actually available
- How to fix the issue

## Solution Implemented

Updated `backend/app/api/reports.py` to provide detailed error responses:

### Before:
```python
if not spec:
    raise HTTPException(status_code=404, detail="Spec not found")
```

### After:
```python
if not spec:
    # Get available specs for helpful error message
    available_specs = db.query(Spec.id).limit(5).all()
    available_ids = [s.id for s in available_specs]

    error_detail = {
        "error": "Spec not found",
        "requested_spec_id": spec_id,
        "message": f"The spec '{spec_id}' does not exist in the database.",
        "available_specs": available_ids,
        "hint": "Use one of the available spec IDs or create a new design using POST /api/v1/generate"
    }
    raise HTTPException(status_code=404, detail=error_detail)
```

## New Error Response Format

When requesting a non-existent spec, you now get:

```json
{
  "detail": {
    "error": "Spec not found",
    "requested_spec_id": "spec_test123",
    "message": "The spec 'spec_test123' does not exist in the database.",
    "available_specs": [
      "spec_cb54d186",
      "spec_f0c7e52b",
      "spec_61927daf",
      "spec_8beccc69a76c",
      "spec_7741258885f4"
    ],
    "hint": "Use one of the available spec IDs or create a new design using POST /api/v1/generate"
  }
}
```

## How to Test

### 1. Start the server:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Run the test script:
```bash
python test_report_fix.py
```

### 3. Or test manually with curl:

**Get a valid token:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "bhiv2024"}'
```

**Test with invalid spec_id:**
```bash
curl -X GET "http://localhost:8000/api/v1/reports/spec_test123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Test with valid spec_id:**
```bash
curl -X GET "http://localhost:8000/api/v1/reports/spec_cb54d186" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Available Specs in Database

Current specs (as of test):
- spec_cb54d186
- spec_f0c7e52b
- spec_61927daf
- spec_8beccc69a76c
- spec_7741258885f4

## Benefits

1. **Better Developer Experience**: Clear error messages with actionable information
2. **Faster Debugging**: Shows available specs immediately
3. **Self-Documenting**: Hints guide users to the correct endpoint
4. **Production Ready**: Helpful for API consumers and frontend developers

## Files Modified

- `backend/app/api/reports.py` - Enhanced error handling in get_report endpoint
- `backend/test_report_fix.py` - Test script to verify the fix

## Next Steps

To create a new spec for testing:
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Design a modern 3-bedroom apartment",
    "city": "Mumbai",
    "budget": 5000000
  }'
```

This will return a new spec_id that you can use with the reports endpoint.
