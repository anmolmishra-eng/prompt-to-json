# BHIV DESIGN ENGINE - QUICK REFERENCE

**Version:** 1.0 | **Status:** Production Ready | **Date:** Jan 14, 2026

---

## 🚀 START SERVER

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Access:** http://localhost:8000/docs

---

## 🔐 AUTHENTICATION

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=admin&password=bhiv2024" \
  -H "Content-Type: application/x-www-form-urlencoded"

# Response: {"access_token": "...", "token_type": "bearer"}
```

---

## 🎨 CORE WORKFLOWS

### 1. Generate Design
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Design a 3BHK apartment",
    "city": "Mumbai",
    "user_id": "admin"
  }'
```

### 2. Evaluate Design
```bash
curl -X POST "http://localhost:8000/api/v1/evaluate" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"spec_id": "spec_xxx", "user_id": "admin"}'
```

### 3. Iterate Design
```bash
curl -X POST "http://localhost:8000/api/v1/iterate" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"spec_id": "spec_xxx", "user_id": "admin", "strategy": "auto_optimize"}'
```

### 4. Get History
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/history?limit=20"
```

---

## ✅ COMPLIANCE

```bash
# Check compliance
curl -X POST "http://localhost:8000/api/v1/compliance/run_case" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "project_id": "proj_123",
    "case_id": "case_456",
    "city": "Mumbai",
    "parameters": {"plot_size": 1000, "location": "urban", "road_width": 15}
  }'
```

---

## 🔍 DATA AUDIT

```bash
# Audit spec
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/audit/spec/spec_xxx"

# System integrity
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/audit/integrity?limit=50"

# Storage audit
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/audit/storage"
```

---

## 📊 HEALTH CHECKS

```bash
# Basic health
curl http://localhost:8000/health

# Detailed health
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/health/detailed

# Metrics
curl http://localhost:8000/metrics
```

---

## 🏙️ SUPPORTED CITIES

- Mumbai
- Pune
- Ahmedabad
- Nashik

---

## 🔗 EXTERNAL SERVICES

**MCP (Sohum):** https://ai-rule-api-w7z5.onrender.com
**RL (Ranjeet):** https://land-utilization-rl.onrender.com

---

## 💾 STORAGE LOCATIONS

```
data/
├── specs/              - JSON specifications
├── previews/           - Preview images
├── geometry_outputs/   - GLB files
├── evaluations/        - Evaluation results
├── compliance/         - Compliance reports
└── logs/               - Application logs
```

---

## 📈 VALIDATION RESULTS

- **Total Flows:** 72
- **Mumbai:** 22 flows
- **Pune:** 20 flows
- **Ahmedabad:** 15 flows
- **Nashik:** 15 flows
- **GLB Files:** 20
- **Success Rate:** 100% generation

---

## 🔧 CONFIGURATION

**File:** `backend/.env`

```env
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=...
JWT_SECRET_KEY=...
SOHAM_URL=https://ai-rule-api-w7z5.onrender.com
RANJEET_RL_URL=https://land-utilization-rl.onrender.com
```

---

## 📞 SUPPORT

**Documentation:** `HANDOVER.md`
**API Docs:** http://localhost:8000/docs
**Validation:** `MULTI_CITY_PROOF.md`

---

## ✅ QUICK CHECKLIST

- [ ] Server running
- [ ] Database connected
- [ ] Supabase configured
- [ ] External services accessible
- [ ] JWT token obtained
- [ ] Test generate endpoint
- [ ] Check health status
- [ ] Review validation results

---

**System Status:** ✅ PRODUCTION READY
