# Complete Backend API Endpoint Analysis

## Project Overview
This is a **Design Engine API** - A comprehensive FastAPI backend for architectural/interior design generation with AI, compliance checking, and workflow automation.

---

## 🔐 Authentication Endpoints (`/api/v1/auth`)

### 1. POST `/api/v1/auth/login`
- **Purpose**: User authentication and JWT token generation
- **Input**: Username and password (OAuth2 form)
- **Output**: JWT access token
- **Users**: `user`, `admin`, `demo` (hardcoded for demo)

### 2. POST `/api/v1/auth/refresh`
- **Purpose**: Refresh expired JWT tokens
- **Input**: Valid JWT token
- **Output**: New JWT token with extended expiration

---

## 🎨 Core Design Generation Workflow

### 3. POST `/api/v1/generate`
- **Purpose**: Generate new design specification from natural language prompt
- **Process**:
  1. Validates user input and city support
  2. Calls LM (Language Model) for design generation
  3. Calculates estimated cost based on materials, area, design type
  4. Saves spec to database
  5. Generates 3D preview (GLB file)
  6. Returns complete design specification
- **Input**:
  - `user_id`, `prompt`, `city`, `style`, `context`
- **Output**:
  - `spec_id`, `spec_json`, `preview_url`, `estimated_cost`, `compliance_check_id`
- **Cost Calculation**: Based on design type (house: ₹25k/sqm, kitchen: ₹35k/sqm, etc.)

### 4. GET `/api/v1/specs/{spec_id}`
- **Purpose**: Retrieve existing design specification
- **Output**: Complete spec with preview URL and metadata

### 5. POST `/api/v1/evaluate`
- **Purpose**: Evaluate and rate a design specification
- **Process**:
  1. Validates spec exists
  2. Saves user rating (0-5 scale)
  3. Processes feedback loop for ML training
  4. Triggers training if rating threshold met
- **Input**: `spec_id`, `user_id`, `rating`, `notes`, `feedback_text`
- **Output**: `eval_id`, `feedback_processed`, `training_triggered`

### 6. POST `/api/v1/iterate`
- **Purpose**: Improve/modify existing design based on strategy
- **Strategies**: `auto_optimize`, `improve_materials`, `improve_layout`, `improve_colors`
- **Process**:
  1. Loads existing spec
  2. Applies optimization strategy
  3. Generates new version
  4. Saves as iteration
- **Output**: `before`, `after`, `feedback`, `iteration_id`, `preview_url`

### 7. POST `/api/v1/switch`
- **Purpose**: Switch materials/properties using natural language
- **Supported Commands**:
  - "change floor to marble"
  - "replace kitchen counter with granite"
  - "make all cushions orange"
  - "update wall color to #FFE4B5"
- **Process**:
  1. Parses natural language query
  2. Identifies target objects
  3. Applies changes
  4. Recalculates cost impact
  5. Generates new preview
- **Output**: `iteration_id`, `changes`, `cost_impact`, `preview_url`

---

## ✅ Compliance & Validation

### 8. POST `/api/v1/compliance/run_case`
- **Purpose**: Run compliance check against city regulations
- **Supported Cities**: Mumbai, Pune, Ahmedabad, Nashik
- **Process**:
  1. Validates city
  2. Calls external Soham MCP service
  3. Falls back to mock response if service unavailable
- **Output**: `case_id`, `rules_applied`, `reasoning`, `confidence_score`

### 9. POST `/api/v1/compliance/feedback`
- **Purpose**: Submit feedback on compliance results
- **Input**: `project_id`, `case_id`, `user_feedback` (up/down)

### 10. POST `/api/v1/compliance/ingest_pdf`
- **Purpose**: Ingest compliance rules from PDF documents
- **Process**: Triggers Prefect workflow for PDF processing

### 11. POST `/api/v1/compliance/check`
- **Purpose**: Generate compliance report for spec
- **Output**: Compliance ZIP file with signed URL

