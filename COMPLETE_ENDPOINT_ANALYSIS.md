# Complete Backend API Endpoint Analysis

## Project Overview
This is a **Design Engine API** - A comprehensive FastAPI backend for architectural/interior design generation with AI, compliance checking, and workflow automation.

---

## 🔐 Authentication Endpoints (`/api/v1/auth`)

### 1. POST `/api/v1/auth/login`
- **Purpose**: User authentication and JWT token generation
- **Input**: Username and password (OAuth2 form)
- **Output**: JWT access token
- **Users**: `user`, `admin`, `demo` (hardcoded)
- **Token Expiry**: Configurable via JWT_EXPIRATION_HOURS

### 2. POST `/api/v1/auth/refresh`
- **Purpose**: Refresh expired JWT tokens
- **Input**: Valid JWT token
- **Output**: New JWT token with extended expiry
- **Security**: Requires valid existing token

---

## 🎨 Core Design Generation Endpoints

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
  - `user_id`: User identifier
  - `prompt`: Natural language design request (min 10 chars)
  - `city`: City for compliance (Mumbai, Delhi, Bangalore, Pune, Ahmedabad)
  - `style`: Design style (modern, luxury, minimalist, etc.)
  - `context`: Additional parameters
- **Output**:
  - `spec_id`: Unique specification ID
  - `spec_json`: Complete design JSON with objects, materials, dimensions
  - `preview_url`: 3D preview file URL
  - `estimated_cost`: Cost in INR
  - `compliance_check_id`: For async compliance validation
- **Cost Calculation**: Based on design type, area, materials, stories
  - House: ₹25k/sqm base
  - Office: ₹15k/sqm base
  - Kitchen: ₹35k/sqm base
  - Material premiums: Marble (1.8x), Granite (1.6x), Glass (1.5x)

### 4. GET `/api/v1/specs/{spec_id}`
- **Purpose**: Retrieve existing design specification
- **Input**: Spec ID
- **Output**: Complete spec with preview URL
- **Storage**: Database + Supabase storage fallback

---

## 📊 Design Evaluation Endpoints

### 5. POST `/api/v1/evaluate`
- **Purpose**: Evaluate and rate a design specification
- **Process**:
  1. Validates spec exists
  2. Saves evaluation to database
  3. Processes feedback loop for ML training
  4. Triggers training if rating threshold met
- **Input**:
  - `spec_id`: Design to evaluate
  - `user_id`: User providing feedback
  - `rating`: 0-5 score
  - `notes`: Optional feedback text
  - `feedback_text`: Detailed feedback
- **Output**:
  - `eval_id`: Evaluation ID
  - `feedback_processed`: Boolean
  - `training_triggered`: Boolean (if rating >= 4)
- **Fallback**: Saves to local file if database unavailable

---

## 🔄 Design Iteration Endpoints

### 6. POST `/api/v1/iterate`
- **Purpose**: Improve and iterate on existing design
- **Strategies**:
  - `auto_optimize`: Automatic optimization
  - `improve_materials`: Material upgrades
  - `improve_layout`: Layout optimization
  - `improve_colors`: Color scheme improvements
- **Input**:
  - `spec_id`: Design to iterate
  - `user_id`: User requesting iteration
  - `strategy`: Optimization strategy
- **Output**:
  - `before`: Original spec
  - `after`: Improved spec
  - `feedback`: Changes made
  - `iteration_id`: New iteration ID
  - `preview_url`: Updated preview
  - `training_triggered`: Boolean

---

## 🔄 Material Switch Endpoints

### 7. POST `/api/v1/switch`
- **Purpose**: Switch materials/properties using natural language
- **NLP Patterns Supported**:
  - "change floor to marble"
  - "replace kitchen counter with granite"
  - "make all cushions orange"
  - "update wall color to #FFE4B5"
- **Process**:
  1. Parses natural language query
  2. Identifies target objects
  3. Applies material/color changes
  4. Recalculates cost impact
  5. Generates new preview
  6. Saves as iteration
- **Input**:
  - `spec_id`: Design to modify
  - `query`: Natural language change request
