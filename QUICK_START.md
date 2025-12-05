# 🚀 BHIV AI Assistant - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Run Setup
```bash
# Run the complete setup script
setup_complete.bat
```

### Step 2: Configure Environment
```bash
# Edit .env file with your credentials
notepad backend\.env

# Required variables:
# DATABASE_URL=postgresql://...
# SUPABASE_URL=https://...
# SUPABASE_KEY=eyJ...
# JWT_SECRET_KEY=your-secret-key
```

### Step 3: Validate Setup
```bash
# Check if everything is configured correctly
python validate_setup.py
```

### Step 4: Start All Services
```bash
# Start all services in separate windows
start_all_services.bat
```

### Step 5: Test System
```bash
# Run comprehensive system tests
python test_complete_system.py
```

## 🎯 Service Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Main API** | http://localhost:8000/docs | Core design engine with Swagger UI |
| **BHIV Assistant** | http://localhost:8003 | AI orchestration layer |
| **Prefect UI** | http://localhost:4200 | Workflow management dashboard |
| **Health Check** | http://localhost:8000/api/v1/health | System health status |

## 🧪 Quick API Tests

### 1. Generate Design
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Design a modern 2BHK apartment in Mumbai",
    "city": "Mumbai",
    "budget": 50000
  }'
```

### 2. Test BHIV Assistant
```bash
curl -X POST http://localhost:8003/bhiv/v1/design \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "prompt": "Optimize lighting in living room",
    "city": "Mumbai"
  }'
```

### 3. Submit RL Feedback
```bash
curl -X POST http://localhost:8003/rl/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "spec_id": "test_spec",
    "rating": 4.5,
    "design_accepted": true
  }'
```

### 4. Check Compliance
```bash
curl -X POST http://localhost:8000/api/v1/compliance/check \
  -H "Content-Type: application/json" \
  -d '{
    "design_id": "test_design",
    "city": "Mumbai",
    "regulations": ["IBC", "NBC"]
  }'
```

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BHIV AI Assistant System                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Main API    │    │ BHIV        │    │ Prefect     │     │
│  │ Port 8000   │◄──►│ Assistant   │◄──►│ Workflows   │     │
│  │             │    │ Port 8003   │    │ Port 4200   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ PostgreSQL  │    │ Sohum MCP   │    │ Local RL    │     │
│  │ (Supabase)  │    │ Service     │    │ System      │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Key Features

### 🎨 Core Design Engine
- **Generate**: Natural language to 3D designs
- **Evaluate**: Multi-criteria design assessment
- **Iterate**: AI-powered design optimization
- **Switch**: Component replacement and updates
- **History**: Complete design evolution tracking

### 🧠 BHIV AI Assistant Layer
- **MCP Integration**: Real-time compliance checking via Sohum's service
- **RL Integration**: Reinforcement learning feedback loop
- **Workflow Orchestration**: Automated PDF processing and rule extraction
- **Multi-Agent Coordination**: Seamless service integration

### ✅ Compliance & Validation
- **Multi-City Support**: Mumbai, Pune, Ahmedabad, Nashik
- **Building Codes**: IBC, NBC, local DCR validation
- **Real-time Checking**: Live compliance analysis
- **Feedback Loop**: Continuous improvement via user feedback

### 🤖 AI/ML Capabilities
- **Local GPU**: RTX-3060 support for fast inference
- **Cloud Fallback**: Yotta cloud GPU integration
- **RL Training**: PPO-based design optimization
- **RLHF**: Human feedback integration

### 📊 Monitoring & Observability
- **Health Checks**: Real-time system status
- **Metrics**: Prometheus integration
- **Error Tracking**: Sentry integration
- **Audit Logs**: Complete operation tracking

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check what's using the port
netstat -ano | findstr :8000
# Kill the process
taskkill /PID <process_id> /F
```

**2. Import Errors**
```bash
# Ensure virtual environment is activated
cd backend
venv\Scripts\activate.bat
pip install -r requirements.txt
```

**3. Database Connection Issues**
```bash
# Check DATABASE_URL in .env
# Verify Supabase credentials
# Test connection: python -c "from app.database import engine; print('DB OK')"
```

**4. GPU Not Detected**
```bash
# Check CUDA installation
nvidia-smi
# Verify PyTorch CUDA support
python -c "import torch; print(torch.cuda.is_available())"
```

**5. External Services Unreachable**
```bash
# Test Sohum's service
curl https://ai-rule-api-w7z5.onrender.com/health
# Check firewall/proxy settings
```

## 📈 Performance Tips

1. **GPU Acceleration**: Ensure CUDA drivers are installed for RTX-3060
2. **Database Pooling**: Increase pool size for high load
3. **Caching**: Enable Redis for better response times
4. **Prefect Workers**: Scale workers based on workflow load
5. **Load Balancing**: Use nginx for production deployment

## 🔒 Security Checklist

- [ ] Change default JWT_SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS in production
- [ ] Configure CORS origins properly
- [ ] Set up proper firewall rules
- [ ] Enable audit logging
- [ ] Regular security updates

## 📚 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Redoc**: http://localhost:8000/redoc

## 🎯 Next Steps

1. **Frontend Integration**: Connect with React/Vue.js frontend
2. **Mobile App**: Integrate with mobile applications
3. **VR/AR**: Add immersive design visualization
4. **Scaling**: Deploy on cloud infrastructure
5. **Monitoring**: Set up production monitoring

---

**🎉 You're all set! The BHIV AI Assistant system is now running with full AI capabilities, multi-city compliance, and workflow automation.**
