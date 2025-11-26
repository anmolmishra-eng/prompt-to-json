"""
BHIV AI Assistant Layer - Main API
Orchestrates calls to Task 7, Sohum's MCP, and Ranjeet's RL systems
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

import httpx

try:
    from app.config import settings
except ImportError:
    # Fallback for when running from bhiv_assistant context
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from app.config import settings

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .rl_feedback_handler import RLFeedbackHandler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bhiv/v1", tags=["BHIV Assistant"])


# Request/Response Models
class DesignRequest(BaseModel):
    """User request for design generation"""

    user_id: str
    prompt: str = Field(description="Natural language design prompt")
    city: str = Field(description="City for compliance (Mumbai, Pune, etc.)")
    project_id: Optional[str] = None
    context: Optional[Dict] = {}


class ComplianceResult(BaseModel):
    """Compliance check result from Sohum's system"""

    compliant: bool
    violations: List[str] = []
    geometry_url: Optional[str] = None
    case_id: Optional[str] = None


class RLOptimization(BaseModel):
    """RL optimization from Ranjeet's system"""

    optimized_layout: Dict
    confidence: float
    reward_score: float


class BHIVResponse(BaseModel):
    """Unified BHIV Assistant response"""

    request_id: str
    spec_id: str
    spec_json: Dict

    # From Task 7
    preview_url: str

    # From Sohum MCP
    compliance: ComplianceResult

    # From Ranjeet RL
    rl_optimization: Optional[RLOptimization] = None

    # Metadata
    processing_time_ms: int
    timestamp: datetime


class BHIVAssistant:
    """BHIV AI Assistant orchestration layer"""

    def __init__(self):
        self.http_client = None
        # Initialize RL handler with default values
        self.rl_handler = RLFeedbackHandler(
            base_url=getattr(settings, "RANJEET_RL_URL", "http://localhost:8001"),
            api_key=getattr(settings, "RANJEET_API_KEY", None),
        )

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if not self.http_client:
            self.http_client = httpx.AsyncClient(timeout=60.0)
        return self.http_client

    async def generate_design(self, request: DesignRequest) -> BHIVResponse:
        """
        Main orchestration flow:
        1. Call Task 7 to generate spec from prompt
        2. Call Sohum's MCP for compliance check
        3. Call Ranjeet's RL for optimization (optional)
        4. Aggregate and return unified response
        """
        start_time = datetime.now()
        request_id = f"bhiv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        client = await self._get_client()

        try:
            # STEP 1: Generate spec from prompt (Task 7)
            logger.info(f"[{request_id}] Step 1: Generating spec from Task 7...")
            spec_result = await self._call_task7_generate(client, request)

            # STEP 2: Run compliance check (Sohum's MCP)
            logger.info(f"[{request_id}] Step 2: Running compliance check...")
            compliance_result = await self._call_sohum_compliance(
                client, spec_result["spec_json"], request.city, request.project_id or request_id
            )

            # STEP 3: Get RL optimization (Ranjeet's RL) - Optional
            rl_result = None
            try:
                logger.info(f"[{request_id}] Step 3: Getting RL optimization...")
                rl_result = await self._call_ranjeet_rl(client, spec_result["spec_json"], request.city)

                # Get confidence score for bonus points
                if rl_result:
                    confidence = await self.rl_handler.get_confidence_score(spec_result["spec_json"], request.city)
                    if confidence:
                        rl_result["confidence"] = confidence

            except Exception as e:
                logger.warning(f"[{request_id}] RL optimization failed (non-blocking): {e}")

            # STEP 4: Aggregate response
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return BHIVResponse(
                request_id=request_id,
                spec_id=spec_result["spec_id"],
                spec_json=spec_result["spec_json"],
                preview_url=spec_result.get("preview_url", ""),
                compliance=ComplianceResult(**compliance_result),
                rl_optimization=RLOptimization(**rl_result) if rl_result else None,
                processing_time_ms=processing_time,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"[{request_id}] Error in design generation: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Design generation failed: {str(e)}")

    async def _call_task7_generate(self, client: httpx.AsyncClient, request: DesignRequest) -> Dict:
        """Call Task 7 generate endpoint"""
        url = "http://localhost:8000/api/v1/generate"

        headers = {}
        # Internal call - no auth needed

        payload = {
            "user_id": request.user_id,
            "prompt": request.prompt,
            "project_id": request.project_id or f"bhiv_{request.user_id}",
            "context": {**(request.context or {}), "city": request.city, "source": "bhiv_assistant"},
        }

        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Task 7 generate failed: {e}")
            raise HTTPException(status_code=503, detail=f"Task 7 service unavailable: {str(e)}")

    async def _call_sohum_compliance(
        self, client: httpx.AsyncClient, spec_json: Dict, city: str, project_id: str
    ) -> Dict:
        """Call Sohum's MCP compliance endpoint"""
        sohum_url = getattr(settings, "SOHAM_URL", "https://ai-rule-api-w7z5.onrender.com")
        url = f"{sohum_url}/compliance/run_case"

        headers = {}
        # No auth needed for Sohum's API

        payload = {"spec_json": spec_json, "city": city, "project_id": project_id}

        try:
            response = await client.post(url, json=payload, headers=headers, timeout=90.0)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Sohum compliance check failed: {e}")
            # Return default non-compliant result
            return {
                "compliant": False,
                "violations": [f"Compliance check service unavailable: {str(e)}"],
                "geometry_url": None,
                "case_id": None,
            }

    async def _call_ranjeet_rl(self, client: httpx.AsyncClient, spec_json: Dict, city: str) -> Optional[Dict]:
        """Call Ranjeet's RL optimization endpoint"""
        yotta_url = getattr(settings, "YOTTA_URL", "https://api.yotta.com")
        url = f"{yotta_url}/rl/predict"

        headers = {}
        yotta_key = getattr(settings, "YOTTA_API_KEY_RL", None)
        if yotta_key:
            headers["Authorization"] = f"Bearer {yotta_key}"

        payload = {"spec_json": spec_json, "city": city, "constraints": {}}

        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.warning(f"RL optimization failed: {e}")
            return None


