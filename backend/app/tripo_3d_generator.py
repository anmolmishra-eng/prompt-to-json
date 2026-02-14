"""
Tripo AI 3D Model Generator
Generates realistic 3D construction models from text prompts
"""
import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)


async def generate_3d_with_tripo(prompt: str, dimensions: dict, api_key: str) -> Optional[bytes]:
    """Generate 3D model using Tripo AI (10 free credits/month)"""
    try:
        # Build detailed architectural prompt
        width = dimensions.get("width", 10)
        length = dimensions.get("length", 10)
        height = dimensions.get("height", 3)

        detailed_prompt = (
            f"Architectural building construction: {prompt}. "
            f"Realistic 3D model with dimensions {width}m width x {length}m length x {height}m height. "
            f"Include walls, roof, foundation, doors, windows. Professional architectural visualization."
        )

        logger.info(f"Tripo AI: Creating task with prompt: {detailed_prompt[:100]}...")

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        # Create 3D generation task
        response = requests.post(
            "https://api.tripo3d.ai/v2/openapi/task",
            headers=headers,
            json={"type": "text_to_model", "prompt": detailed_prompt},
            timeout=10,
        )

        if response.status_code == 403:
            error_data = response.json()
            if error_data.get("code") == 2010:
                logger.warning("\n" + "=" * 80)
                logger.warning("⚠️  TRIPO AI: NO CREDITS REMAINING")
                logger.warning("You've used all 10 free credits for this month.")
                logger.warning("Options:")
                logger.warning("  1. Wait for monthly reset")
                logger.warning("  2. Purchase credits at https://platform.tripo3d.ai/")
                logger.warning("  3. System will use fallback GLB generator (free, instant)")
                logger.warning("=" * 80 + "\n")
            return None

        if response.status_code != 200:
            logger.warning(f"Tripo task creation failed: {response.status_code} - {response.text}")
            return None

        task_id = response.json()["data"]["task_id"]
        logger.info(f"Tripo task created: {task_id}")

        # Poll for completion (max 2 minutes)
        for attempt in range(24):
            time.sleep(5)

            result = requests.get(f"https://api.tripo3d.ai/v2/openapi/task/{task_id}", headers=headers, timeout=10)

            if result.status_code != 200:
                logger.warning(f"Tripo status check failed: {result.status_code}")
                return None

            data = result.json()["data"]
            status = data["status"]

            logger.info(f"Tripo status (attempt {attempt+1}/24): {status}")

            if status == "success":
                glb_url = data["output"]["model"]
                logger.info(f"Tripo success! Downloading from: {glb_url}")

                # Download GLB file
                glb_response = requests.get(glb_url, timeout=30)
                glb_data = glb_response.content

                logger.info(f"✅ Tripo generated {len(glb_data)} bytes of realistic 3D model")
                return glb_data

            elif status == "failed":
                logger.warning(f"Tripo generation failed: {data.get('error', 'Unknown error')}")
                return None

        logger.warning("Tripo timeout after 2 minutes")
        return None

    except Exception as e:
        logger.error(f"Tripo AI error: {e}", exc_info=True)
        return None