- **Output**:
  - `iteration_id`: New iteration ID
  - `changes`: List of changes made
  - `cost_impact`: Cost difference
  - `preview_url`: Updated preview
  - `nlp_confidence`: Parsing confidence score

---

## ✅ Compliance & Validation Endpoints

### 8. POST `/api/v1/compliance/run_case`
- **Purpose**: Run compliance check against city regulations
- **Supported Cities**: Mumbai, Pune, Ahmedabad, Nashik
- **Process**:
  1. Validates city
  2. Calls external Soham MCP service
  3. Falls back to mock response if service unavailable
- **Input**:
  - `city`: City name
  - `project_id`: Project identifier
  - `parameters`: Design parameters
- **Output**:
  - `case_id`: Compliance case ID
  - `rules_applied`: List of regulation rules
  - `reasoning`: Compliance analysis
  - `confidence_score`: Analysis confidence
  - `clause_summaries`: Detailed rule summaries

### 9. POST `/api/v1/compliance/feedback`
- **Purpose**: Submit feedback on compliance results
- **Input**:
  - `project_id`: Project ID
  - `case_id`: Compliance case ID
  - `user_feedback`: "up" or "down"
- **Output**: Feedback confirmation

### 10. POST `/api/v1/compliance/ingest_pdf`
- **Purpose**: Ingest compliance rules from PDF documents
- **Process**: Triggers Prefect workflow for PDF processing
- **Input**:
  - `pdf_url`: URL to PDF document
  - `city`: City for rules
- **Output**: Workflow initiation confirmation

### 11. POST `/api/v1/compliance/check`
- **Purpose**: Generate compliance report for spec
- **Output**:
  - `compliance_url`: Signed URL to compliance ZIP
  - `status`: PASSED/FAILED

### 12. GET `/api/v1/compliance/regulations`
- **Purpose**: Get available compliance regulations
- **Output**: List of regulations (ISO 9001, OSHA, CE Marking, FDA 510K)

---

## 📊 System Health & Monitoring Endpoints

### 13. GET `/health`
- **Purpose**: Basic public health check (no auth required)
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
  - External service health (Sohum MCP, Ranjeet RL)
  - Workflow system status
  - Mock fallback status

### 16. GET `/api/v1/metrics`
- **Purpose**: Prometheus metrics for monitoring
- **Output**: Metrics in Prometheus text format

### 17. GET `/api/v1/test-error`
- **Purpose**: Test Sentry error tracking
- **Output**: Confirmation of error capture

---

## 📚 Design History Endpoints

### 18. GET `/api/v1/history/{spec_id}`
- **Purpose**: Get complete history for specific design
- **Output**:
  - Spec details
  - All iterations
  - All evaluations
  - Counts

### 19. GET `/api/v1/history`
- **Purpose**: Get user's complete design history
- **Input**:
  - `limit`: Max specs to return (default 20)
  - `project_id`: Optional project filter
- **Output**:
  - List of specs with metadata
  - Iteration counts
  - Evaluation counts
  - Compliance counts
  - Data integrity summary

---

## 📁 File Management & Reports Endpoints

### 20. GET `/api/v1/reports/{spec_id}`
- **Purpose**: Get complete report with data integrity checks
- **Output**:
  - Spec data
  - All iterations
  - All evaluations
  - All compliance checks
  - Preview URLs
  - Data integrity status

### 21. POST `/api/v1/reports`
- **Purpose**: Create custom report
- **Input**:
  - `title`: Report title
  - `content`: Report content
  - `report_type`: Type of report
  - `spec_id`: Optional spec reference
- **Output**: Report ID and storage confirmation

### 22. POST `/api/v1/upload`
- **Purpose**: Upload report files
- **Input**: File upload
- **Output**: Signed URL, metadata

### 23. POST `/api/v1/upload-preview`
- **Purpose**: Upload preview files (GLB, JPG, PNG)
- **Input**: Spec ID, file
- **Output**: Signed URL, metadata

### 24. POST `/api/v1/upload-geometry`
- **Purpose**: Upload geometry STL files
- **Input**: Spec ID, file
- **Output**: Signed URL, metadata

### 25. POST `/api/v1/upload-compliance`
- **Purpose**: Upload compliance ZIP files
- **Input**: Case ID, file
- **Output**: Signed URL, metadata

