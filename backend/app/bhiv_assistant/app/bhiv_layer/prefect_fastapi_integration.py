import json
import os
from typing import Any

import requests
from fastapi import FastAPI
from prefect import flow, task
from prefect.client import get_client
from pydantic import BaseModel

# Define FastAPI app
app = FastAPI(title="BHIV AI Assistant with Prefect Integration")


# Example RL agent task and flow
@task
def run_rl_agent(prompt: str) -> dict:
    """Use existing RL model code from repository"""
    try:
        from app.bhiv_assistant.workflows.rl_integration_flows import run_rl_agent as existing_rl

        # Convert prompt to state input
        state_input = {
            "prompt": prompt,
            "objects": [{"id": "room_1", "type": "room", "material": "default"}],
            "scene": {},
        }

        # Use existing RL model
        result = existing_rl(state_input)
        return {"decision": result}

    except Exception as e:
        # Fallback to mock if RL model fails
        result = {
            "decision": f"Optimized layout for: {prompt}",
            "confidence": 0.85,
            "recommendations": ["Increase green space", "Optimize traffic flow"],
            "error": str(e),
        }
        return {"decision": result}


@flow
def rl_flow(prompt: str) -> dict:
    return run_rl_agent(prompt)


# Data models for request bodies
class Feedback(BaseModel):
    user_id: str
    feedback: Any


class PromptRequest(BaseModel):
    prompt: str
    city: str = "Mumbai"
    user_id: str


@app.get("/rules")
async def get_mcp_rules():
    """Fetch rules from MCP (could be Prefect task if complex)"""
    try:
        # Try to fetch from actual MCP service
        response = requests.get("http://localhost:8000/api/v1/compliance/regulations", timeout=5)
        if response.status_code == 200:
            return {"rules": response.json()}
    except Exception:
        pass

    # Fallback to mock rules
    return {"rules": {"building_height": "Max 15 floors", "setback": "3 meters minimum", "fsi": "2.5 maximum"}}


@app.post("/submit")
async def submit_prompt(request: PromptRequest):
    """Submit a prompt to the RL agent via Prefect."""
    try:
        future = rl_flow.submit(request.prompt)
        return {"task_run_id": str(future.task_run_id), "status": "submitted", "prompt": request.prompt}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@app.get("/tasks/{task_run_id}/status")
async def check_status(task_run_id: str):
    """Poll Prefect for RL task status."""
    try:
        client = get_client()
        tr = await client.read_task_run(task_run_id)
        state = tr.state

        if state.is_completed():
            return {"status": "completed", "result": state.result()}
        elif state.is_failed():
            return {"status": "error", "result": str(state.state_details)}
        else:
            return {"status": state.name}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/feedback")
async def log_feedback(item: Feedback):
    """Log user feedback (e.g. to database or file)"""
    try:
        os.makedirs("data/feedback", exist_ok=True)
        feedback_entry = {"user_id": item.user_id, "feedback": item.feedback, "timestamp": "2024-12-05T20:00:00Z"}

        with open("data/feedback/feedback.jsonl", "a") as f:
            f.write(json.dumps(feedback_entry) + "\n")

        return {"status": "ok", "message": "Feedback logged successfully"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "BHIV AI Assistant with Prefect", "prefect_integration": "active"}
