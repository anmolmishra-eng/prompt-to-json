# Quick Reference: Testing /api/v1/generate with cURL

## 🚀 Quick Start (Windows)

Run one of these batch files:
```cmd
test_generate_simple.bat              # Simple, easy to debug
test_generate_comprehensive.bat       # Detailed with full analysis
```

## 🚀 Quick Start (Unix/Linux/Mac)

```bash
chmod +x test_generate_curl.sh
./test_generate_curl.sh
```

---

## 📋 Manual cURL Commands

### 1. Register User
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"admin","full_name":"Admin User"}'
```

### 2. Login
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

### 3. Generate Design (replace TOKEN)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/generate" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
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
  }'
```

---

## 🎯 Expected Results

### Success (HTTP 201)
```json
{
  "spec_id": "spec_abc123...",
  "spec_json": { ... },
  "preview_url": "https://...",
  "estimated_cost": 5000000,
  "compliance_check_id": "comp_xyz789...",
  "created_at": "2024-02-11T10:37:02.343Z",
  "spec_version": 1,
  "user_id": "admin"
}
```

### Error (HTTP 422)
```json
{
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check token is valid and not expired |
| 422 Validation Error | Verify all required fields are present |
| 500 Internal Error | Check server logs, ensure DB and LM service are running |
| Timeout | Increase --max-time parameter (LM inference can take 5-15s) |
| Empty preview_url | Verify storage service (Supabase/local) is configured |

---

## 📁 Generated Files

After running tests, you'll find:
- `register_response.json` - Registration response
- `login_response.json` - Login response with token
- `generate_response.json` - Generate endpoint response
- `spec_details.json` - Retrieved spec details (if successful)

---

## 🔍 Verification Steps

1. ✅ Check HTTP status is 201
2. ✅ Verify spec_id is present and unique
3. ✅ Confirm estimated_cost > 0
4. ✅ Check preview_url is accessible
5. ✅ Verify compliance_check_id is generated
6. ✅ Confirm spec can be retrieved via GET /api/v1/specs/{spec_id}

---

## 📚 Additional Resources

- Full Analysis: `GENERATE_ENDPOINT_ANALYSIS.md`
- Python Test: `test_full_flow.py`
- API Documentation: http://127.0.0.1:8000/docs

---

## 💡 Tips

- Use `-v` flag for verbose output: `curl -v ...`
- Use `-w "\nHTTP: %{http_code}\n"` to see status code
- Use `-o file.json` to save response to file
- Use `--max-time 60` to prevent timeout on slow LM inference
- Install `jq` for better JSON formatting: `curl ... | jq '.'`

---

## 🎨 Example Prompts to Test

```json
// Residential Building
{
  "prompt": "Design a 3-bedroom residential building in Mumbai with 2000 sq ft area",
  "context": {"city": "Mumbai", "plot_area": 2000, "building_type": "residential"}
}

// Commercial Building
{
  "prompt": "Design a modern office building in Pune with parking for 50 vehicles",
  "context": {"city": "Pune", "building_type": "commercial"}
}

// Mixed Use
{
  "prompt": "Design a mixed-use building with shops on ground floor and apartments above",
  "context": {"city": "Ahmedabad", "building_type": "mixed"}
}
```