---

## 🤖 Machine Learning & RL Training Endpoints

### 26. POST `/api/v1/rl/feedback`
- **Purpose**: Submit RL feedback for training
- **Process**:
  1. Saves to local database
  2. Sends to Ranjeet's live RL service
- **Input**:
  - `design_a_id`, `design_b_id`: Designs to compare
  - `rating_a`: Rating for design A
- **Output**: Feedback confirmation

### 27. POST `/api/v1/rl/feedback/city`
- **Purpose**: Submit city-specific RL feedback
- **Input**:
  - `city`: City name
  - `user_rating`: Rating 0-5
  - `design_spec`: Design JSON
  - `compliance_result`: Compliance data
- **Output**: Feedback ID

### 28. GET `/api/v1/rl/feedback/city/{city}/summary`
- **Purpose**: Get feedback summary for specific city
- **Output**:
  - Total feedback count
  - Average rating
  - Rating distribution
  - Recent feedback count

### 29. POST `/api/v1/rl/train/rlhf`
- **Purpose**: Train Reward Model using RLHF
- **Input**:
  - `steps`: Training steps
  - `rm_epochs`: Reward model epochs
- **Process**:
  1. Builds preference pairs from database
  2. Trains reward model
  3. Runs PPO RLHF training
- **Output**: Training artifact path

### 30. POST `/api/v1/rl/train/opt`
- **Purpose**: Train PPO spec-edit policy
- **Input**: Training parameters
- **Output**: Policy artifact path

### 31. POST `/api/v1/rl/optimize`
- **Purpose**: RL-based design optimization
- **Input**:
  - `spec_json`: Design to optimize
  - `city`: City context
  - `constraints`: Optimization constraints
- **Output**:
  - Optimized spec
  - Improvements list
  - Metrics (cost savings, space utilization, compliance score)

### 32. POST `/api/v1/rl/suggest/iterate`
- **Purpose**: Get RL-based iteration suggestions
- **Input**:
  - `spec_id`: Design to improve
  - `strategy`: Optimization strategy
- **Output**: Iteration suggestions

---

## 📱 Mobile API Endpoints

### 33. POST `/api/v1/mobile/generate`
- **Purpose**: Mobile wrapper for generate endpoint
- **Input**: Same as `/api/v1/generate`
- **Output**: Same as `/api/v1/generate`

### 34. POST `/api/v1/mobile/evaluate`
- **Purpose**: Mobile wrapper for evaluate endpoint
- **Input**: Same as `/api/v1/evaluate`
- **Output**: Same as `/api/v1/evaluate`

### 35. POST `/api/v1/mobile/iterate`
- **Purpose**: Mobile wrapper for iterate endpoint
- **Input**: Same as `/api/v1/iterate`
- **Output**: Same as `/api/v1/iterate`

### 36. POST `/api/v1/mobile/switch`
- **Purpose**: Mobile wrapper for switch endpoint
- **Converts**: Mobile format to natural language query
- **Output**: Same as `/api/v1/switch`

### 37. GET `/api/v1/mobile/health`
- **Purpose**: Mobile-specific health check
- **Output**: Status, platform, API version

---

## 🥽 VR (Virtual Reality) Endpoints

### 38. GET `/api/v1/vr/preview/{spec_id}`
- **Purpose**: Get VR-optimized preview URL
- **Output**: GLB file URL for VR viewing

### 39. GET `/api/v1/vr/render/{spec_id}`
- **Purpose**: Generate VR rendering
- **Quality Options**: high, medium, low, ultra
- **Process**:
  1. Creates VR render record
  2. Processes geometry for VR
  3. Uploads to storage
  4. Returns render URL
- **Output**:
  - Render ID
  - Status
  - Progress
  - Render URL
  - Estimated time

### 40. GET `/api/v1/vr/status/{render_id}`
- **Purpose**: Check VR render status
- **Output**:
  - Status (queued, processing, completed, failed)
  - Progress percentage
  - VR URL
  - File size
  - Timing info

### 41. POST `/api/v1/vr/feedback`
- **Purpose**: Submit VR experience feedback
- **Input**: Feedback data
- **Output**: Feedback ID

---

