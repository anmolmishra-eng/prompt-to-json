import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time

import sentry_sdk
from app.api import (
    auth,
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
from app.utils import setup_logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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
    import torch

    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        logger.info(f"✅ Local GPU connected: {gpu_name}")
    else:
        logger.warning("❌ No GPU available - using CPU")
except ImportError:
    logger.warning("❌ PyTorch not available")

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

# Check database connection
try:
    from app.database import engine
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("✅ Database connected")
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")

app = FastAPI(title="Design Engine API")

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
app.include_router(switch.router, prefix="/api/v1", tags=["🎨 Core Design Engine"])
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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
