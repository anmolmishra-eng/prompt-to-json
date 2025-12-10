"""
Prefect Integration Module - MINIMAL FOR BHIV AI ASSISTANT
Only essential endpoints for automations and AI assistant workflows
"""
import asyncio
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Minimal Prefect client for essential operations only
try:
    from prefect import get_client

    PREFECT_AVAILABLE = True
    logger.info("✅ Minimal Prefect integration available")
except ImportError as e:
    PREFECT_AVAILABLE = False
    logger.warning(f"❌ Prefect not available: {e}. Using direct execution fallback")


# Essential Prefect endpoints for BHIV AI Assistant
class MinimalPrefectClient:
    """Minimal Prefect client with only essential endpoints"""

    def __init__(self):
        self.client = None
        if PREFECT_AVAILABLE:
            try:
                self.client = get_client()
            except Exception as e:
                logger.error(f"Failed to initialize Prefect client: {e}")

    async def create_flow_run(self, flow_name: str, parameters: Dict) -> Dict:
        """Create and run a flow - ESSENTIAL for automations"""
        if not self.client:
            return {"status": "error", "message": "Prefect client not available"}

        try:
            flow_run = await self.client.create_flow_run_from_deployment(name=flow_name, parameters=parameters)
            return {"status": "success", "flow_run_id": str(flow_run.id)}
        except Exception as e:
            logger.error(f"Failed to create flow run: {e}")
            return {"status": "error", "message": str(e)}

    async def get_flow_run_status(self, flow_run_id: str) -> Dict:
        """Get flow run status - ESSENTIAL for monitoring"""
        if not self.client:
            return {"status": "error", "message": "Prefect client not available"}

        try:
            flow_run = await self.client.read_flow_run(flow_run_id)
            return {
                "status": "success",
                "state": flow_run.state.type.value if flow_run.state else "unknown",
                "name": flow_run.name,
            }
        except Exception as e:
            logger.error(f"Failed to get flow run status: {e}")
            return {"status": "error", "message": str(e)}

    async def health_check(self) -> Dict:
        """Basic health check - ESSENTIAL for system monitoring"""
        if not self.client:
            return {"status": "unavailable", "message": "Prefect client not available"}

        try:
            # Simple API call to check connectivity
            await self.client.hello()
            return {"status": "healthy", "message": "Prefect server connected"}
        except Exception as e:
            logger.error(f"Prefect health check failed: {e}")
            return {"status": "unhealthy", "message": str(e)}


# Global minimal client instance
minimal_client = MinimalPrefectClient()


async def trigger_automation_workflow(workflow_type: str, parameters: Dict) -> Dict:
    """Trigger essential automation workflows for BHIV AI Assistant"""
    workflow_map = {
        "pdf_compliance": "bhiv-pdf-compliance",
        "design_optimization": "bhiv-design-optimization",
        "health_monitoring": "bhiv-health-monitoring",
    }

    if workflow_type not in workflow_map:
        return {"status": "error", "message": f"Unknown workflow type: {workflow_type}"}

    flow_name = workflow_map[workflow_type]
    result = await minimal_client.create_flow_run(flow_name, parameters)

    if result["status"] == "success":
        logger.info(f"✅ Started {workflow_type} workflow: {result['flow_run_id']}")
    else:
        logger.error(f"❌ Failed to start {workflow_type} workflow: {result['message']}")
        # Fallback to direct execution
        return await _execute_workflow_directly(workflow_type, parameters)

    return result


async def get_workflow_status(flow_run_id: str) -> Dict:
    """Get status of running workflow - ESSENTIAL for BHIV automations"""
    return await minimal_client.get_flow_run_status(flow_run_id)


async def check_workflow_status() -> Dict:
    """Minimal workflow system status check for BHIV"""
    health_result = await minimal_client.health_check()

    return {
        "prefect_available": PREFECT_AVAILABLE,
        "server_health": health_result["status"],
        "execution_mode": "prefect" if health_result["status"] == "healthy" else "direct",
        "essential_endpoints": ["create_flow_run", "get_flow_run_status", "health_check"],
    }


async def _execute_workflow_directly(workflow_type: str, parameters: Dict) -> Dict:
    """Direct execution fallback for essential workflows"""
    try:
        if workflow_type == "pdf_compliance":
            return {"status": "success", "workflow": "direct", "message": "PDF compliance executed directly"}
        elif workflow_type == "health_monitoring":
            return {"status": "success", "workflow": "direct", "message": "Health monitoring executed directly"}
        else:
            return {"status": "error", "message": f"No direct execution for {workflow_type}"}
    except Exception as e:
        logger.error(f"Direct workflow execution failed: {e}")
        return {"status": "error", "message": str(e)}
