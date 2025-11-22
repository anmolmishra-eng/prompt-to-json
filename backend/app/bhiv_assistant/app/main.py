"""
BHIV Assistant Main Application
"""

import logging
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.bhiv_layer.assistant_api import router as bhiv_router
from app.mcp.mcp_client import mcp_router
from app.bhiv_layer.rl_feedback_handler import rl_router
from config.integration_config import IntegrationConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 BHIV Assistant starting up...")
    yield
    logger.info("🛑 BHIV Assistant shutting down...")


# Create FastAPI app
app = FastAPI(
    title="BHIV AI Assistant",
    description="Orchestration layer for Task 7, Sohum's MCP, and Ranjeet's RL systems",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bhiv_router)
app.include_router(mcp_router)
app.include_router(rl_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "BHIV AI Assistant",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "design": "/bhiv/v1/design",
            "health": "/bhiv/v1/health",
            "mcp": "/mcp",
            "rl": "/rl",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "ok", "service": "bhiv-assistant"}


if __name__ == "__main__":
    import uvicorn
    
    config = IntegrationConfig()
    
    uvicorn.run(
        "app.main:app",
        host=config.bhiv.api_host,
        port=config.bhiv.api_port,
        reload=True,
        log_level="info"
    )