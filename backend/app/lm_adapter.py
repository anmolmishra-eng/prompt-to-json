import httpx
import logging
import re
from typing import Dict, Any
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)

def run_local_lm(prompt: str, params: dict) -> dict:
    """Run inference on local RTX-3060 GPU"""
    logger.info(f"Running local LM for prompt length: {len(prompt)}")
    
    # Placeholder for HuggingFace pipeline or custom model
    # In production: load model, run inference on GPU
    spec_json = {
        "components": ["LocalComponent"],
        "features": ["local_feature"],
        "tech_stack": ["Local GPU"],
        "model_used": "local-rtx-3060"
    }
    
    # Log usage for billing
    log_usage("local", len(prompt), 0.001, params.get("user_id"))  # $0.001 per token
    
    return {
        "spec_json": spec_json,
        "preview_data": f"Local GPU generated response for: {prompt[:50]}...",
        "provider": "local",
        "feedback": f"Local GPU improved design using strategy: {params.get('strategy', 'general')}"
    }

async def run_yotta_lm(prompt: str, params: dict) -> dict:
    """Run inference on Yotta cloud API"""
    logger.info(f"Running Yotta LM for prompt length: {len(prompt)}")
    
    # Always use mock response for testing (no paid API calls)
    logger.info("Using mock Yotta response (testing mode)")
    
    # Log mock usage for billing
    log_usage("yotta", len(prompt), 0.01, params.get("user_id"))  # $0.01 per token
    
    return {
        "spec_json": {
            "objects": [
                {"id": "yotta_obj_1", "type": "component", "material": "steel"},
                {"id": "yotta_obj_2", "type": "feature", "material": "aluminum"}
            ],
            "components": ["MockYottaComponent"],
            "features": ["mock_feature"],
            "tech_stack": ["Mock Yotta Cloud"],
            "model_used": "mock-yotta-model"
        },
        "preview_data": f"Mock Yotta response for: {prompt[:50]}...",
        "provider": "yotta",
        "feedback": f"Mock Yotta improved design using strategy: {params.get('strategy', 'general')}"
    }

def extract_dimensions_from_prompt(prompt: str) -> dict:
    """Extract dimensions from natural language prompt"""
    dimensions = {}
    
    # Patterns to match dimensions
    patterns = [
        r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*(?:x\s*(\d+(?:\.\d+)?))?\s*(?:meter|metres|m|feet|ft|cm|centimeter|centimeters)',
        r'(\d+(?:\.\d+)?)\s*by\s*(\d+(?:\.\d+)?)\s*(?:by\s*(\d+(?:\.\d+)?))?\s*(?:meter|metres|m|feet|ft|cm|centimeter|centimeters)',
        r'length\s*(\d+(?:\.\d+)?)\s*(?:meter|metres|m|feet|ft|cm|centimeter|centimeters)',
        r'width\s*(\d+(?:\.\d+)?)\s*(?:meter|metres|m|feet|ft|cm|centimeter|centimeters)',
        r'height\s*(\d+(?:\.\d+)?)\s*(?:meter|metres|m|feet|ft|cm|centimeter|centimeters)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, prompt.lower())
        if matches:
            if len(matches[0]) == 3 and matches[0][2]:  # 3D dimensions
                dimensions = {
                    "length": float(matches[0][0]),
                    "width": float(matches[0][1]),
                    "height": float(matches[0][2])
                }
                break
            elif len(matches[0]) >= 2:  # 2D dimensions
                dimensions = {
                    "length": float(matches[0][0]),
                    "width": float(matches[0][1]),
                    "height": 3.0  # default height
                }
                break
    
    return dimensions

async def lm_run(prompt: str, params: dict = None) -> dict:
    """Route to local GPU or Yotta based on prompt complexity"""
    if params is None:
        params = {}
    
    # Extract dimensions from prompt
    extracted_dims = extract_dimensions_from_prompt(prompt)
    if extracted_dims:
        params["extracted_dimensions"] = extracted_dims
        logger.info(f"Extracted dimensions from prompt: {extracted_dims}")
    
    # Simple heuristic: use local if prompt short, else use Yotta
    if len(prompt) < 100:  # Local GPU for simple tasks
        return run_local_lm(prompt, params)
    else:  # Yotta for heavy jobs
        return await run_yotta_lm(prompt, params)

def log_usage(provider: str, tokens: int, cost_per_token: float, user_id: str = None):
    """Log LM usage for billing with detailed tracking"""
    total_cost = cost_per_token * tokens
    usage_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "provider": provider,
        "tokens": tokens,
        "cost_per_token": cost_per_token,
        "total_cost": total_cost,
        "user_id": user_id,
        "gpu_hours": tokens / 1000 if provider == "local" else 0,  # Estimate GPU usage
        "api_calls": 1 if provider == "yotta" else 0
    }
    
    # Log for monitoring and billing
    logger.info(f"BILLING: {usage_log}")
    
    # Store in usage log file
    with open("lm_usage.log", "a") as f:
        f.write(f"{usage_log}\n")
    
    # Log to audit system
    from app.utils import log_audit_event
    if user_id:
        log_audit_event(
            "lm_usage",
            user_id,
            {"provider": provider, "tokens": tokens, "cost": total_cost}
        )

class LMAdapter:
    async def generate(self, prompt: str, model: str = "default") -> str:
        result = await lm_run(prompt, {"model": model})
        return result["preview_data"]

lm_adapter = LMAdapter()