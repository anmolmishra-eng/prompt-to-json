"""Multi-Model AI Adapter"""
import json
import logging
import re

import httpx
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_with_multi_model_ai(prompt: str, params: dict) -> dict:
    """Try multiple AI models with automatic fallback - Groq prioritized"""

    groq_key = settings.GROQ_API_KEY
    openai_key = settings.OPENAI_API_KEY
    anthropic_key = settings.ANTHROPIC_API_KEY

    logger.info(f"[DEBUG] Groq: {'Found' if groq_key else 'Missing'}")
    logger.info(f"[DEBUG] OpenAI: {'Found' if openai_key else 'Missing'}")
    logger.info(f"[DEBUG] Anthropic: {'Found' if anthropic_key else 'Missing'}")

    system_prompt = """You are an expert architectural and interior design AI. Generate detailed design specifications in JSON format.

Your response MUST be valid JSON with this exact structure:
{
  "objects": [
    {
      "id": "unique_id",
      "type": "foundation|wall|roof|door|window|furniture|fixture|room|etc",
      "subtype": "optional_subtype",
      "material": "material_name",
      "color_hex": "#HEXCODE",
      "dimensions": {"width": float, "length": float, "height": float},
      "count": int (optional)
    }
  ],
  "design_type": "house|apartment|villa|kitchen|office|bathroom|bedroom|living_room",
  "style": "modern|traditional|contemporary|rustic|etc",
  "stories": int,
  "dimensions": {"width": float, "length": float, "height": float},
  "estimated_cost": {"total": float, "currency": "INR"}
}

IMPORTANT RULES:
1. ALL dimensions MUST be in METERS (not feet)
2. Use REALISTIC dimensions for Indian residential buildings:
   - 1BHK: 8m × 6m (48 sqm / 500 sqft)
   - 2BHK: 10m × 8m (80 sqm / 860 sqft)
   - 3BHK: 12m × 10m (120 sqm / 1290 sqft)
   - 4BHK Villa: 15m × 12m (180 sqm / 1940 sqft)
   - 5BHK Villa: 18m × 14m (252 sqm / 2700 sqft)
   - Story height: 3.0m to 3.5m per floor
3. If dimensions are provided in context, use EXACTLY those dimensions
4. Keep estimated_cost within the specified budget
5. Generate ALL objects mentioned in the prompt (garden, countertops, etc.)"""

    city = params.get("city", "Mumbai")
    budget = params.get("budget") or params.get("context", {}).get("budget", "Not specified")
    style = params.get("style", "modern")
    extracted_dims = params.get("extracted_dimensions", {})

    budget_str = f"Rs.{budget:,}" if isinstance(budget, (int, float)) else str(budget)

    # Add dimension constraints to prompt
    dim_str = ""
    if extracted_dims:
        dim_parts = []
        if "width" in extracted_dims:
            dim_parts.append(f"Width: {extracted_dims['width']:.2f}m")
        if "length" in extracted_dims:
            dim_parts.append(f"Length: {extracted_dims['length']:.2f}m")
        if "height" in extracted_dims:
            dim_parts.append(f"Height: {extracted_dims['height']:.2f}m")
        if "area_sqm" in extracted_dims:
            dim_parts.append(f"Area: {extracted_dims['area_sqm']:.2f} sqm")
        if dim_parts:
            dim_str = f"\n- Dimensions (in METERS): {', '.join(dim_parts)}"

    user_prompt = f"""Design request: {prompt}

Context:
- City: {city}
- Budget: {budget_str} (DO NOT EXCEED){dim_str}
- Style: {style}

Generate complete design in JSON. Use EXACT dimensions provided above (already in meters). Keep cost within budget."""

    errors = []

    # Try Groq FIRST (fastest and free)
    if groq_key:
        for model in ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]:
            try:
                logger.info(f"[AI] Trying Groq {model}...")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                        json={
                            "model": model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                            ],
                            "temperature": 0.7,
                            "response_format": {"type": "json_object"},
                        },
                    )

                    if response.status_code == 200:
                        result = response.json()
                        content = result["choices"][0]["message"]["content"]
                        spec_json = json.loads(content)
                        spec_json.setdefault("tech_stack", [f"Groq {model}"])
                        spec_json.setdefault("model_used", model)
                        if "metadata" not in spec_json:
                            spec_json["metadata"] = {}
                        spec_json["metadata"]["city"] = city

                        # Force correct dimensions from extracted values
                        if extracted_dims:
                            if "width" in extracted_dims and "length" in extracted_dims:
                                spec_json["dimensions"]["width"] = round(extracted_dims["width"], 2)
                                spec_json["dimensions"]["length"] = round(extracted_dims["length"], 2)
                            if "height" in extracted_dims:
                                spec_json["dimensions"]["height"] = round(extracted_dims["height"], 2)

                        # Force budget constraint
                        if isinstance(budget, (int, float)) and budget > 0:
                            if spec_json.get("estimated_cost", {}).get("total", 0) > budget * 1.1:
                                spec_json["estimated_cost"]["total"] = budget

                        logger.info(f"[SUCCESS] Groq {model} worked! City set to: {city}")
                        return spec_json
                    else:
                        error_msg = f"Groq {model} HTTP {response.status_code}"
                        logger.warning(f"[WARNING] {error_msg}")
                        errors.append(error_msg)
            except Exception as e:
                error_msg = f"Groq {model} error: {str(e)[:150]}"
                logger.warning(f"[WARNING] {error_msg}")
                errors.append(error_msg)

    # Try OpenAI as fallback
    if openai_key:
        for model in ["gpt-4o-mini", "gpt-3.5-turbo"]:
            try:
                logger.info(f"[AI] Trying OpenAI {model}...")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
                        json={
                            "model": model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                            ],
                            "temperature": 0.7,
                            "response_format": {"type": "json_object"},
                        },
                    )

                    if response.status_code == 200:
                        result = response.json()
                        content = result["choices"][0]["message"]["content"]
                        spec_json = json.loads(content)
                        spec_json.setdefault("tech_stack", [f"OpenAI {model}"])
                        spec_json.setdefault("model_used", model)
                        if "metadata" not in spec_json:
                            spec_json["metadata"] = {}
                        spec_json["metadata"]["city"] = city

                        # Force correct dimensions
                        if extracted_dims:
                            if "width" in extracted_dims and "length" in extracted_dims:
                                spec_json["dimensions"]["width"] = round(extracted_dims["width"], 2)
                                spec_json["dimensions"]["length"] = round(extracted_dims["length"], 2)
                            if "height" in extracted_dims:
                                spec_json["dimensions"]["height"] = round(extracted_dims["height"], 2)

                        # Force budget constraint
                        if isinstance(budget, (int, float)) and budget > 0:
                            if spec_json.get("estimated_cost", {}).get("total", 0) > budget * 1.1:
                                spec_json["estimated_cost"]["total"] = budget

                        logger.info(f"[SUCCESS] {model} worked! City set to: {city}")
                        return spec_json
                    else:
                        error_msg = f"{model} HTTP {response.status_code}"
                        logger.warning(f"[WARNING] {error_msg}")
                        errors.append(error_msg)
            except Exception as e:
                error_msg = f"{model} error: {str(e)[:150]}"
                logger.warning(f"[WARNING] {error_msg}")
                errors.append(error_msg)

    # Try Anthropic as last resort
    if anthropic_key:
        for model in ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]:
            try:
                logger.info(f"[AI] Trying Anthropic {model}...")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": anthropic_key,
                            "anthropic-version": "2023-06-01",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": model,
                            "max_tokens": 4096,
                            "messages": [{"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}],
                        },
                    )

                    if response.status_code == 200:
                        result = response.json()
                        content = result["content"][0]["text"]
                        json_match = re.search(r"\{[\s\S]*\}", content)
                        if json_match:
                            spec_json = json.loads(json_match.group())
                            spec_json.setdefault("tech_stack", [f"Anthropic {model}"])
                            spec_json.setdefault("model_used", model)
                            if "metadata" not in spec_json:
                                spec_json["metadata"] = {}
                            spec_json["metadata"]["city"] = city

                            # Force correct dimensions
                            if extracted_dims:
                                if "width" in extracted_dims and "length" in extracted_dims:
                                    spec_json["dimensions"]["width"] = round(extracted_dims["width"], 2)
                                    spec_json["dimensions"]["length"] = round(extracted_dims["length"], 2)
                                if "height" in extracted_dims:
                                    spec_json["dimensions"]["height"] = round(extracted_dims["height"], 2)

                            # Force budget constraint
                            if isinstance(budget, (int, float)) and budget > 0:
                                if spec_json.get("estimated_cost", {}).get("total", 0) > budget * 1.1:
                                    spec_json["estimated_cost"]["total"] = budget

                            logger.info(f"[SUCCESS] {model} worked! City set to: {city}")
                            return spec_json
                    else:
                        error_msg = f"{model} HTTP {response.status_code}"
                        logger.warning(f"[WARNING] {error_msg}")
                        errors.append(error_msg)
            except Exception as e:
                error_msg = f"{model} error: {str(e)[:150]}"
                logger.warning(f"[WARNING] {error_msg}")
                errors.append(error_msg)

    logger.error(f"[ERROR] All AI models failed. Errors: {errors[:3]}")
    raise Exception(f"All AI providers exhausted: {errors[0] if errors else 'No API keys'}")
