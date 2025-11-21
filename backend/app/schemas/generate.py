from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    user_id: str
    prompt: str
    project_id: Optional[str] = None
    context: Optional[Dict] = None


class GenerateResponse(BaseModel):
    spec_id: str
    spec_json: Dict
    preview_url: str = ""
    created_at: datetime
    spec_version: int = 1
    user_id: str