## 🤖 BHIV AI Assistant Endpoints (Main Orchestration)

### 42. POST `/bhiv/v1/prompt`
- **Purpose**: Central BHIV AI Assistant - orchestrates all agents
- **Process**:
  1. Accepts user prompt
  2. Generates design JSON using LM
  3. Calls MCP compliance agent (Sohum)
  4. Calls RL optimization agent (Ranjeet)
  5. Calls geometry generation agent
  6. Aggregates all results
  7. Notifies Prefect for workflow automation
- **Input**:
  - `user_id`: User identifier
  - `prompt`: Natural language design request
  - `city`: City for compliance
  - `project_id`: Optional project grouping
  - `design_type`: kitchen, house, office, etc.
  - `budget`: Budget in INR
  - `area_sqft`: Area in square feet
  - `notify_prefect`: Send event to Prefect (default true)
- **Output**:
  - `request_id`: Unique request ID
  - `spec_id`: Generated spec ID
  - `design_spec`: Complete design JSON
  - `agents`: Results from all agents (MCP, RL, Geometry)
  - `total_duration_ms`: Total processing time
  - `status`: success/partial/failed

### 43. POST `/bhiv/v1/feedback`
- **Purpose**: Submit feedback for BHIV-generated designs
- **Input**:
  - `request_id`: BHIV request ID
  - `spec_id`: Design spec ID
  - `rating`: 0-5 rating
  - `feedback_type`: explicit/implicit
  - `notes`: Optional notes
  - `aspect_ratings`: Ratings for specific aspects
- **Output**:
  - Feedback ID
  - Training queue status

### 44. GET `/bhiv/v1/health`
- **Purpose**: BHIV assistant health check
- **Output**: Service status, version, timestamp

---

## 🤖 BHIV Integrated Design Endpoint

### 45. POST `/bhiv/v1/design`
- **Purpose**: Generate complete design with compliance and RL optimization
- **Process**:
  1. Generate spec from prompt (internal LM)
  2. Run Sohum's MCP compliance check
  3. Run Ranjeet's RL optimization
  4. Aggregate results
- **Input**:
  - `user_id`: User identifier
  - `prompt`: Design request
  - `city`: City for compliance
  - `project_id`: Optional project ID
  - `context`: Additional parameters
- **Output**:
  - `request_id`: Request ID
  - `spec_id`: Spec ID
  - `spec_json`: Design JSON
  - `preview_url`: Preview URL
  - `compliance`: Compliance result
  - `rl_optimization`: RL optimization result
  - `processing_time_ms`: Processing time

### 46. POST `/bhiv/v1/process_with_workflow`
- **Purpose**: Process design with integrated workflow orchestration
- **Additional**: Handles PDF processing via Prefect workflows
- **Output**: Same as `/bhiv/v1/design` plus workflow info

---

## 🤖 BHIV Automation & Workflow Endpoints

### 47. GET `/api/v1/automation/status`
- **Purpose**: Get BHIV automation system status
- **Output**:
  - Automation system status
  - External service health
  - Available workflows
  - Recent workflow executions (last 10)
  - Total execution count

### 48. POST `/api/v1/automation/pdf-compliance`
- **Purpose**: Trigger PDF compliance automation workflow
- **Input**:
  - `pdf_url`: PDF document URL
  - `city`: City for rules
  - `sohum_url`: Soham service URL
- **Output**: Workflow trigger confirmation

### 49. POST `/api/v1/automation/workflow`
- **Purpose**: Trigger any BHIV automation workflow
- **Workflow Types**:
  - `pdf_compliance`: PDF processing
  - `design_optimization`: Design optimization
  - `health_monitoring`: System health monitoring
- **Input**:
  - `workflow_type`: Type of workflow
  - `parameters`: Workflow parameters
- **Output**:
  - Workflow ID
  - Run ID
  - Status endpoint URL
  - Traceable execution info

### 50. GET `/api/v1/automation/workflow/{flow_run_id}/status`
- **Purpose**: Get real-time status of specific workflow run
- **Output**:
  - Workflow status
  - Execution details
  - Database record info
  - Result/error info

---

## 🏙️ Multi-City Support Endpoints

