"""
Hugging Face 3D Model Generator
Completely FREE with unlimited usage
"""
import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)


async def generate_3d_with_huggingface(prompt: str, dimensions: dict, api_key: Optional[str] = None) -> Optional[bytes]:
    """Generate 3D model using Hugging Face Inference API (FREE, unlimited)"""
    try:
        width = dimensions.get("width", 10)
        length = dimensions.get("length", 10)
        height = dimensions.get("height", 3)

        detailed_prompt = (
            f"3D architectural building model: {prompt}. "
            f"Realistic construction with dimensions {width}m x {length}m x {height}m. "
            f"Include walls, roof, foundation, doors, windows. Modern architectural design."
        )

        logger.info(f"Hugging Face: Generating 3D model (FREE)...")

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Try multiple FREE 3D models
        models = [
            "stabilityai/stable-zero123",  # Stability AI 3D model
            "ashawkey/stable-dreamfusion",  # DreamFusion 3D
        ]

        for model in models:
            try:
                response = requests.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json={"inputs": detailed_prompt},
                    timeout=60,
                )

                # Model might be loading, retry once
                if response.status_code == 503:
                    logger.info(f"Model {model} loading, retrying in 20s...")
                    time.sleep(20)
                    response = requests.post(
                        f"https://api-inference.huggingface.co/models/{model}",
                        headers=headers,
                        json={"inputs": detailed_prompt},
                        timeout=60,
                    )

                if response.status_code == 200:
                    glb_data = response.content
                    logger.info(f"✅ Hugging Face ({model}) generated {len(glb_data)} bytes (FREE)")
                    return glb_data
                else:
                    logger.warning(f"Model {model} failed: {response.status_code}")
                    continue

            except Exception as model_error:
                logger.warning(f"Model {model} error: {model_error}")
                continue

        # All models failed
        logger.warning("All Hugging Face models unavailable")
        return None

    except Exception as e:
        logger.error(f"Hugging Face error: {e}")
        return None
