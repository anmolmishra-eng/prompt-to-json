# CURL Testing Guide for /api/v1/generate Endpoint

## Current Status
- ✅ Server is running (http://127.0.0.1:8000)
- ✅ Health check works
- ✅ Authentication works (admin/bhiv2024)
- ❌ Generate endpoint returns 500 error

## Issue Analysis
The generate endpoint is failing with "Unexpected error during spec generation".
Possible causes:
1. Database connection issue
2. LM service (AI model) failure
3. Storage service (Supabase) issue
4. Missing environment variables

## Step-by-Step CURL Commands

### 1. Health Check
```bash
curl http://127.0.0.1:8000/health
```
**Expected Response:**
```json
{"status":"ok","service":"Design Engine API","version":"0.1.0"}
```

### 2. Login
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=bhiv2024"
```
**Expected Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```
**Action:** Copy the access_token value

### 3. Generate Design (CURRENTLY FAILING)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "user_id": "admin",
    "prompt": "Design a modern 2BHK apartment",
    "project_id": "test_001"
  }'
```
**Current Response:**
```json
{
  "error": {
    "code": "HTTP_ERROR",
    "message": "Unexpected error during spec generation",
    "status_code": 500
  }
}
```

**Expected Response (when working):**
```json
{
  "spec_id": "spec_abc123def456",
  "spec_json": {
    "objects": [...],
    "design_type": "house",
    "style": "modern",
    "dimensions": {...}
  },
  "preview_url": "https://...",
  "estimated_cost": 5000000,
  "compliance_check_id": "check_abc123def456",
  "created_at": "2026-02-11T10:00:00Z",
  "spec_version": 1,
  "user_id": "admin"
}
```

## Troubleshooting Steps

### Check 1: Database Connection
```bash
psql -U postgres -d bhiv_db -c "SELECT COUNT(*) FROM users;"
```

### Check 2: Environment Variables
Check if these are set in backend/.env:
- DATABASE_URL
- SUPABASE_URL
- SUPABASE_KEY
- OPENAI_API_KEY or ANTHROPIC_API_KEY

### Check 3: Server Logs
Look at the terminal where the server is running for detailed error messages.

### Check 4: Test with Simpler Prompt
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"user_id":"admin","prompt":"Design a kitchen"}'
```

## Verification After Fix

### 1. Check Database
```bash
psql -U postgres -d bhiv_db -c "SELECT id, user_id, prompt, estimated_cost FROM specs ORDER BY created_at DESC LIMIT 1;"
```

### 2. Check Local Files
```bash
dir backend\data\specs\spec_*.json
dir backend\data\geometry_outputs\spec_*.glb
```

### 3. Retrieve Spec
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/specs/YOUR_SPEC_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Common Fixes

### Fix 1: Database Not Running
```bash
# Start PostgreSQL
net start postgresql-x64-14
```

### Fix 2: Missing Environment Variables
Create/update backend/.env with:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bhiv_db
USE_AI_MODEL=false
```

### Fix 3: Restart Server
```bash
# Stop current server (Ctrl+C)
# Start again
cd backend
python -m uvicorn app.main:app --reload
```

## Next Steps
1. Check server terminal for detailed error logs
2. Verify database is running and accessible
3. Check environment variables are set correctly
4. Try with USE_AI_MODEL=false to use template fallback
5. Review server logs in backend/server.log