### 12. POST `/api/v1/mcp/check`
- **Purpose**: MCP (Model Context Protocol) compliance check
- **Integration**: Connects to Soham's MCP service

---

## 📊 System Health & Monitoring

### 13. GET `/health`
- **Purpose**: Basic health check (public, no auth)
- **Output**: Service status, version

### 14. GET `/api/v1/health`
- **Purpose**: Authenticated health check
- **Output**: Status, uptime, service info

### 15. GET `/api/v1/health/detailed`
- **Purpose**: Detailed system health with all components
- **Output**:
  - Database status
  - Storage status
  - GPU availability
  - External services health
  - Workflow system status
  - Mock fallback status

### 16. GET `/metrics`
- **Purpose**: Prometheus metrics for monitoring
- **Output**: Application metrics in Prometheus format

### 17. GET `/test-error`
- **Purpose**: Test Sentry error tracking integration

---

## 📚 History & Reports

### 18. GET `/api/v1/history`
- **Purpose**: Get user's complete design history
- **Query Params**: `limit`, `project_id`
- **Output**: List of specs with iterations, evaluations, compliance checks

### 19. GET `/api/v1/history/{spec_id}`
- **Purpose**: Get complete history for specific spec
- **Output**: Spec details, all iterations, all evaluations

### 20. GET `/api/v1/reports/{spec_id}`
- **Purpose**: Get comprehensive report for spec
- **Output**:
  - Spec data
  - All iterations
  - All evaluations
  - Compliance checks
  - Preview URLs
  - Data integrity checks

### 21. POST `/api/v1/reports`
- **Purpose**: Create custom report
- **Input**: `title`, `content`, `report_type`, `spec_id`

### 22. POST `/api/v1/upload`
- **Purpose**: Upload report files
- **Output**: Signed URL, metadata

### 23. POST `/api/v1/upload-preview`
- **Purpose**: Upload preview files (GLB, JPG, PNG)
- **Input**: `spec_id`, file

### 24. POST `/api/v1/upload-geometry`
- **Purpose**: Upload geometry STL files
- **Input**: `spec_id`, file

### 25. POST `/api/v1/upload-compliance`
- **Purpose**: Upload compliance ZIP files
- **Input**: `case_id`, file

---

## 🤖 Machine Learning & RL Training

### 26. POST `/api/v1/rl/feedback`
- **Purpose**: Submit RL (Reinforcement Learning) feedback
- **Process**:
  1. Saves to local database
  2. Sends to Ranjeet's live RL service
- **Input**: `design_a_id`, `design_b_id`, `rating_a`, `rating_b`

### 27. POST `/api/v1/rl/feedback/city`
- **Purpose**: Submit city-specific RL feedback
- **Input**: `city`, `user_rating`, `design_spec`, `compliance_result`

### 28. GET `/api/v1/rl/feedback/city/{city}/summary`
- **Purpose**: Get feedback summary for specific city
- **Output**: Total feedback, average rating, distribution, recent count

### 29. POST `/api/v1/rl/train/rlhf`
- **Purpose**: Train Reward Model using RLHF (Reinforcement Learning from Human Feedback)
- **Process**:
  1. Builds preference dataset from database
  2. Trains reward model
  3. Runs PPO RLHF on language model
- **Input**: `steps`, `rm_epochs`

### 30. POST `/api/v1/rl/train/opt`
- **Purpose**: Train PPO spec-edit policy
- **Input**: `steps`, `learning_rate`, `batch_size`, etc.

### 31. POST `/api/v1/rl/optimize`
- **Purpose**: RL-based design optimization
- **Input**: `spec_json`, `city`, `constraints`
- **Output**: Optimized spec with improvements and metrics

### 32. POST `/api/v1/rl/suggest/iterate`
- **Purpose**: Get RL-based iteration suggestions
- **Input**: `spec_id`, `strategy`

---

## 📱 Mobile API Wrappers

