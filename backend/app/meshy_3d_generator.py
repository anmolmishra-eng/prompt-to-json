import asyncio
import logging
import os

import httpx
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_3d_with_meshy(prompt: str, dimensions: dict) -> bytes:
    """Generate realistic 3D construction model using Meshy AI"""
    MESHY_API_KEY = os.getenv("MESHY_API_KEY", getattr(settings, "MESHY_API_KEY", None))

    if not MESHY_API_KEY:
        logger.warning("Meshy API key not configured")
        return None

    width = dimensions.get("width", 10)
    length = dimensions.get("length", 10)
    height = dimensions.get("height", 3)

    detailed_prompt = f"""Realistic 3D architectural construction model: {prompt}
Exact dimensions: {width}m wide × {length}m long × {height}m tall
Include: concrete foundation, brick/concrete walls, flat roof slab, wooden doors, aluminum windows
Modern residential construction style with realistic textures
Detailed architectural visualization"""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            logger.info(f"Starting Meshy 3D generation...")
            response = await client.post(
                "https://api.meshy.ai/v2/text-to-3d",
                headers={"Authorization": f"Bearer {MESHY_API_KEY}"},
                json={
                    "mode": "preview",
                    "prompt": detailed_prompt,
                    "art_style": "realistic",
                    "negative_prompt": "cartoon, low quality, distorted",
                },
            )

            if response.status_code != 200:
                logger.error(f"Meshy error: {response.status_code}")
                return None

            task_id = response.json()["result"]
            logger.info(f"Meshy task: {task_id}, waiting for completion...")

            for attempt in range(60):
                await asyncio.sleep(2)
                status_resp = await client.get(
                    f"https://api.meshy.ai/v2/text-to-3d/{task_id}",
                    headers={"Authorization": f"Bearer {MESHY_API_KEY}"},
                )

                if status_resp.status_code == 200:
                    result = status_resp.json()
                    if result.get("status") == "SUCCEEDED":
                        glb_url = result.get("model_urls", {}).get("glb")
                        if glb_url:
                            glb_resp = await client.get(glb_url)
                            logger.info(f"✅ Meshy 3D generated: {len(glb_resp.content)} bytes")
                            return glb_resp.content
                    elif result.get("status") == "FAILED":
                        logger.error(f"Meshy failed: {result.get('error')}")
                        return None

            logger.warning("Meshy timeout")
            return None
    except Exception as e:
        logger.error(f"Meshy error: {e}")
        return None
