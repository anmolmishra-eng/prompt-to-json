#!/usr/bin/env python3
"""
BHIV AI Assistant - Prefect Workflow
Main workflow for design generation and processing
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict

from prefect import flow, task
from prefect.blocks.webhook import Webhook


@task
def process_design_request(prompt: str, user_id: str = "default") -> Dict[str, Any]:
    """Process design generation request"""
    return {
        "design_id": f"design_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "prompt": prompt,
        "user_id": user_id,
        "status": "generated",
        "timestamp": datetime.now().isoformat(),
    }


@task
def evaluate_design(design_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate generated design"""
    design_data["evaluation"] = {
        "aesthetics_score": 8.5,
        "functionality_score": 9.0,
        "cost_effectiveness": 7.8,
        "overall_score": 8.4,
    }
    return design_data


@task
async def send_webhook_notification(design_data: Dict[str, Any]):
    """Send webhook notification using the bhiv-webhook block"""
    try:
        from prefect.blocks.webhook import Webhook

        webhook_block = await Webhook.load("bhiv-webhook")
        response = await webhook_block.call(payload=design_data)
        print(f"Webhook sent successfully: {response.status_code}")
    except Exception as e:
        print(f"Webhook failed: {e}")


@flow(name="bhiv-ai-assistant")
async def bhiv_workflow(prompt: str = "Create a modern kitchen design", user_id: str = "user123"):
    """Main BHIV AI Assistant workflow"""

    # Process design request
    design_data = process_design_request(prompt, user_id)

    # Evaluate design
    evaluated_design = evaluate_design(design_data)

    # Send notification
    await send_webhook_notification(evaluated_design)

    return evaluated_design


if __name__ == "__main__":
    # Run the workflow locally for testing
    result = asyncio.run(bhiv_workflow())
    print(f"Workflow completed: {result}")