### 33. POST `/api/v1/mobile/generate`
- **Purpose**: Mobile wrapper for generate endpoint

### 34. POST `/api/v1/mobile/evaluate`
- **Purpose**: Mobile wrapper for evaluate endpoint

### 35. POST `/api/v1/mobile/iterate`
- **Purpose**: Mobile wrapper for iterate endpoint

### 36. POST `/api/v1/mobile/switch`
- **Purpose**: Mobile wrapper for switch endpoint (converts to query format)

### 37. GET `/api/v1/mobile/health`
- **Purpose**: Mobile-specific health check

---

## 🥽 VR (Virtual Reality) Endpoints

### 38. GET `/api/v1/vr/preview/{spec_id}`
- **Purpose**: Get VR-optimized preview URL
- **Output**: GLB file URL for VR viewing

### 39. GET `/api/v1/vr/render/{spec_id}`
- **Purpose**: Generate VR render with quality settings
- **Quality Options**: `high`, `ultra`
- **Process**:
  1. Creates VR render record
  2. Processes geometry for VR
  3. Uploads to storage
  4. Returns render URL

### 40. GET `/api/v1/vr/status/{render_id}`
- **Purpose**: Check VR render status
- **Output**: Progress, status, file size, timing

### 41. POST `/api/v1/vr/feedback`
- **Purpose**: Submit VR experience feedback

---

## 🧠 BHIV AI Assistant (Main Orchestration Layer)

