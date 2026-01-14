# BHIV DESIGN ENGINE - DEMO SCRIPT

**Duration:** 3-4 minutes
**Purpose:** Showcase office-ready system to Vinayak

---

## 🎬 DEMO FLOW

### PART 1: System Overview (30 seconds)

**Screen:** Open browser to http://localhost:8000/docs

**Script:**
> "Welcome to the BHIV Design Engine backend. This is a complete FastAPI system with over 50 endpoints for AI-powered design generation. Let me show you the key features."

**Actions:**
1. Scroll through API documentation
2. Show endpoint categories:
   - Authentication
   - Design Generation
   - Compliance
   - RL Training
   - Data Audit

**Highlight:**
- "All endpoints are documented with examples"
- "JWT authentication protects all routes"

---

### PART 2: Core Design Flow (90 seconds)

**Screen:** Use Swagger UI or curl commands

**Script:**
> "Let me demonstrate the complete design generation flow."

#### Step 1: Login (10s)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=admin&password=bhiv2024" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

**Say:** "First, we authenticate and get a JWT token."

#### Step 2: Generate Design (30s)
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Design a modern 3BHK apartment in Mumbai",
    "city": "Mumbai",
    "user_id": "admin"
  }'
```

**Say:** "Now we generate a design from a natural language prompt. The system creates a complete JSON specification with materials, dimensions, and cost estimates."

**Show:** Response with spec_id, spec_json, preview_url, estimated_cost

#### Step 3: View Result (20s)
**Say:** "The response includes:"
- Complete design specification
- 3D preview URL
- Cost estimate in INR
- Compliance check ID

#### Step 4: Evaluate (15s)
```bash
curl -X POST "http://localhost:8000/api/v1/evaluate" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"spec_id": "spec_xxx", "user_id": "admin"}'
```

**Say:** "We can evaluate the design quality across multiple criteria."

#### Step 5: Iterate (15s)
```bash
curl -X POST "http://localhost:8000/api/v1/iterate" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"spec_id": "spec_xxx", "user_id": "admin", "strategy": "auto_optimize"}'
```

**Say:** "And iteratively improve the design based on feedback."

---

### PART 3: Multi-City Support (60 seconds)

**Screen:** Show production validation results

**Script:**
> "The system supports multiple cities with validated production flows."

#### Show Validation Results (30s)
```bash
cd backend
dir production_validation_results\responses
```

**Say:** "We've validated 72 complete flows across 4 cities:"
- Mumbai: 22 flows
- Pune: 20 flows
- Ahmedabad: 15 flows
- Nashik: 15 flows

#### Show Sample Flow (30s)
```bash
type production_validation_results\responses\pune_8_20260112_202810.json
```

**Say:** "Each flow includes:"
- Prompt to JSON generation
- MCP compliance checking
- RL optimization
- Geometry generation
- Feedback collection
- Training updates

**Highlight:** "All responses, logs, and GLB files are saved for audit."

---

### PART 4: Data Integrity (30 seconds)

**Screen:** Run audit commands

**Script:**
> "The system includes comprehensive data integrity auditing."

#### Run Audit (20s)
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/audit/integrity?limit=50"
```

**Say:** "We can audit the entire system to verify:"
- All specs have JSON
- All previews are stored
- All GLBs are generated
- All evaluations are recorded

**Show:** Integrity score and completeness metrics

#### Show Storage (10s)
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/audit/storage"
```

**Say:** "Storage audit shows all directories and file counts."

---

### PART 5: Production Ready (30 seconds)

**Screen:** Show summary

**Script:**
> "The system is production ready with complete validation."

**Highlight:**
1. **72 Validated Flows**
   - All cities tested
   - All artifacts saved

2. **Complete API**
   - 50+ endpoints
   - Full documentation
   - JWT security

3. **External Integrations**
   - MCP compliance (Sohum)
   - RL optimization (Ranjeet)
   - Prefect workflows

4. **Data Integrity**
   - Complete audit system
   - Storage verification
   - Integrity scoring

**Final Screen:** Show HANDOVER.md

**Say:** "Complete handover documentation is available in HANDOVER.md with:"
- API list
- Prefect workflows
- MCP integration
- RL integration
- Storage architecture
- Deployment guide

---

## 🎥 RECORDING TIPS

### Setup
1. Clean desktop
2. Full screen browser
3. Clear terminal
4. Test all commands first
5. Have token ready

### During Recording
- Speak clearly and slowly
- Pause between sections
- Show results clearly
- Highlight key points
- Keep under 4 minutes

### Tools
- Screen recorder: OBS Studio / QuickTime
- Resolution: 1920x1080
- Frame rate: 30fps
- Audio: Clear microphone

---

## 📋 PRE-RECORDING CHECKLIST

- [ ] Server running (http://localhost:8000)
- [ ] Get auth token
- [ ] Test all curl commands
- [ ] Open browser to /docs
- [ ] Navigate to validation results folder
- [ ] Have HANDOVER.md open
- [ ] Clear terminal history
- [ ] Close unnecessary applications
- [ ] Test microphone
- [ ] Start screen recording

---

## 🎯 KEY MESSAGES

1. **Complete System** - 50+ endpoints, fully documented
2. **Multi-City** - 72 validated flows across 4 cities
3. **Production Ready** - Tested, secure, monitored
4. **Data Integrity** - Complete audit and verification
5. **Office Ready** - Full handover documentation

---

## 📤 SUBMISSION TO VINAYAK

### Package Contents
1. **HANDOVER.md** - Complete documentation
2. **Demo Video** - 3-4 minute walkthrough
3. **Validation Results** - 72 flow responses
4. **API Documentation** - Available at /docs

### Email Template
```
Subject: BHIV Design Engine - Production Ready Handover

Hi Vinayak,

The BHIV Design Engine backend is complete and production ready.

Deliverables:
✅ Complete API (50+ endpoints)
✅ Multi-city validation (72 flows)
✅ Data integrity system
✅ Full documentation (HANDOVER.md)
✅ Demo video (attached)

Key Features:
- JWT authentication
- Design generation & iteration
- MCP compliance integration
- RL optimization integration
- Complete data audit system
- 4 cities supported (Mumbai, Pune, Ahmedabad, Nashik)

System Status: PRODUCTION READY

Documentation: See attached HANDOVER.md
Demo: See attached video
API Docs: http://localhost:8000/docs

Ready for deployment.

Best regards,
[Your Name]
```

---

**Demo Script Complete**
**Ready to Record:** ✅
**Estimated Duration:** 3-4 minutes
