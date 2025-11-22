"""
BHIV AI Assistant - Fully Integrated with Backend
Uses existing backend infrastructure and dependencies
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

import httpx
from app.config import settings
from app.lm_adapter import run_local_lm
from app.utils import create_new_spec_id
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bhiv/v1", tags=["BHIV AI Assistant"])


# Request/Response Models
class DesignRequest(BaseModel):
    """User request for design generation"""

    user_id: str
    prompt: str = Field(description="Natural language design prompt")
    city: str = Field(description="City for compliance (Mumbai, Pune, etc.)")
    project_id: Optional[str] = None
    context: Optional[Dict] = {}


class ComplianceResult(BaseModel):
    """Compliance check result"""

    compliant: bool
    violations: List[str] = []
    geometry_url: Optional[str] = None
    case_id: Optional[str] = None


class RLOptimization(BaseModel):
    """RL optimization result"""

    optimized_layout: Dict
    confidence: float
    reward_score: float


class BHIVResponse(BaseModel):
    """Unified BHIV Assistant response"""

    request_id: str
    spec_id: str
    spec_json: Dict
    preview_url: str
    compliance: ComplianceResult
    rl_optimization: Optional[RLOptimization] = None
    processing_time_ms: int
    timestamp: datetime


async def call_sohum_compliance(spec_json: Dict, city: str, project_id: str) -> Dict:
    """Call Sohum's MCP compliance endpoint"""
    sohum_url = getattr(settings, "SOHAM_URL", "https://ai-rule-api-w7z5.onrender.com")
    url = f"{sohum_url}/compliance/run_case"

    payload = {"spec_json": spec_json, "city": city, "project_id": project_id}

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Sohum compliance check failed: {e}")
        return {
            "compliant": False,
            "violations": [f"Compliance check service unavailable: {str(e)}"],
            "geometry_url": None,
            "case_id": None,
        }


async def call_ranjeet_rl(spec_json: Dict, city: str) -> Optional[Dict]:
    """Call Ranjeet's RL optimization endpoint"""
    yotta_url = getattr(settings, "YOTTA_URL", "https://api.yotta.com")
    url = f"{yotta_url}/rl/predict"

    headers = {}
    yotta_key = getattr(settings, "YOTTA_API_KEY_RL", None)
    if yotta_key:
        headers["Authorization"] = f"Bearer {yotta_key}"

    payload = {"spec_json": spec_json, "city": city, "constraints": {}}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.warning(f"RL optimization failed: {e}")
        return None


@router.post("/design", response_model=BHIVResponse)
async def create_design(request: DesignRequest):
    """
    Generate complete design with compliance and RL optimization

    Orchestrates:
    1. Task 7: Generate spec from natural language prompt (internal)
    2. Sohum's MCP: Run compliance check
    3. Ranjeet's RL: Optimize land utilization
    """
    start_time = datetime.now()
    request_id = f"bhiv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        # STEP 1: Generate spec using internal LM adapter
        logger.info(f"[{request_id}] Step 1: Generating spec internally...")

        params = {
            "user_id": request.user_id,
            "strategy": request.context.get("style", "modern"),
            "extracted_dimensions": request.context.get("dimensions", {}),
        }

        lm_result = run_local_lm(request.prompt, params)
        spec_id = create_new_spec_id()

        spec_result = {
            "spec_id": spec_id,
            "spec_json": lm_result["spec_json"],
            "preview_url": f"https://bhiv-previews.s3.amazonaws.com/{spec_id}.glb",
        }

        # STEP 2: Run compliance check
        logger.info(f"[{request_id}] Step 2: Running compliance check...")
        compliance_result = await call_sohum_compliance(
            spec_result["spec_json"], request.city, request.project_id or request_id
        )

        # STEP 3: Get RL optimization (optional)
        rl_result = None
        try:
            logger.info(f"[{request_id}] Step 3: Getting RL optimization...")
            rl_result = await call_ranjeet_rl(spec_result["spec_json"], request.city)
        except Exception as e:
            logger.warning(f"[{request_id}] RL optimization failed (non-blocking): {e}")

        # STEP 4: Aggregate response
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

        return BHIVResponse(
            request_id=request_id,
            spec_id=spec_result["spec_id"],
            spec_json=spec_result["spec_json"],
            preview_url=spec_result["preview_url"],
            compliance=ComplianceResult(**compliance_result),
            rl_optimization=RLOptimization(**rl_result) if rl_result else None,
            processing_time_ms=processing_time,
            timestamp=datetime.now(),
        )

    except Exception as e:
        logger.error(f"[{request_id}] Error in design generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Design generation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for BHIV Assistant"""
    health = {"bhiv": "ok", "task7_internal": "ok", "sohum_mcp": "unknown", "ranjeet_rl": "unknown"}

    # Test external systems
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Test Sohum MCP
        try:
            sohum_url = getattr(settings, "SOHAM_URL", "https://ai-rule-api-w7z5.onrender.com")
            response = await client.get(f"{sohum_url}/health")
            health["sohum_mcp"] = "ok" if response.status_code == 200 else "error"
        except:
            health["sohum_mcp"] = "unreachable"

        # Test Ranjeet RL
        try:
            yotta_url = getattr(settings, "YOTTA_URL", "https://api.yotta.com")
            response = await client.get(f"{yotta_url}/health")
            health["ranjeet_rl"] = "ok" if response.status_code == 200 else "error"
        except:
            health["ranjeet_rl"] = "unreachable"

    return health
