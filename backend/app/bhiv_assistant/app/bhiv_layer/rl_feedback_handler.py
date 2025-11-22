"""
RL Feedback Handler
Integrates with Ranjeet's RL system for dynamic weight updates
"""

import logging
from typing import Dict, Optional
from datetime import datetime

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FeedbackPayload(BaseModel):
    """Feedback payload for RL agent"""
    user_id: str
    spec_id: str
    rating: float  # 0-5 scale
    feedback_text: Optional[str] = None
    design_accepted: bool
    timestamp: Optional[str] = None
    
    def model_dump(self, **kwargs):
        """Custom serialization to handle datetime"""
        data = super().model_dump(**kwargs)
        if self.timestamp is None:
            data['timestamp'] = datetime.now().isoformat()
        return data


class RLFeedbackHandler:
    """Handler for RL feedback integration"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
    
    async def submit_feedback(self, feedback: FeedbackPayload) -> Dict:
        """
        Submit user feedback to Ranjeet's RL system
        This triggers RL weight updates if threshold met
        """
        url = f"{self.base_url}/rl/feedback"
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = feedback.model_dump()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                logger.info(
                    f"Feedback submitted: spec_id={feedback.spec_id}, "
                    f"weights_updated={result.get('weights_updated', False)}"
                )
                
                return result
            
            except httpx.HTTPError as e:
                logger.error(f"Failed to submit RL feedback: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "weights_updated": False
                }
    
    async def get_confidence_score(self, spec_json: Dict, city: str) -> Optional[float]:
        """
        Get RL agent confidence score for a spec
        Used for bonus points display to end-users
        """
        url = f"{self.base_url}/rl/confidence"
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "spec_json": spec_json,
            "city": city
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=15.0)
                response.raise_for_status()
                
                result = response.json()
                return result.get("confidence", None)
            
            except httpx.HTTPError as e:
                logger.warning(f"Failed to get confidence score: {e}")
                return None


# API Router
from fastapi import APIRouter

rl_router = APIRouter(prefix="/rl", tags=["RL Integration"])


@rl_router.post("/feedback")
async def submit_user_feedback(feedback: FeedbackPayload):
    """Submit user feedback to RL agent"""
    from config.integration_config import IntegrationConfig
    
    config = IntegrationConfig()
    handler = RLFeedbackHandler(
        base_url=str(config.ranjeet.base_url),
        api_key=config.ranjeet.api_key
    )
    
    result = await handler.submit_feedback(feedback)
    return result


class ConfidenceRequest(BaseModel):
    """Request model for confidence score"""
    spec_json: Dict
    city: str


@rl_router.post("/confidence")
async def get_spec_confidence(request: ConfidenceRequest):
    """Get RL confidence score for spec"""
    from config.integration_config import IntegrationConfig
    
    config = IntegrationConfig()
    handler = RLFeedbackHandler(
        base_url=str(config.ranjeet.base_url),
        api_key=config.ranjeet.api_key
    )
    
    confidence = await handler.get_confidence_score(request.spec_json, request.city)
    return {
        "confidence": confidence,
        "city": request.city
    }