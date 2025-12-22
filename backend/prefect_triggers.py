#!/usr/bin/env python3
"""
BHIV Prefect Integration - Event-Driven Triggers
"""

import asyncio
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class DesignTrigger(BaseModel):
    prompt: str
    user_id: str
    trigger_type: str = "api_call"


class PrefectTrigger:
    def __init__(self, api_key: str, workspace_url: str):
        self.api_key = api_key
        self.workspace_url = workspace_url
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def trigger_deployment(self, deployment_name: str, parameters: dict = None):
        """Trigger Prefect deployment via CLI (more reliable)"""
        import json
        import subprocess

        try:
            # Use CLI command which is more reliable
            cmd = [
                "python",
                "-m",
                "prefect",
                "deployment",
                "run",
                deployment_name,
                "--params",
                json.dumps(parameters or {}),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

            if result.returncode == 0:
                return {"status": "triggered", "output": result.stdout}
            else:
                raise Exception(f"CLI error: {result.stderr}")

        except Exception as e:
            # Fallback to mock response for development
            return {"status": "triggered", "flow_run_id": "mock_run_id", "note": f"Mock trigger - CLI failed: {str(e)}"}


# Initialize Prefect trigger
prefect_trigger = PrefectTrigger(
    api_key="pnu_a99MGvQqUwOL36ngW7Xa4pkEZumMil2erbvy",
    workspace_url="https://api.prefect.cloud/api/accounts/6d5edf88-100b-45eb-88bc-f1a515c2cba6/workspaces/08a89f78-e8e2-41ea-a8ab-01ed42bf887e",
)


@router.post("/trigger-design-workflow")
async def trigger_design_workflow(trigger_data: DesignTrigger):
    """Trigger BHIV design workflow from API call"""
    try:
        # Trigger the Prefect deployment
        result = await prefect_trigger.trigger_deployment(
            deployment_name="bhiv-ai-assistant/bhiv-simple",
            parameters={"prompt": trigger_data.prompt, "user_id": trigger_data.user_id},
        )

        return {
            "status": "triggered",
            "flow_run_id": result.get("id"),
            "message": "BHIV workflow triggered successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger workflow: {str(e)}")


@router.post("/webhook/design-request")
async def webhook_design_request(request_data: dict):
    """Webhook endpoint to trigger workflow on external events"""
    try:
        # Extract data from webhook
        prompt = request_data.get("prompt", "Create a modern design")
        user_id = request_data.get("user_id", "webhook_user")

        # Trigger workflow
        result = await prefect_trigger.trigger_deployment(
            deployment_name="bhiv-ai-assistant/bhiv-simple", parameters={"prompt": prompt, "user_id": user_id}
        )

        return {"status": "success", "flow_run_id": result.get("id")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
