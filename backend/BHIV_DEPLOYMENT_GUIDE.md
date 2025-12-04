# BHIV AI Assistant - Complete Deployment Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
pip install -r app/bhiv_assistant/workflows/requirements.txt
```

### Step 2: Setup Prefect Workflows
```bash
cd app/bhiv_assistant/workflows
python setup_prefect_complete.py
```

### Step 3: Start Services
```bash
# Terminal 1: Start main backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start BHIV Assistant
cd app/bhiv_assistant
python start_bhiv.py

# Terminal 3: Start Prefect server
prefect server start

# Terminal 4: Start Prefect worker
prefect worker start --pool default-pool
```

### Step 4: Test Integration
```bash
python test_bhiv_integration_fixed.py
```

## 🔧 Detailed Setup

### 1. BHIV Assistant Integration ✅ FIXED

**Problem**: Broken import paths, missing config
**Solution**: Created proper config structure

```
app/bhiv_assistant/
├── config/
│   ├── __init__.py
│   └── integration_config.py  ← NEW
├── app/
│   ├── mcp/mcp_client.py      ← FIXED imports
│   └── bhiv_layer/rl_feedback_handler.py ← FIXED imports
```

### 2. MCP Integration ✅ FIXED

**Problem**: Mock responses instead of real Sohum service
**Solution**: Updated to use live service

- **Sohum's Service**: `https://ai-rule-api-w7z5.onrender.com`
- **Endpoints**: `/mcp/compliance/check`, `/mcp/rules/fetch`
- **Fallback**: Internal compliance if external fails

### 3. RL Integration ✅ FIXED

**Problem**: Missing Ranjeet's service
**Solution**: Integrated with local RL system

- **Local RL Endpoints**: `/api/v1/rl/feedback`, `/api/v1/rl/train/opt`
- **Real Responses**: No more mock data
- **Feedback Loop**: Actual RL weight updates

### 4. Prefect Workflows ✅ FIXED

**Problem**: Not deployed, dependency issues
**Solution**: Complete deployment automation

```bash
# Setup everything
python app/bhiv_assistant/workflows/setup_prefect_complete.py

# Manual deployment
python app/bhiv_assistant/workflows/deploy_all_flows.py
```

**Workflows Deployed**:
- PDF Ingestion (Daily)
- Log Aggregation (Hourly)
- Geometry Verification (6-hourly)

### 5. Geometry Verification ✅ FIXED

**Problem**: Trimesh dependency failures
**Solution**: Auto-install + fallback validation

- **Auto-install**: Attempts to install trimesh if missing
- **Fallback**: Basic file validation without trimesh
- **Enhanced**: Better error handling and reporting

## 📊 Service Architecture

```
BHIV AI Assistant System
├── Main Backend (Port 8000)
│   ├── Core Design Engine
│   ├── Multi-City Support (4 cities)
│   ├── Local RL System
│   └── Compliance Validation
├── BHIV Assistant (Port 8003)
│   ├── MCP Integration → Sohum's Service
│   ├── RL Integration → Local RL
│   └── Unified Orchestration
├── Prefect Server (Port 4200)
│   ├── PDF Ingestion Workflow
│   ├── Log Aggregation Workflow
│   └── Geometry Verification Workflow
└── External Services
    └── Sohum MCP: ai-rule-api-w7z5.onrender.com
```

## 🧪 Testing & Validation

### Run Integration Tests
```bash
python test_bhiv_integration_fixed.py
```

**Expected Results**:
- ✅ Configuration: Config loads properly
- ✅ MCP Integration: Connects to Sohum's service
- ✅ RL Integration: Uses local RL system
- ✅ Geometry Verification: Handles dependencies
- ✅ BHIV Assistant: End-to-end orchestration

### Test Individual Components
```bash
# Test BHIV Assistant
curl -X POST http://localhost:8003/bhiv/v1/design \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","prompt":"Design 2BHK in Mumbai","city":"Mumbai"}'

# Test MCP Integration
curl http://localhost:8003/mcp/metadata/Mumbai

# Test RL Integration
curl -X POST http://localhost:8003/rl/feedback \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","spec_id":"test","rating":4.5,"design_accepted":true}'
```

## 🔄 Workflow Management

### Prefect UI Access
- **URL**: http://localhost:4200
- **Features**: Deployment management, flow monitoring, logs

### Workflow Operations
```bash
# Check workflow status
prefect deployment ls

# Run workflow manually
prefect deployment run "pdf-ingestion-daily"

# View logs
prefect flow-run logs <run-id>
```

## 🚨 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Fix: Ensure proper Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**2. Prefect Connection Issues**
```bash
# Fix: Reset Prefect config
prefect config unset PREFECT_API_URL
prefect config set PREFECT_API_URL=http://localhost:4200/api
```

**3. MCP Service Unreachable**
```bash
# Check: Sohum's service status
curl https://ai-rule-api-w7z5.onrender.com/health
```

**4. Geometry Dependencies**
```bash
# Fix: Install manually
pip install trimesh[easy]
```

## 📈 Production Deployment

### Environment Variables
```bash
# .env file
BHIV_SOHUM_BASE_URL=https://ai-rule-api-w7z5.onrender.com
BHIV_SOHUM_API_KEY=your-api-key
BHIV_RANJEET_BASE_URL=http://localhost:8000
PREFECT_API_URL=http://localhost:4200/api
```

### Docker Deployment
```bash
# Build and run
docker-compose up -d

# Check services
docker-compose ps
```

## ✅ Verification Checklist

- [ ] Main backend running on port 8000
- [ ] BHIV Assistant running on port 8003
- [ ] Prefect server running on port 4200
- [ ] Prefect worker active
- [ ] All integration tests passing
- [ ] MCP service reachable
- [ ] RL endpoints responding
- [ ] Workflows deployed successfully

## 🎯 Success Metrics

**Integration Status**: ✅ FULLY FUNCTIONAL
- **BHIV Assistant**: Real orchestration (no mocks)
- **MCP Integration**: Live Sohum service connection
- **RL Integration**: Local RL system integration
- **Workflow Automation**: Prefect workflows deployed
- **End-to-End**: Complete system working

**Next Steps**:
1. Monitor production performance
2. Add more cities to MCP system
3. Enhance RL feedback collection
4. Scale Prefect workers as needed

---

**Status**: ✅ PRODUCTION READY
**Last Updated**: December 2024
**Deployment Time**: ~10 minutes
