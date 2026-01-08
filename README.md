# Design Engine API Backend

Complete FastAPI backend for design generation, evaluation, and optimization with AI/ML capabilities.

## 🚀 Features

- **Core Design Engine**: Generate, evaluate, iterate, and switch design components
- **Authentication**: JWT-based authentication system
- **Database**: PostgreSQL with Supabase integration
- **Storage**: File storage with signed URLs
- **AI/ML**: Local GPU support + cloud compute routing
- **RL/RLHF**: Reinforcement learning training endpoints
- **Compliance**: Design validation and compliance checking
- **Monitoring**: Health checks, metrics, and Sentry error tracking
- **Security**: Data encryption, GDPR compliance, audit logging

## 📋 Complete Setup Guide

### Prerequisites
- **Python 3.11+** (Download from [python.org](https://www.python.org/downloads/))
- **PostgreSQL Database** (Supabase account - free tier available)
- **Git** (Download from [git-scm.com](https://git-scm.com/))
- **NVIDIA GPU** (Optional, for local AI processing)
- **Code Editor** (VS Code recommended)

---

## 🗄️ Database Setup (Supabase)

### Step 1: Create Supabase Account
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project" and sign up
3. Create a new project:
   - **Project Name**: `design-engine-api`
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Select closest to your location
   - Wait 2-3 minutes for project creation

### Step 2: Get Database Credentials
1. In Supabase Dashboard, go to **Settings** → **Database**
2. Copy these values:
   - **Connection String** (URI format)
   - **Host**
   - **Database name**
   - **Port** (usually 6543 for pooler)
   - **User** (usually `postgres`)

3. Go to **Settings** → **API**
4. Copy these values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key
   - **service_role** key (keep this secret!)

### Step 3: Create Database Tables
The application will auto-create tables on first run, but you can verify:

1. In Supabase Dashboard, go to **Table Editor**
2. You should see these tables after first run:
   - `users` - User accounts
   - `specs` - Design specifications
   - `iterations` - Design iterations
   - `evaluations` - Design evaluations
   - `compliance_checks` - Compliance validations
   - `rl_feedback` - RL training data
   - `audit_logs` - Security audit trail

### Step 4: Create Storage Buckets
1. In Supabase Dashboard, go to **Storage**
2. Create these buckets (click "New bucket"):
   - `files` - User uploaded files
   - `previews` - Design preview images
   - `geometry` - 3D geometry files (.glb, .obj)
   - `compliance` - Compliance documents

3. For each bucket, set policies:
   - Go to bucket → **Policies**
   - Add policy: "Enable read access for authenticated users"
   - Add policy: "Enable insert for authenticated users"

---

## 🚀 Application Setup

### Step 1: Clone Repository
```bash
# Clone the project
git clone https://github.com/anmolmishra-eng/prompt-to-json.git
cd prompt-to-json
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Verify activation (you should see (venv) in terminal)
```

### Step 3: Navigate to Backend
```bash
cd backend
```

### Step 4: Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# This will install:
# - FastAPI (web framework)
# - SQLAlchemy (database ORM)
# - Supabase client
# - JWT authentication
# - And 50+ other dependencies
```

### Step 5: Configure Environment Variables

1. **Copy example file**:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

2. **Edit `.env` file** with your credentials:

```env
# ============================================================================
# DATABASE CONFIGURATION (from Supabase Step 2)
# ============================================================================
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# ============================================================================
# SUPABASE STORAGE (from Supabase Step 2)
# ============================================================================
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_KEY=eyJhbGc...[YOUR-ANON-KEY]
SUPABASE_SERVICE_KEY=eyJhbGc...[YOUR-SERVICE-KEY]

# ============================================================================
# AUTHENTICATION
# ============================================================================
JWT_SECRET_KEY=your-super-secret-key-min-32-chars-long-change-this
DEMO_USERNAME=admin
DEMO_PASSWORD=bhiv2024

# ============================================================================
# EXTERNAL SERVICES (Live URLs)
# ============================================================================
SOHAM_URL=https://ai-rule-api-w7z5.onrender.com
RANJEET_RL_URL=https://land-utilization-rl.onrender.com
LAND_UTILIZATION_ENABLED=true
LAND_UTILIZATION_MOCK_MODE=false
RANJEET_SERVICE_AVAILABLE=true

# ============================================================================
# MONITORING (Optional)
# ============================================================================
SENTRY_DSN=https://your-sentry-dsn (optional)
OPENAI_API_KEY=sk-your-openai-key (optional)

# ============================================================================
# ENVIRONMENT
# ============================================================================
DEBUG=true
ENVIRONMENT=development
```

### Step 6: Initialize Database
```bash
# Create initial admin user
python create_test_user.py

# Verify database connection
python get_users.py
```

### Step 7: Start the Server
```bash
# Development mode (auto-reload on code changes)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# ======================================================================
# 🚀 Design Engine API Server Starting...
# 🌍 Server URL: http://0.0.0.0:8000
# 📄 API Docs: http://0.0.0.0:8000/docs
# 🔍 Health Check: http://0.0.0.0:8000/health
# ======================================================================
```

### Step 8: Verify Installation

1. **Open browser** and go to:
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/api/v1/health

2. **Test authentication**:
   - In Swagger UI (http://localhost:8000/docs)
   - Find `POST /api/v1/auth/login`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "username": "admin",
       "password": "bhiv2024"
     }
     ```
   - Click "Execute"
   - Copy the `access_token` from response

3. **Authorize all endpoints**:
   - Click "Authorize" button (top right)
   - Paste token in format: `Bearer YOUR_TOKEN`
   - Click "Authorize"
   - Now you can test all protected endpoints!

---

## 🧪 Testing the Setup

### Quick Health Check
```bash
# Test basic connectivity
curl http://localhost:8000/health

# Expected response:
# {"status": "ok", "service": "Design Engine API", "version": "0.1.0"}
```

### Comprehensive Tests
```bash
# Run all endpoint tests
python quick_test_all.py

# Test specific features
python test_auth.py              # Authentication
python test_generate_simple.py   # Design generation
python test_evaluate_simple.py   # Design evaluation
python test_compliance_check.py  # Compliance checking
```

### Test External Services
```bash
# Wake up Render services (they sleep after inactivity)
python wake_services.py

# Check service integration
python check_mock_usage.py

# Should show:
# Sohum MCP: AVAILABLE
# Ranjeet RL: AVAILABLE
```

---

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Test database connection
python -c "from app.database import SessionLocal; db = SessionLocal(); print('✅ Database connected'); db.close()"

# Common fixes:
# 1. Check DATABASE_URL format
# 2. Verify Supabase project is active
# 3. Check firewall/network settings
# 4. Ensure password is URL-encoded (use %40 for @)
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.11+
```

### Port Already in Use
```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### External Services Down
```bash
# Render services sleep after 15 min inactivity
# Wake them up:
python wake_services.py

# Or enable mock mode temporarily in .env:
LAND_UTILIZATION_MOCK_MODE=true
```

---

## 📱 API Usage Examples

### 1. Login and Get Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "bhiv2024"}'
```

### 2. Generate Design
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

### 3. Check System Health
```bash
curl -X GET "http://localhost:8000/api/v1/health/detailed" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Next Steps

1. **Explore API Documentation**: http://localhost:8000/docs
2. **Test all endpoints** using Swagger UI
3. **Review logs** in `backend/data/logs/`
4. **Check monitoring** at http://localhost:8000/api/v1/monitoring/metrics
5. **Read API contract** in `docs/api_contract_v2.md`

---

## 📞 Support

If you encounter issues:
1. Check logs in `backend/data/logs/bhiv_assistant.jsonl`
2. Review error messages in terminal
3. Verify all environment variables are set
4. Ensure Supabase project is active
5. Check external services are awake (Render)

---

## 🔗 API Endpoints Documentation

### 🔐 Authentication

#### `POST /api/v1/auth/login`
**Purpose**: Authenticate users and obtain JWT tokens
- **Input**: `{"username": "string", "password": "string"}`
- **Output**: `{"access_token": "jwt_token", "token_type": "bearer"}`
- **What it does**: Validates user credentials and returns a JWT token for accessing protected endpoints

---

### 🎨 Core Design Engine

#### `POST /api/v1/generate`
**Purpose**: Generate new designs from natural language prompts
- **Input**: `{"prompt": "Create a modern kitchen with island", "style": "modern", "budget": 50000}`
- **Output**: Complete design specification with components, materials, and 3D geometry
- **What it does**:
  - Parses natural language design requirements
  - Extracts dimensions automatically (supports meters, feet, cm)
  - Generates detailed design specifications
  - Creates 3D geometry and material lists
  - Estimates costs and timelines

#### `POST /api/v1/evaluate`
**Purpose**: Evaluate design quality and feasibility
- **Input**: `{"design_id": "uuid", "criteria": ["aesthetics", "functionality", "cost"]}`
- **Output**: Detailed evaluation scores and improvement suggestions
- **What it does**:
  - Analyzes design against multiple criteria
  - Provides scores for aesthetics, functionality, cost-effectiveness
  - Identifies potential issues and bottlenecks
  - Suggests specific improvements

#### `POST /api/v1/iterate`
**Purpose**: Improve existing designs iteratively
- **Input**: `{"user_id": "user123", "spec_id": "spec_015ba76e", "strategy": "auto_optimize"}`
- **Output**: Before/after comparison with iteration details
- **What it does**:
  - Applies optimization strategies (auto_optimize, user_feedback, etc.)
  - Shows before/after design comparison
  - Generates new preview URLs and version numbers
  - Tracks iteration history with unique iteration IDs
  - Updates cost estimates and material specifications

#### `POST /api/v1/switch`
**Purpose**: Switch or replace specific design components
- **Input**: `{"user_id": "user123", "spec_id": "spec_015ba76e", "target": {"object_id": "kitchen_cabinet_01", "object_query": "upper cabinets"}, "update": {"material": "oak", "color_hex": "#8B4513", "texture_override": "wood_grain"}, "note": "Changed to oak for warmer look", "expected_version": 2}`
- **Output**: Updated design with component replacements
- **What it does**:
  - Targets specific objects by ID or query
  - Updates materials, colors, and textures
  - Maintains version control with expected_version
  - Preserves overall design integrity with user notes

#### `GET /api/v1/history`
**Purpose**: Retrieve user's design history and iterations
- **Input**: Query parameters for filtering (user_id, date_range, design_type)
- **Output**: List of all user designs with metadata and thumbnails
- **What it does**:
  - Shows complete design evolution timeline
  - Provides quick access to previous designs
  - Enables design comparison and rollback
  - Tracks user preferences over time

---

### 🤖 RL/RLHF Training (Reinforcement Learning)

#### `POST /api/v1/rl/feedback`
**Purpose**: Submit user preference feedback for AI training
- **Input**: `{"design_a_id": "uuid", "design_b_id": "uuid", "preference": "A", "reason": "Better layout"}`
- **Output**: Confirmation of feedback submission
- **What it does**:
  - Collects human preference data
  - Trains AI to understand user preferences
  - Improves future design generation quality
  - Enables personalized design recommendations

#### `POST /api/v1/rl/train/rlhf`
**Purpose**: Train reward model using human feedback
- **Input**: Training configuration and feedback dataset
- **Output**: Training status and model performance metrics
- **What it does**:
  - Processes collected human feedback
  - Trains reward models to predict user preferences
  - Improves AI alignment with human values
  - Updates design generation algorithms

#### `POST /api/v1/rl/train/opt`
**Purpose**: Train optimization policy for design improvement
- **Input**: Policy configuration and training parameters
- **Output**: Training progress and policy performance
- **What it does**:
  - Optimizes design generation strategies
  - Learns to create better designs over time
  - Balances multiple objectives (cost, aesthetics, functionality)
  - Adapts to user feedback patterns

---

### ✅ Compliance & Validation

#### `GET /api/v1/compliance/regulations`
**Purpose**: Get list of available building codes and regulations
- **Input**: Optional location/region parameters
- **Output**: List of applicable regulations and standards
- **What it does**:
  - Provides building codes for different regions
  - Lists safety and accessibility requirements
  - Shows environmental regulations
  - Includes industry standards and best practices

#### `POST /api/v1/compliance/check`
**Purpose**: Validate design against building codes and regulations
- **Input**: `{"design_id": "uuid", "regulations": ["IBC", "ADA"], "location": "California"}`
- **Output**: Compliance report with violations and recommendations
- **What it does**:
  - Checks design against building codes
  - Validates accessibility requirements
  - Identifies safety violations
  - Provides specific fix recommendations
  - Generates compliance certificates

#### `POST /api/v1/compliance/run_case`
**Purpose**: Run compliance analysis for specific Indian city projects
- **Input**: Project details with city-specific parameters
- **Output**: Detailed compliance analysis with DCR validation
- **Supported Cities**: Mumbai, Pune, Ahmedabad
- **What it does**:
  - Validates against city-specific Development Control Regulations (DCR)
  - Analyzes plot size, location type, and road width requirements
  - Provides compliance scores and recommendations
  - Integrates with external compliance service for real-time validation

#### `POST /api/v1/compliance/feedback`
**Purpose**: Submit user feedback on compliance analysis results
- **Input**: `{"project_id": "proj_123", "case_id": "case_456", "input_case": {}, "output_report": {}, "user_feedback": "up"}`
- **Output**: Feedback confirmation with unique feedback ID
- **What it does**:
  - Records user satisfaction with compliance analysis
  - Enables adaptive learning for compliance AI
  - Supports "up" (positive) or "down" (negative) feedback
  - Integrates with external feedback service for continuous improvement

**Example Test Cases**:
```json
// Ahmedabad Project
{
  "project_id": "proj_lotus_towers_04",
  "case_id": "ahmedabad_001",
  "city": "Ahmedabad",
  "document": "Ahmedabad_DCR.pdf",
  "parameters": {
    "plot_size": 1500,
    "location": "urban",
    "road_width": 15
  }
}

// Mumbai Small Plot
{
  "project_id": "proj_compact_living_03",
  "case_id": "mumbai_002_small_plot",
  "city": "Mumbai",
  "document": "DCPR_2034.pdf",
  "parameters": {
    "plot_size": 400,
    "location": "suburban",
    "road_width": 15
  }
}

// Pune Riverfront
{
  "project_id": "proj_riverfront_02",
  "case_id": "pune_001",
  "city": "Pune",
  "document": "Pune_DCR.pdf",
  "parameters": {
    "plot_size": 800,
    "location": "suburban",
    "road_width": 10
  }
}

// Feedback Example
{
  "project_id": "proj_lotus_towers_04",
  "case_id": "ahmedabad_001",
  "input_case": {
    "city": "Ahmedabad",
    "parameters": {
      "plot_size": 1500,
      "location": "urban",
      "road_width": 15
    }
  },
  "output_report": {
    "rules_applied": ["AMD-FSI-URBAN-R15-20"],
    "confidence_score": 0.8
  },
  "user_feedback": "up"
}
```

---

### 🔒 Data Privacy (GDPR Compliance)

#### `GET /api/v1/data/{user_id}/export`
**Purpose**: Export all user data for GDPR compliance
- **Input**: User ID in URL path
- **Output**: Complete data export in JSON format
- **What it does**:
  - Exports all user designs and preferences
  - Includes interaction history and feedback
  - Provides machine-readable data format
  - Ensures GDPR "right to data portability"

#### `DELETE /api/v1/data/{user_id}`
**Purpose**: Delete all user data (GDPR "right to be forgotten")
- **Input**: User ID in URL path
- **Output**: Confirmation of data deletion
- **What it does**:
  - Permanently removes all user data
  - Deletes designs, preferences, and history
  - Anonymizes any remaining references
  - Provides deletion confirmation

---

### 🏥 System Health & Monitoring

#### `GET /api/v1/health`
**Purpose**: Check system health and service status
- **Output**: System status, database connectivity, and service metrics
- **What it does**:
  - Monitors database connections
  - Checks AI model availability
  - Reports system resource usage
  - Validates external service connections

## 🧪 Testing

Run comprehensive endpoint tests:
```bash
python quick_test_all.py
```

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── models.py     # Database models
│   ├── schemas.py    # Pydantic schemas
│   ├── database.py   # Database connection
│   ├── config.py     # Configuration
│   ├── storage.py    # File storage
│   ├── security.py   # Security utilities
│   └── utils.py      # Utility functions
├── requirements.txt  # Dependencies
└── .env             # Environment variables
```

## 🔧 Configuration Reference

### Required Environment Variables
| Variable | Description | Example |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:6543/db` |
| `SUPABASE_URL` | Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_KEY` | Supabase anon key | `eyJhbGc...` |
| `JWT_SECRET_KEY` | JWT signing key (min 32 chars) | `your-secret-key-here` |

### Optional Environment Variables
| Variable | Description | Default |
|----------|-------------|----------|
| `SENTRY_DSN` | Error monitoring | None |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `DEBUG` | Debug mode | `false` |
| `ENVIRONMENT` | Environment name | `development` |

### External Service URLs
| Service | URL | Status |
|---------|-----|--------|
| Sohum MCP | `https://ai-rule-api-w7z5.onrender.com` | ✅ Live |
| Ranjeet RL | `https://land-utilization-rl.onrender.com` | ✅ Live |

## 📊 Monitoring

- **Health**: `/api/v1/health` - Service health status
- **Metrics**: `/metrics` - Prometheus metrics
- **Logs**: Structured logging with audit trails
- **Errors**: Sentry integration for error tracking

## 🔒 Security

- JWT authentication for all endpoints
- AES-256 encryption for sensitive data
- GDPR compliance with data export/deletion
- Role-based access control
- Audit logging for all operations

## 🚀 Deployment

The backend is production-ready with:
- Docker support
- HTTPS configuration
- Environment-based configuration
- Database migrations
- Health checks
- Monitoring integration

## 📝 License

MIT License - see LICENSE file for details.SENTRY_DSN` - Error monitoring
- `OPENAI_API_KEY` - OpenAI API key

## 📊 Monitoring

- **Health**: `/api/v1/health` - Service health status
- **Metrics**: `/metrics` - Prometheus metrics
- **Logs**: Structured logging with audit trails
- **Errors**: Sentry integration for error tracking

## 🔒 Security

- JWT authentication for all endpoints
- AES-256 encryption for sensitive data
- GDPR compliance with data export/deletion
- Role-based access control
- Audit logging for all operations

## 🚀 Deployment

The backend is production-ready with:
- Docker support
- HTTPS configuration
- Environment-based configuration
- Database migrations
- Health checks
- Monitoring integration

## 📝 License

MIT License - see LICENSE file for details.
