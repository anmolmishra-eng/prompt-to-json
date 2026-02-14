from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    user_id: str
    prompt: str
    city: Optional[str] = "Mumbai"
    style: Optional[str] = "modern"
    project_id: Optional[str] = None
    context: Optional[Dict] = None


class GenerateResponse(BaseModel):
    spec_id: str
    spec_json: Dict
    preview_url: str = ""
    estimated_cost: float
    compliance_check_id: str
    created_at: datetime
    spec_version: int = 1
    user_id: str
