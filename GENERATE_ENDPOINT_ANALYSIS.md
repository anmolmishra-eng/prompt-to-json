# /api/v1/generate Endpoint Analysis & Testing

## Endpoint Overview

**URL:** `POST /api/v1/generate`
**Purpose:** Generate new design specification using Language Model
**Authentication:** Required (Bearer Token)

---

## Request Specification

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Request Body Schema
```json
{
  "user_id": "string",           // Required: User identifier
  "prompt": "string",             // Required: Design description
  "project_id": "string",         // Required: Project identifier
  "context": {                    // Optional: Additional context
    "city": "string",             // City name (Mumbai, Pune, etc.)
    "plot_area": number,          // Area in sq ft
    "building_type": "string",    // residential/commercial/etc.
    "additionalProp1": {}         // Any additional properties
  }
}
```

### Example Request
```json
{
  "user_id": "admin",
  "prompt": "Design a 3-bedroom residential building in Mumbai with 2000 sq ft area",
  "project_id": "proj_001",
  "context": {
    "city": "Mumbai",
    "plot_area": 2000,
    "building_type": "residential"
  }
}
```

---

## Response Specification

### Success Response (201 Created)
```json
{
  "spec_id": "string",                    // Unique specification ID
  "spec_json": {                          // Complete design specification
    "additionalProp1": {}
  },
  "preview_url": "string",                // Signed URL for 3D preview
  "estimated_cost": number,               // Cost in INR
  "compliance_check_id": "string",        // Async compliance validation ID
  "created_at": "2026-02-11T10:37:02.343Z", // ISO timestamp
  "spec_version": 1,                      // Version number
  "user_id": "string"                     // User identifier
}
```

### Error Response (422 Validation Error)
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

## Backend Processing Flow

1. **Validate Input**
   - Check required fields (user_id, prompt, project_id)
   - Validate city support (if provided)
   - Verify user authentication

2. **Run LM Inference**
   - Route to local GPU or cloud service
   - Generate design specification from prompt
   - Apply city-specific rules (if applicable)

3. **Calculate Estimated Cost**
   - Analyze design parameters
   - Apply cost estimation model
   - Return cost in INR

4. **Save Specification**
   - Store in PostgreSQL database
   - Save JSON to local/cloud storage
   - Generate unique spec_id

5. **Generate 3D Preview**
   - Create GLB file from specification
   - Upload to storage (local/Supabase)
   - Generate signed URL

6. **Queue Compliance Check**
   - Create async compliance validation job
   - Return compliance_check_id
   - Process in background

7. **Create Audit Log**
   - Log generation event
   - Track user action
   - Record timestamp

8. **Return Response**
   - Complete specification
   - Preview URL
   - Compliance check ID

---

## Testing with cURL

### Prerequisites
1. Server running at `http://127.0.0.1:8000`
2. Valid user credentials (username: admin, password: admin)
3. curl installed

### Step 1: Register User (if needed)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin",
    "full_name": "Admin User"
  }'
```

### Step 2: Login and Get Token
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin" \
  -s | jq -r '.access_token'
```

### Step 3: Call Generate Endpoint
```bash
TOKEN="<your_token_here>"

curl -X POST "http://127.0.0.1:8000/api/v1/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "admin",
    "prompt": "Design a 3-bedroom residential building in Mumbai with 2000 sq ft area",
    "project_id": "proj_001",
    "context": {
      "city": "Mumbai",
      "plot_area": 2000,
      "building_type": "residential"
    }
  }' \
  -w "\nHTTP Status: %{http_code}\n" \
  -o generate_response.json
```

### Step 4: View Response
```bash
cat generate_response.json | jq '.'
```

### Step 5: Retrieve Generated Spec
```bash
SPEC_ID=$(cat generate_response.json | jq -r '.spec_id')

curl -X GET "http://127.0.0.1:8000/api/v1/specs/$SPEC_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -s | jq '.'
```

---

## Expected Behavior

### Success Scenario
- HTTP Status: 201 Created
- Response contains valid spec_id
- preview_url is accessible
- estimated_cost > 0
- compliance_check_id is generated
- Spec is saved to database
- 3D preview file (.glb) is created

### Validation Error Scenario
- HTTP Status: 422 Unprocessable Entity
- Response contains error details
- Missing required fields
- Invalid data types

### Authentication Error Scenario
- HTTP Status: 401 Unauthorized
- Missing or invalid token
- Expired token

---

## Verification Checklist

- [ ] Request returns 201 status
- [ ] spec_id is generated and unique
- [ ] spec_json contains valid design data
- [ ] preview_url is accessible (signed URL)
- [ ] estimated_cost is calculated
- [ ] compliance_check_id is returned
- [ ] created_at timestamp is valid
- [ ] spec_version is set to 1
- [ ] Database record is created
- [ ] Local/cloud file is saved
- [ ] 3D preview (.glb) is generated
- [ ] Audit log entry is created
- [ ] Spec can be retrieved via GET /api/v1/specs/{spec_id}

---

## Common Issues & Solutions

### Issue: 401 Unauthorized
**Solution:** Ensure token is valid and included in Authorization header

### Issue: 422 Validation Error
**Solution:** Check all required fields are present and correctly formatted

### Issue: 500 Internal Server Error
**Solution:** Check server logs, verify database connection, ensure LM service is running

### Issue: Empty preview_url
**Solution:** Verify storage service (Supabase/local) is configured and accessible

### Issue: compliance_check_id is null
**Solution:** Check if compliance service is running and properly configured

---

## Performance Considerations

- **LM Inference:** 2-10 seconds (depends on GPU/cloud)
- **3D Preview Generation:** 1-3 seconds
- **Database Save:** < 100ms
- **Total Expected Time:** 3-15 seconds

---

## Security Notes

- All requests require valid JWT token
- Tokens expire after configured duration
- Preview URLs are signed with expiration
- User can only access their own specs
- Input is validated and sanitized
- SQL injection protection via ORM

---

## Related Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/specs/{spec_id}` - Retrieve specification
- `GET /api/v1/compliance/{compliance_check_id}` - Check compliance status
- `POST /api/v1/iterate` - Iterate on existing design
- `POST /api/v1/evaluate` - Evaluate design quality