### 51. POST `/api/v1/rl/feedback/city`
- **Purpose**: Submit city-specific RL feedback
- **Supported Cities**: Mumbai, Pune, Nashik, Ahmedabad, Bangalore
- **Input**:
  - `city`: City name
  - `user_rating`: Rating
  - `design_spec`: Design JSON
  - `compliance_result`: Compliance data
- **Output**: Feedback ID

### 52. GET `/api/v1/rl/feedback/city/{city}/summary`
- **Purpose**: Get feedback summary for specific city
- **Output**: Statistics and distribution

---

## 🔍 Data Privacy & Audit Endpoints

### 53. Data Privacy Endpoints (prefix: `/api/v1`)
- **Purpose**: Handle data privacy and GDPR compliance
- **Features**: Data export, deletion, consent management

### 54. Data Audit Endpoints (prefix: `/api/v1`)
- **Purpose**: Track data access and modifications
- **Features**: Audit logs, integrity checks

---

## 🔧 Integration & Monitoring Endpoints

### 55. Integration Layer Endpoints
- **Purpose**: Modular separation and dependency mapping
- **Features**: System analysis, overlap detection

### 56. Workflow Consolidation Endpoints
- **Purpose**: Prefect-based workflow management (replaces N8N)
- **Features**: Workflow deployment, monitoring

### 57. Multi-City Testing Endpoints
- **Purpose**: Test multi-city functionality
- **Features**: City-specific testing, validation

### 58. Geometry Generator Endpoints
- **Purpose**: 3D geometry generation
- **Features**: GLB/STL file generation

### 59. Monitoring System Endpoints
- **Purpose**: System monitoring and alerting
- **Features**: Performance tracking, error logging

---

## 🔑 Key Features Summary

### External Service Integrations:
1. **Sohum's MCP Service**: Compliance checking against city regulations
2. **Ranjeet's RL Service**: Reinforcement learning optimization
3. **Prefect Cloud**: Workflow automation and orchestration
4. **Supabase**: Storage for geometry, previews, compliance files
5. **Sentry**: Error tracking and monitoring

### Storage Buckets:
- `geometry`: 3D geometry files (GLB, STL)
- `previews`: Preview images and files
- `compliance`: Compliance reports (ZIP)
- `files`: General file uploads

### Database Tables:
- `users`: User accounts
- `specs`: Design specifications
- `iterations`: Design iterations
- `evaluations`: User evaluations
- `compliance_checks`: Compliance results
- `rl_feedback`: RL training feedback
- `vr_renders`: VR rendering jobs
- `workflow_runs`: Prefect workflow executions
- `reports`: Custom reports
- `audit_logs`: Data audit trail

### AI/ML Components:
- **Language Model (LM)**: Design generation from prompts
- **Reward Model**: RLHF training
- **PPO Policy**: Reinforcement learning optimization
- **NLP Parser**: Natural language material switching

### Cost Estimation:
- Design type-based rates (₹/sqm)
- Material premium multipliers
- Special object premiums
- City-specific adjustments

### Supported Cities:
- Mumbai
- Pune
- Nashik
- Ahmedabad
- Bangalore
- Delhi

### Design Types:
- House, Building, Office
- Kitchen, Bedroom, Bathroom, Living Room
- Car Body, PCB, Components

---

## 🔒 Authentication & Security

- **JWT-based authentication** for all protected endpoints
- **Token refresh** mechanism
- **Role-based access** (user, admin, demo)
- **Sentry integration** for error tracking
- **CORS middleware** for frontend integration
- **Rate limiting** middleware
- **Data privacy** compliance

---

## 📊 Monitoring & Observability

- **Prometheus metrics** at `/api/v1/metrics`
- **Health checks** at multiple levels
- **Request/response logging**
- **Performance tracking**
- **Error alerting** via Sentry
- **Workflow execution tracking**

---

## 🚀 Deployment & Infrastructure

- **Docker support** with docker-compose
- **Nginx configuration** for production
- **Backup and rollback** scripts
- **Health check** scripts
- **CI/CD pipelines** (.github/workflows)
- **Environment-based configuration**

---

## 📝 Total Endpoint Count: **59+ endpoints**

This backend provides a complete design generation platform with AI, compliance checking, workflow automation, and multi-city support.
