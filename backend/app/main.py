import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time

import sentry_sdk
from app.api import (
    auth,
    bhiv_assistant,
    bhiv_integrated,
    compliance,
    data_privacy,
    evaluate,
    generate,
    geometry_generator,
    health,
    history,
    integration_layer,
    iterate,
    mcp_integration,
    mock_rl,
    monitoring_system,
    multi_city_testing,
    reports,
    rl,
    switch,
    workflow_consolidation,
)

# BHIV AI Assistant: Both bhiv_assistant.py and bhiv_integrated.py are included
# bhiv_assistant.py: Main orchestration layer (/bhiv/v1/prompt)
# bhiv_integrated.py: Integrated design endpoint (/bhiv/v1/design)
from app.config import settings
from app.database import get_current_user
from app.multi_city.city_data_loader import city_router
from app.utils import setup_logging
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(),
        ],
        traces_sample_rate=1.0,
        environment=settings.ENVIRONMENT,
        send_default_pii=True,
    )
    logger.info("✅ Sentry initialized and connected")
else:
    logger.warning("❌ Sentry not configured")

# Lazy GPU detection - only when needed
try:
    from app.gpu_detector import gpu_detector

    logger.info("GPU detector loaded (detection deferred)")
except ImportError:
    logger.info("GPU detector not available - using CPU mode")

# Lazy Supabase connection - only when needed
try:
    from supabase import create_client

    logger.info(f"Supabase client loaded (connection deferred): {settings.SUPABASE_URL}")
except Exception as e:
    logger.error(f"❌ Supabase client loading failed: {e}")

# Check Yotta configuration
if settings.YOTTA_API_KEY and settings.YOTTA_URL:
    logger.info(f"✅ Yotta configured: {settings.YOTTA_URL}")
else:
    logger.warning("❌ Yotta not configured")

# Lazy initialization - validate on first use
try:
    from app.database_validator import validate_database
    from app.storage_manager import ensure_storage_ready

    logger.info("Storage and database modules loaded (validation deferred)")
except Exception as e:
    logger.error(f"❌ Storage/Database module loading failed: {e}")

# JWT Security scheme
security = HTTPBearer()

app = FastAPI(
    title="Design Engine API",
    description="Complete FastAPI backend for design generation with JWT authentication",
    version="0.1.0",
)


# Global exception handler for consistent error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": exc.detail, "status_code": exc.status_code}},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error", "status_code": 500}},
    )


# Essential metrics only for BHIV automations
if settings.ENABLE_METRICS:
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        excluded_handlers=["/metrics", "/docs", "/openapi.json"],
        env_var_name="ENABLE_METRICS",
    )
    instrumentator.instrument(app).expose(app, tags=["📊 Metrics"])
    logger.info("✅ Essential metrics enabled")
else:
    logger.info("📊 Metrics disabled")

# CORS middleware - TODO: Update with actual frontend origins
# Yash & Bhavesh: Provide your frontend URLs to replace ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Alternative dev port
        "https://staging.bhiv.com",  # Staging (update with actual)
        "https://app.bhiv.com",  # Production (update with actual)
        "*",  # Remove this in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Force-Update"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log incoming request
    logger.info(
        f"Request: {request.method} {request.url.path} " f"from {request.client.host if request.client else 'unknown'}"
    )

    response = await call_next(request)

    # Log response with timing
    process_time = time.time() - start_time
    logger.info(
        f"Response: {request.method} {request.url.path} " f"status={response.status_code} duration={process_time:.3f}s"
    )

    return response


# ============================================================================
# PUBLIC ENDPOINTS (No Authentication Required)
# ============================================================================


# Basic public health check
@app.get("/health", tags=["📊 Public Health"])
async def basic_health_check():
    """Basic health check - no authentication required"""
    return {"status": "ok", "service": "Design Engine API", "version": "0.1.0"}


