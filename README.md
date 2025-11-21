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

## 📋 How to Run This Project

### Prerequisites
- Python 3.11+
- PostgreSQL database (Supabase account)
- NVIDIA GPU (optional, for local AI processing)
- Git installed

### Step-by-Step Setup

1. **Clone the Repository**
```bash
git clone https://github.com/anmolmishra-eng/prompt-to-json.git
cd prompt-to-json
```

2. **Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Navigate to Backend Directory**
```bash
cd backend
```

4. **Install All Dependencies**
```bash
pip install -r requirements.txt
```

5. **Setup Environment Variables**
   - Copy `.env.example` to `.env`
   - Fill in your Supabase credentials:
     ```
     DATABASE_URL=postgresql://user:pass@host:port/dbname
     SUPABASE_URL=https://your-project.supabase.co
     SUPABASE_KEY=your-supabase-anon-key
     JWT_SECRET_KEY=your-secret-key
     SENTRY_DSN=your-sentry-dsn (optional)
     OPENAI_API_KEY=your-openai-key (optional)
     ```

6. **Start the Development Server**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Access the API**
   - API Base URL: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/api/v1/health`

### Testing the Setup
```bash
# Run comprehensive endpoint tests
python quick_test_all.py
```

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

## 🔧 Configuration

Key environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase API key
- `JWT_SECRET_KEY` - JWT signing key
- `SENTRY_DSN` - Error monitoring
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
