"""
BHIV Assistant Main Application
FastAPI app for BHIV AI Assistant layer
"""

import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Simple imports without relative paths
try:
    from app.bhiv_assistant.config.integration_config import IntegrationConfig
except ImportError:
    IntegrationConfig = None

from app.bhiv_assistant.app.bhiv_layer.assistant_api import router as bhiv_router
from app.bhiv_assistant.app.bhiv_layer.main_api import app as bhiv_main_api
from app.bhiv_assistant.app.bhiv_layer.rl_feedback_handler import rl_router
from app.bhiv_assistant.app.mcp.mcp_client import mcp_router

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Config
config = IntegrationConfig() if IntegrationConfig else None

# App
app = FastAPI(
    title="BHIV AI Assistant", description="Unified AI Assistant Layer for Multi-Agent Design System", version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bhiv_router)
app.include_router(mcp_router)
app.include_router(rl_router)

# Mount BHIV main API
app.mount("/api", bhiv_main_api)

# Mount Prefect-FastAPI integration
from app.bhiv_assistant.app.bhiv_layer.prefect_fastapi_integration import app as prefect_api

app.mount("/prefect", prefect_api)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "BHIV AI Assistant",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "design": "/bhiv/v1/design",
            "health": "/bhiv/v1/health",
            "mcp_rules": "/mcp/rules/{city}",
            "rl_feedback": "/rl/feedback",
        },
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main_bhiv:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info",
    )
