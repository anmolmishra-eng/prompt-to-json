"""
Workflow Management API - MINIMAL FOR BHIV AI ASSISTANT
Only essential automation endpoints for AI assistant workflows
"""
import logging
from typing import Dict

from app.external_services import get_service_health_status
from app.prefect_integration_minimal import check_workflow_status, get_workflow_status, trigger_automation_workflow
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/automation", tags=["🤖 BHIV Automations"])


class AutomationRequest(BaseModel):
    """Request for BHIV automation workflows"""

    workflow_type: str  # pdf_compliance, design_optimization, health_monitoring
    parameters: Dict


class PDFComplianceRequest(BaseModel):
    """PDF compliance automation request"""

    pdf_url: str
    city: str
    sohum_url: str = "https://ai-rule-api-w7z5.onrender.com"


@router.get("/status")
async def get_automation_status():
    """Get BHIV automation system status - ESSENTIAL"""
    try:
        workflow_status = await check_workflow_status()
        service_status = await get_service_health_status()

        return {
            "automation_system": workflow_status,
            "external_services": service_status,
            "available_workflows": ["pdf_compliance", "design_optimization", "health_monitoring"],
            "status": "operational" if workflow_status.get("prefect_available") else "limited",
        }
    except Exception as e:
        logger.error(f"Failed to get automation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pdf-compliance")
async def trigger_pdf_compliance(request: PDFComplianceRequest):
    """Trigger PDF compliance automation - ESSENTIAL for BHIV"""
    try:
        parameters = {"pdf_url": request.pdf_url, "city": request.city, "sohum_url": request.sohum_url}
        result = await trigger_automation_workflow("pdf_compliance", parameters)
        return result
    except Exception as e:
        logger.error(f"PDF compliance automation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow")
async def trigger_workflow(request: AutomationRequest):
    """Trigger any BHIV automation workflow - ESSENTIAL"""
    try:
        result = await trigger_automation_workflow(workflow_type=request.workflow_type, parameters=request.parameters)
        return result
    except Exception as e:
        logger.error(f"Automation workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{flow_run_id}/status")
async def get_workflow_run_status(flow_run_id: str):
    """Get status of specific workflow run - ESSENTIAL for monitoring"""
    try:
        result = await get_workflow_status(flow_run_id)
        return result
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
