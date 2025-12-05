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
    core,
    data_privacy,
    evaluate,
    generate,
    health,
    history,
    iterate,
    mobile,
    reports,
    rl,
    switch,
    vr,
)
from app.config import settings
from app.multi_city.city_data_loader import city_router
from app.utils import setup_logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# Check GPU availability
try:
    from app.gpu_detector import gpu_detector

    gpu_info = gpu_detector.detect_gpu()
    if gpu_info["cuda_available"]:
        best_gpu = gpu_detector.get_best_gpu()
        gpu_name = best_gpu["name"] if best_gpu else "Unknown GPU"
        logger.info(f"GPU connected: {gpu_name} (Method: {gpu_info['detection_method']})")
    else:
        logger.info("Using CPU mode (GPU not available)")
except ImportError:
    logger.info("GPU detector not available - using CPU mode")

# Check Supabase connection
try:
    from supabase import create_client

    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    logger.info(f"✅ Supabase connected: {settings.SUPABASE_URL}")
except Exception as e:
    logger.error(f"❌ Supabase connection failed: {e}")

# Check Yotta configuration
if settings.YOTTA_API_KEY and settings.YOTTA_URL:
    logger.info(f"✅ Yotta configured: {settings.YOTTA_URL}")
else:
    logger.warning("❌ Yotta not configured")

# Initialize storage and validate database
try:
    from app.database_validator import validate_database
    from app.storage_manager import ensure_storage_ready

    # Ensure all storage directories exist
    storage_ready = ensure_storage_ready()
    if storage_ready:
        logger.info("✅ Storage system initialized")
    else:
        logger.warning("⚠️ Some storage paths failed validation")

    # Validate database
    db_ready = validate_database()
    if db_ready:
        logger.info("✅ Database validated and ready")
    else:
        logger.warning("⚠️ Database validation issues detected")

except Exception as e:
    logger.error(f"❌ Storage/Database initialization failed: {e}")

app = FastAPI(title="Design Engine API")


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


# Initialize Prometheus metrics
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(app)

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


# Include routers in logical sequence
# 1. Authentication & Security
app.include_router(auth.router, prefix="/api/v1/auth", tags=["🔐 Authentication"])
app.include_router(data_privacy.router, prefix="/api/v1", tags=["🔐 Data Privacy"])

# 2. System Health & Monitoring
app.include_router(health.router, prefix="/api/v1", tags=["📊 Monitoring & Health"])

# 3. Core Design Engine (Main Workflow)
app.include_router(generate.router, prefix="/api/v1", tags=["🎨 Core Design Engine"])
app.include_router(evaluate.router, prefix="/api/v1", tags=["🎨 Core Design Engine"])
app.include_router(iterate.router, prefix="/api/v1", tags=["🎨 Core Design Engine"])
app.include_router(switch.router, tags=["🎨 Core Design Engine"])
app.include_router(history.router, prefix="/api/v1", tags=["🎨 Core Design Engine"])

# 4. Core Operations & Management
app.include_router(core.router, prefix="/api/v1", tags=["⚙️ Core Operations"])

# 5. Compliance & Validation
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["✅ Compliance & Validation"])

# 6. File Management & Reports
app.include_router(reports.router, prefix="/api/v1", tags=["📁 File Management & Reports"])

# 7. Platform Integrations
app.include_router(mobile.router, prefix="/api/v1", tags=["📱 Mobile Integration"])
app.include_router(vr.router, prefix="/api/v1", tags=["🥽 VR/AR Integration"])

# 8. AI Training & Optimization
app.include_router(rl.router, prefix="/api/v1", tags=["🤖 RL/RLHF Training"])

# 9. Multi-City Support
app.include_router(city_router, prefix="/api/v1", tags=["🏙️ Multi-City Support"])

# 10. BHIV AI Assistant (Task 8)
app.include_router(bhiv_assistant.router, tags=["🧠 BHIV AI Assistant"])
app.include_router(bhiv_integrated.router, tags=["🤖 BHIV AI Assistant"])

# 11. Workflow Management
from app.api import workflow_management

app.include_router(workflow_management.router, prefix="/api/v1", tags=["⚙️ Workflow Management"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
