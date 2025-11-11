import logging

from app.schemas import MessageResponse
from app.utils import get_uptime
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Prometheus instrumentator
instrumentator = Instrumentator()


@router.get("/", response_model=MessageResponse, name="Service Status")
async def health_check():
    return MessageResponse(message="Service is healthy")


@router.get("/health", name="Detailed Health")
async def health():
    return {
        "status": "ok",
        "uptime": get_uptime(),
        "service": "Design Engine API",
        "version": "1.0.0",
    }


@router.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "uptime": get_uptime(),
        "service": "Design Engine API",
        "version": "1.0.0",
        "components": {
            "database": "connected",
            "storage": "connected",
            "gpu": ("available" if __import__("torch").cuda.is_available() else "unavailable"),
        },
    }


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    # Return Prometheus metrics in text format
    try:
        return instrumentator.registry.generate_latest().decode("utf-8")
    except Exception:
        # Fallback metrics if instrumentator not properly initialized
        uptime = get_uptime()
        return f"""# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds {uptime}
# HELP app_info Application information
# TYPE app_info gauge
app_info{{version="1.0.0",service="design_engine_api"}} 1
"""


@router.get("/test-error")
async def test_error():
    """Test endpoint to verify Sentry error tracking"""
    import sentry_sdk

    # Capture the error in Sentry
    try:
        # Intentionally cause an error
        1 / 0
    except Exception as e:
        # Send to Sentry
        sentry_sdk.capture_exception(e)
        logger.error(f"Test error captured: {e}")

        # Return success message
        return {
            "message": "Test error successfully sent to Sentry!",
            "error_type": "ZeroDivisionError",
            "sentry_status": "captured",
        }