### 42. POST `/bhiv/v1/prompt`
- **Purpose**: **CENTRAL BHIV AI ASSISTANT ENDPOINT** - Main orchestration brain
- **Process**:
  1. Accepts user prompt
  2. Generates design JSON using LM
  3. Routes to all agents in parallel:
     - **MCP Compliance Agent** (Sohum's service)
     - **RL Optimization Agent** (Ranjeet's service)
     - **Geometry Generation Agent** (3D GLB files)
  4. Collects and aggregates results
  5. Notifies Prefect for workflow automation
  6. Returns unified response
- **Input**:
  - `user_id`, `prompt`, `city`, `project_id`, `design_type`, `budget`, `area_sqft`
- **Output**:
  - `request_id`, `spec_id`, `design_spec`
  - Agent results (MCP, RL, Geometry)
  - Total duration, status

### 43. POST `/bhiv/v1/feedback`
- **Purpose**: Submit feedback for BHIV-generated designs
- **Process**: Records evaluation and queues for training

### 44. GET `/bhiv/v1/health`
- **Purpose**: BHIV assistant health check

### 45. POST `/bhiv/v1/design`
- **Purpose**: Fully integrated design generation
- **Process**:
  1. Generate spec from prompt
  2. Run Sohum's MCP compliance
  3. Run Ranjeet's RL optimization
  4. Return unified response

### 46. POST `/bhiv/v1/process_with_workflow`
- **Purpose**: Process design with integrated workflow orchestration
- **Features**: Includes PDF processing via Prefect workflows

---

## 🤖 Workflow Automation (BHIV Automations)

### 47. GET `/api/v1/automation/status`
- **Purpose**: Get BHIV automation system status
- **Output**:
  - Workflow system status
  - External services health
  - Available workflows
  - Recent executions (from database)

### 48. POST `/api/v1/automation/pdf-compliance`
- **Purpose**: Trigger PDF compliance automation
- **Input**: `pdf_url`, `city`, `sohum_url`
- **Process**: Triggers Prefect workflow for PDF processing

### 49. POST `/api/v1/automation/workflow`
- **Purpose**: Trigger any BHIV automation workflow
- **Workflow Types**:
  - `pdf_compliance`
  - `design_optimization`
  - `health_monitoring`
- **Output**: Traceable workflow execution with run_id

### 50. GET `/api/v1/automation/workflow/{flow_run_id}/status`
- **Purpose**: Get real-time status of workflow run
- **Output**: Prefect status + database execution details

---

## 🏙️ Multi-City Support

### 51. POST `/api/v1/rl/feedback/city`
- **Purpose**: Submit city-specific RL feedback
- **Supported Cities**: Mumbai, Pune, Nashik, Ahmedabad, Bangalore

### 52. GET `/api/v1/rl/feedback/city/{city}/summary`
- **Purpose**: Get feedback analytics for specific city

---

## 🔍 Data Audit & Privacy

### 53. Data Audit Endpoints
- **Purpose**: Track data lineage, integrity, and compliance
- **Features**: Audit logs for all operations

### 54. Data Privacy Endpoints
- **Purpose**: GDPR compliance, data anonymization

---

## 🎯 Geometry Generation

### 55. POST `/api/v1/geometry/generate`
- **Purpose**: Generate 3D geometry files (GLB format)
- **Input**: `spec_json`, `request_id`, `format`
- **Output**: Geometry URL, file size, generation time

---

## 📊 Monitoring System

### 56. Monitoring Endpoints
- **Purpose**: Real-time system monitoring
- **Features**:
  - Performance tracking
  - Error logging
  - Service health checks
  - Alert management

---

## 🔄 Integration Layer

### 57. Integration Endpoints
- **Purpose**: Modular separation and dependency mapping
- **Features**: System analysis, overlap detection

---

## 🧪 Multi-City Testing

### 58. Multi-City Testing Endpoints
- **Purpose**: Test design generation across all supported cities
- **Features**: Automated testing for Mumbai, Pune, Nashik, Ahmedabad, Bangalore

---

## 📈 Key Features Summary

### External Service Integrations:
1. **Soham's MCP Service** - Compliance checking with city regulations
2. **Ranjeet's RL Service** - Reinforcement learning optimization
3. **Prefect Cloud** - Workflow automation and orchestration
4. **Supabase** - File storage (geometry, previews, compliance)
5. **Sentry** - Error tracking and monitoring
6. **Yotta** - GPU compute for heavy ML training

### Database Tables:
- `specs` - Design specifications
- `iterations` - Design iterations/versions
- `evaluations` - User ratings and feedback
- `compliance_checks` - Compliance validation results
- `rl_feedback` - RL training data
- `vr_renders` - VR rendering jobs
- `workflow_runs` - Prefect workflow executions
- `reports` - Generated reports
- `audit_logs` - Data audit trail

### Supported Cities:
- Mumbai
- Pune
- Nashik
- Ahmedabad
- Bangalore

### Design Types:
- House, Building, Office
- Kitchen, Bedroom, Bathroom, Living Room
- Car Body, PCB, Components

### File Formats:
- **3D Models**: GLB, STL
- **Images**: PNG, JPG
- **Documents**: PDF, ZIP
- **Data**: JSON, JSONL

---

## 🔐 Authentication Flow:
1. User logs in → Receives JWT token
2. All subsequent requests include JWT in Authorization header
3. Token expires after configured hours
4. User can refresh token without re-login

## 🎨 Design Generation Flow:
1. **Generate** → Create initial design from prompt
2. **Evaluate** → Rate the design (triggers ML training)
3. **Iterate** → Improve design with strategies
4. **Switch** → Modify materials/properties
5. **Compliance** → Validate against regulations
6. **VR Render** → Generate VR-ready 3D model

## 🤖 BHIV AI Assistant Flow:
1. User submits prompt to `/bhiv/v1/prompt`
2. System generates design spec using LM
3. Parallel agent execution:
   - MCP checks compliance
   - RL optimizes layout
   - Geometry generates 3D model
4. Results aggregated and returned
5. Prefect notified for workflow automation

---

## 📝 Notes:
- All endpoints (except `/health` and `/api/v1/auth/*`) require JWT authentication
- Mock responses used as fallback when external services unavailable
- Cost calculations in INR (Indian Rupees)
- Comprehensive error handling with Sentry integration
- Data integrity checks on all operations
- Prometheus metrics for monitoring
- CORS enabled for frontend integration
