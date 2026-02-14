# 🎨 /api/v1/generate Endpoint Testing - Complete Package

## 📦 Created Files Summary

### 🔧 Test Scripts

#### Windows Batch Files
1. **test_generate_simple.bat**
   - Simple, straightforward test
   - Easy to debug
   - Saves responses to JSON files
   - Best for: Quick testing

2. **test_generate_comprehensive.bat**
   - Detailed step-by-step execution
   - Full response analysis
   - Verification checklist
   - PowerShell integration for JSON parsing
   - Best for: Complete validation

3. **test_generate_curl_complete.bat**
   - Advanced with token extraction
   - Automatic spec retrieval
   - Verbose output
   - Best for: Automated testing

#### Unix/Linux/Mac Shell Script
4. **test_generate_curl.sh**
   - Colored output
   - jq integration for JSON parsing
   - Automatic spec retrieval
   - Cross-platform compatible
   - Best for: Unix-based systems

### 📚 Documentation

5. **GENERATE_ENDPOINT_ANALYSIS.md**
   - Complete endpoint specification
   - Request/response schemas
   - Backend processing flow
   - Security notes
   - Performance considerations
   - Troubleshooting guide

6. **CURL_QUICK_REFERENCE.md**
   - Quick start commands
   - Manual cURL examples
   - Expected results
   - Troubleshooting table
   - Example prompts
   - Tips and tricks

---

## 🚀 How to Use

### Option 1: Automated Testing (Recommended)

**Windows:**
```cmd
cd C:\Users\Anmol\Desktop\Backend
test_generate_comprehensive.bat
```

**Unix/Linux/Mac:**
```bash
cd ~/Desktop/Backend
chmod +x test_generate_curl.sh
./test_generate_curl.sh
```

### Option 2: Manual Testing

Follow the commands in `CURL_QUICK_REFERENCE.md`

### Option 3: Python Testing

Use the existing Python test:
```bash
python test_full_flow.py
```

---

## 📋 Test Flow

All scripts follow this flow:

```
1. Register User (admin/admin)
   ↓
2. Login & Get Token
   ↓
3. Call /api/v1/generate
   ↓
4. Analyze Response
   ↓
5. Retrieve Generated Spec
   ↓
6. Display Summary
```

---

## ✅ What Gets Tested

- ✅ User authentication flow
- ✅ Token generation and usage
- ✅ Design generation endpoint
- ✅ Request validation
- ✅ Response structure
- ✅ Spec ID generation
- ✅ Cost estimation
- ✅ Preview URL generation
- ✅ Compliance check queuing
- ✅ Spec retrieval
- ✅ Database storage
- ✅ File system storage

---

## 📊 Expected Output Files

After running tests:
- `register_response.json` - User registration response
- `login_response.json` - Authentication token
- `generate_response.json` - Generated design specification
- `spec_details.json` - Retrieved spec (if successful)

---

## 🎯 Success Criteria

A successful test should show:

1. **HTTP 201** status from /api/v1/generate
2. **Valid spec_id** in response
3. **Estimated cost** > 0 (in INR)
4. **Preview URL** present
5. **Compliance check ID** generated
6. **Spec retrievable** via GET endpoint
7. **Database record** created
8. **Files saved** to storage

---

## 🔍 Verification Checklist

Use this checklist after running tests:

- [ ] Server is running at http://127.0.0.1:8000
- [ ] Database is accessible
- [ ] LM service is running (local GPU or cloud)
- [ ] Storage service is configured (Supabase/local)
- [ ] Registration successful or user exists
- [ ] Login returns valid token
- [ ] Generate returns 201 status
- [ ] Response contains all required fields
- [ ] Spec can be retrieved
- [ ] Files are created in data/specs/
- [ ] Preview file (.glb) is generated
- [ ] Database record exists

---

## 🐛 Common Issues & Solutions

### Issue: Connection Refused
```
Solution: Ensure server is running
Command: python backend/app/main.py
```

### Issue: 401 Unauthorized
```
Solution: Token expired or invalid
Action: Re-run login step
```

### Issue: 422 Validation Error
```
Solution: Check request body format
Action: Verify JSON structure matches schema
```

### Issue: 500 Internal Server Error
```
Solution: Check server logs
Command: tail -f backend/logs/server.log
```

### Issue: Timeout
```
Solution: LM inference takes time
Action: Increase timeout (--max-time 60)
```

---

## 📈 Performance Expectations

| Operation | Expected Time |
|-----------|--------------|
| Registration | < 1 second |
| Login | < 1 second |
| LM Inference | 2-10 seconds |
| 3D Preview Gen | 1-3 seconds |
| Database Save | < 100ms |
| **Total** | **3-15 seconds** |

---

## 🔐 Security Notes

- Tokens expire after configured duration
- Preview URLs are signed with expiration
- All requests require authentication
- Input is validated and sanitized
- SQL injection protection via ORM
- Passwords are hashed (bcrypt)

---

## 📞 Support

If tests fail:
1. Check server logs: `backend/logs/`
2. Verify database connection
3. Ensure all services are running
4. Review error messages in response files
5. Check `GENERATE_ENDPOINT_ANALYSIS.md` for details

---

## 🎓 Learning Resources

- **API Docs:** http://127.0.0.1:8000/docs
- **Redoc:** http://127.0.0.1:8000/redoc
- **OpenAPI JSON:** http://127.0.0.1:8000/openapi.json

---

## 🔄 Next Steps

After successful testing:
1. Test other endpoints (/iterate, /evaluate)
2. Test with different cities (Pune, Ahmedabad, Nashik)
3. Test with various building types
4. Load testing with multiple concurrent requests
5. Integration testing with frontend

---

## 📝 Notes

- All scripts use `admin/admin` credentials
- Base URL is `http://127.0.0.1:8000`
- Responses are saved to JSON files for inspection
- Scripts are idempotent (can be run multiple times)
- User registration may fail if user exists (expected)

---

## 🎉 Summary

You now have:
- ✅ 4 test scripts (3 Windows, 1 Unix)
- ✅ 2 comprehensive documentation files
- ✅ Complete testing workflow
- ✅ Troubleshooting guides
- ✅ Quick reference commands
- ✅ Verification checklists

**Ready to test!** Run any script and verify the endpoint works correctly.