# Create instance
assistant = BHIVAssistant()


# API Endpoints
@router.post("/design", response_model=BHIVResponse)
async def create_design(request: DesignRequest):
    """
    Generate complete design with compliance and RL optimization

    This endpoint orchestrates:
    1. Task 7: Generate spec from natural language prompt
    2. Sohum's MCP: Run compliance check
    3. Ranjeet's RL: Optimize land utilization
    """
    return await assistant.generate_design(request)


@router.get("/health")
async def health_check():
    """Health check for BHIV Assistant"""
    client = await assistant._get_client()

    # Check connectivity to all systems
    health = {"bhiv": "ok", "task7": "unknown", "sohum_mcp": "unknown", "ranjeet_rl": "unknown"}

    # Test Task 7
    try:
        response = await client.get("http://localhost:8000/api/v1/health", timeout=5.0)
        health["task7"] = "ok" if response.status_code == 200 else "error"
    except:
        health["task7"] = "unreachable"

    # Test Sohum MCP
    try:
        response = await client.get(
            f"{getattr(settings, 'SOHAM_URL', 'https://ai-rule-api-w7z5.onrender.com')}/health", timeout=5.0
        )
        health["sohum_mcp"] = "ok" if response.status_code == 200 else "error"
    except:
        health["sohum_mcp"] = "unreachable"

    # Test Ranjeet RL
    try:
        response = await client.get(f"{getattr(settings, 'YOTTA_URL', 'https://api.yotta.com')}/health", timeout=5.0)
        health["ranjeet_rl"] = "ok" if response.status_code == 200 else "error"
    except:
        health["ranjeet_rl"] = "unreachable"

    return health
