"""Multi-Model AI Adapter"""
import json
import logging
import os
import re

import httpx
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_with_multi_model_ai(prompt: str, params: dict) -> dict:
    """Try multiple AI models with automatic fallback"""

    openai_key = settings.OPENAI_API_KEY
    groq_key = settings.GROQ_API_KEY
    anthropic_key = settings.ANTHROPIC_API_KEY

    logger.info(f"[DEBUG] OpenAI: {'Found' if openai_key else 'Missing'}")
    logger.info(f"[DEBUG] Groq: {'Found' if groq_key else 'Missing'}")
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
  "design_type": "house|kitchen|office|bathroom|bedroom|living_room|commercial_office",
  "style": "modern|traditional|contemporary|rustic|etc",
  "stories": int,
  "dimensions": {"width": float, "length": float, "height": float},
  "estimated_cost": {"total": float, "currency": "INR"}
}

Analyze the user's prompt carefully and generate ALL objects mentioned."""

    city = params.get("city", "Mumbai")
    budget = params.get("context", {}).get("budget", "Not specified")
    style = params.get("style", "modern")

    user_prompt = f"Design request: {prompt}\n\nContext:\n- City: {city}\n- Budget: Rs.{budget}\n- Style: {style}\n\nGenerate complete design in JSON."

    errors = []

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
                        # Force correct city in metadata
                        if "metadata" not in spec_json:
                            spec_json["metadata"] = {}
                        spec_json["metadata"]["city"] = city
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
                        # Force correct city in metadata
                        if "metadata" not in spec_json:
                            spec_json["metadata"] = {}
                        spec_json["metadata"]["city"] = city
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
                            # Force correct city in metadata
                            if "metadata" not in spec_json:
                                spec_json["metadata"] = {}
                            spec_json["metadata"]["city"] = city
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
