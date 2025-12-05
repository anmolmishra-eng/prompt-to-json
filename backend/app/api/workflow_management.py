"""
Workflow Management API
Provides endpoints for managing and monitoring workflows
"""
import logging
from typing import Dict

from app.external_services import get_service_health_status, initialize_external_services
from app.prefect_integration_enhanced import (
    check_workflow_status,
    get_workflow_capabilities,
    trigger_health_monitoring_workflow,
    trigger_pdf_workflow,
)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/workflow", tags=["Workflow Management"])


class PDFWorkflowRequest(BaseModel):
    pdf_url: str
    city: str
    sohum_url: str = "https://ai-rule-api-w7z5.onrender.com"


@router.get("/status")
async def get_workflow_status():
    """Get comprehensive workflow system status"""
    try:
        workflow_status = await check_workflow_status()
        service_status = await get_service_health_status()
        capabilities = await get_workflow_capabilities()

        return {
            "workflow_system": workflow_status,
            "external_services": service_status,
            "capabilities": capabilities,
            "overall_status": "operational" if workflow_status.get("status") != "unavailable" else "limited",
        }
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pdf/process")
async def process_pdf_workflow(request: PDFWorkflowRequest):
    """Trigger PDF processing workflow"""
    try:
        result = await trigger_pdf_workflow(pdf_url=request.pdf_url, city=request.city, sohum_url=request.sohum_url)
        return result
    except Exception as e:
        logger.error(f"PDF workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health/monitor")
async def trigger_health_monitoring():
    """Trigger health monitoring workflow for all external services"""
    try:
        result = await trigger_health_monitoring_workflow()
        return result
    except Exception as e:
        logger.error(f"Health monitoring workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities")
async def get_capabilities():
    """Get available workflow capabilities"""
    try:
        return await get_workflow_capabilities()
    except Exception as e:
        logger.error(f"Failed to get capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/services/initialize")
async def initialize_services():
    """Initialize and health check all external services"""
    try:
        result = await initialize_external_services()
        return {
            "status": "completed",
            "services": result,
            "message": "External services initialized and health checked",
        }
    except Exception as e:
        logger.error(f"Service initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
