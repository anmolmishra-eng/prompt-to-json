# Demo Mode - Public API Endpoints

## Overview
In demo/production mode, only whitelisted endpoints are visible in Swagger/OpenAPI documentation.

## Environment Variable
Set `DEMO_MODE=true` (default) to hide internal endpoints from docs.
Set `DEMO_MODE=false` for development to see all endpoints.

## Whitelisted Endpoints (Visible in Swagger)

### 1. Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration (if enabled)

### 2. Design Generation
- `POST /api/v1/generate` - Generate design from prompt

### 3. Compliance & Validation
- `POST /api/v1/compliance/check` - Check design compliance
- `GET /api/v1/compliance/*` - Compliance-related endpoints

### 4. Geometry Generation
- `POST /api/v1/geometry/generate` - Generate 3D geometry
- `GET /api/v1/geometry/*` - Geometry-related endpoints

### 5. Health Check
- `GET /health` - Basic health check (no auth required)

## Hidden Endpoints (Not in Swagger)
All other endpoints are hidden from public documentation:
- RL Training endpoints
- BHIV Assistant endpoints
- Workflow automation endpoints
- Prefect triggers
- Mobile/VR endpoints
- Data audit endpoints
- Multi-city testing endpoints
- Reports and file management
- Design evaluation, iteration, switching
- History endpoints
- Monitoring system

## Accessing Docs
- **Demo Mode (DEMO_MODE=true)**: Docs disabled entirely
- **Dev Mode (DEMO_MODE=false)**:
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc
  - OpenAPI JSON: http://localhost:8000/openapi.json

## Notes
- All hidden endpoints remain functional via direct API calls
- Only the documentation visibility is affected
- JWT authentication still required for protected endpoints