# Authentication endpoints
app.include_router(auth.router, prefix="/api/v1/auth", tags=["🔐 Authentication"])

# ============================================================================
# PROTECTED ENDPOINTS (JWT Authentication Required)
# ============================================================================

# 1. System Health & Monitoring
app.include_router(health.router, prefix="/api/v1", tags=["📊 System Health"], dependencies=[Depends(get_current_user)])
app.include_router(monitoring_system.router, dependencies=[Depends(get_current_user)])

# 2. Data Privacy & Security
app.include_router(
    data_privacy.router, prefix="/api/v1", tags=["🔐 Data Privacy"], dependencies=[Depends(get_current_user)]
)

# 3. Core Design Engine (Sequential Workflow)
app.include_router(
    generate.router, prefix="/api/v1", tags=["🎨 Design Generation"], dependencies=[Depends(get_current_user)]
)
app.include_router(
    evaluate.router, prefix="/api/v1", tags=["📊 Design Evaluation"], dependencies=[Depends(get_current_user)]
)
app.include_router(
    iterate.router, prefix="/api/v1", tags=["🔄 Design Iteration"], dependencies=[Depends(get_current_user)]
)
app.include_router(switch.router, dependencies=[Depends(get_current_user)])
app.include_router(
    history.router, prefix="/api/v1", tags=["📚 Design History"], dependencies=[Depends(get_current_user)]
)

# 4. Compliance & Validation
app.include_router(
    compliance.router,
    prefix="/api/v1/compliance",
    tags=["✅ Compliance & Validation"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(mcp_integration.router, dependencies=[Depends(get_current_user)])

# 5. Multi-City Support
app.include_router(city_router, prefix="/api/v1", tags=["🏙️ Multi-City"], dependencies=[Depends(get_current_user)])

# Multi-city RL feedback endpoint
from app.multi_city.rl_feedback_integration import multi_city_rl


@app.post("/api/v1/rl/feedback/city", tags=["🏙️ Multi-City"])
async def city_rl_feedback(
    city: str, design_spec: dict, user_rating: float, compliance_result: dict, current_user=Depends(get_current_user)
):
    """Submit city-specific RL feedback"""
    feedback_id = await multi_city_rl.collect_city_feedback(city, design_spec, user_rating, compliance_result)
    return {"feedback_id": feedback_id, "city": city, "status": "success"}


# 6. BHIV AI Assistant (Main Features)
app.include_router(bhiv_assistant.router, dependencies=[Depends(get_current_user)])
app.include_router(bhiv_integrated.router, dependencies=[Depends(get_current_user)])

# 7. BHIV Automations & Workflows
from app.api import workflow_management

app.include_router(
    workflow_management.router, prefix="/api/v1", tags=["🤖 BHIV Automations"], dependencies=[Depends(get_current_user)]
)

# 8. File Management
app.include_router(
    reports.router, prefix="/api/v1", tags=["📁 File Management"], dependencies=[Depends(get_current_user)]
)

# 9. Machine Learning & Training
app.include_router(rl.router, prefix="/api/v1", tags=["🤖 RL Training"], dependencies=[Depends(get_current_user)])

# 9.1 Mock RL System (Land Utilization - Ranjeet's service)
app.include_router(mock_rl.router, tags=["🔄 Mock RL System"])

# 9.2 Integration Layer (Modular Separation & Dependency Mapping)
app.include_router(integration_layer.router, dependencies=[Depends(get_current_user)])

# 9.3 Workflow Consolidation (Prefect-based, replaces N8N)
app.include_router(workflow_consolidation.router, dependencies=[Depends(get_current_user)])

# 9.4 Multi-City Testing & Integration
app.include_router(multi_city_testing.router, dependencies=[Depends(get_current_user)])

# 10. 3D Geometry Generation
app.include_router(geometry_generator.router, dependencies=[Depends(get_current_user)])


# Note: /api/v1/rl/feedback/city/{city}/summary endpoint is handled by rl.router


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
