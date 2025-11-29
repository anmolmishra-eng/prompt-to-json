"""
Prefect Integration Module
Connects Prefect workflows with main API endpoints
"""
import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

try:
    from prefect import get_client
    from workflows.pdf_to_mcp_flow import pdf_to_mcp_flow

    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False
    logger.warning("Prefect not available, using direct execution")


async def trigger_pdf_workflow(pdf_url: str, city: str, sohum_url: str) -> Dict:
    """Trigger PDF to MCP workflow"""
    if PREFECT_AVAILABLE:
        try:
            # Run as Prefect flow
            result = await pdf_to_mcp_flow(pdf_url, city, sohum_url)
            return {"status": "success", "workflow": "prefect", "result": result}
        except Exception as e:
            logger.error(f"Prefect workflow failed: {e}")
            # Fallback to direct execution
            return await _direct_pdf_processing(pdf_url, city, sohum_url)
    else:
        return await _direct_pdf_processing(pdf_url, city, sohum_url)


async def _direct_pdf_processing(pdf_url: str, city: str, sohum_url: str) -> Dict:
    """Direct PDF processing without Prefect"""
    try:
        # Import workflow functions directly
        from workflows.pdf_to_mcp_flow import (
            cleanup_temp_files,
            download_pdf_from_storage,
            extract_text_from_pdf,
            parse_compliance_rules,
            send_rules_to_mcp,
        )

        # Execute workflow steps directly
        local_path = f"temp/{city}_compliance.pdf"
        pdf_path = download_pdf_from_storage(pdf_url, local_path)
        text_content = extract_text_from_pdf(pdf_path)
        rules = parse_compliance_rules(text_content, city)
        success = await send_rules_to_mcp(rules, sohum_url)
        cleanup_temp_files(pdf_path)

        return {
            "status": "success",
            "workflow": "direct",
            "result": {"city": city, "rules_count": len(rules["rules"]), "success": success},
        }
    except Exception as e:
        logger.error(f"Direct PDF processing failed: {e}")
        return {"status": "error", "message": str(e)}


async def check_workflow_status() -> Dict:
    """Check status of workflow system"""
    if PREFECT_AVAILABLE:
        try:
            client = get_client()
            # Simple connectivity check
            return {"prefect": "available", "mode": "workflow"}
        except Exception as e:
            return {"prefect": "error", "mode": "direct", "error": str(e)}
    else:
        return {"prefect": "unavailable", "mode": "direct"}
