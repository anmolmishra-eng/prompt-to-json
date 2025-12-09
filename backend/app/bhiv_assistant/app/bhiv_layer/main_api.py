import json
import os

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="BHIV AI Assistant API")


class Prompt(BaseModel):
    """Schema for RL prompt data."""

    city: str
    parameters: dict


class Feedback(BaseModel):
    """Schema for user feedback."""

    user: str
    message: str
    rating: int


@app.get("/mcp_rules")
def get_mcp_rules():
    """
    Return current MCP rules as JSON.
    In practice, load rules from database or central bucket.
    """
    # Placeholder: read rules from a file or database
    rules = {"rule1": "No buildings above X floors", "rule2": "Zone A restrictions"}
    return {"rules": rules}


@app.post("/submit_prompt")
def submit_prompt(prompt: Prompt):
    """
    Submit a prompt (e.g. for land-use optimization) to the RL agent.
    Returns the agent's decision or action plan.
    """
    # Placeholder: integrate with existing RL model code
    try:
        # Simulate RL agent prediction
        result = {
            "city": prompt.city,
            "optimization": "land_use_optimized",
            "parameters": prompt.parameters,
            "confidence": 0.85,
            "recommendations": ["Increase green space", "Optimize traffic flow"],
        }
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


@app.post("/feedback")
def log_feedback(feedback: Feedback):
    """
    Log user feedback for continuous RL improvement.
    """
    # For example, write to database or append to a feedback file.
    log_entry = feedback.dict()
    os.makedirs("data", exist_ok=True)
    with open("data/feedback_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    return {"status": "success", "received": feedback}
