from typing import Dict, Optional

from pydantic import BaseModel


class IterateRequest(BaseModel):
    user_id: str
    spec_id: str
    strategy: str


class IterateResponse(BaseModel):
    before: Dict
    after: Dict
    feedback: str
    iteration_id: str
    preview_url: Optional[str] = ""
    spec_version: Optional[int] = None
    training_triggered: Optional[bool] = False
    strategy: Optional[str] = None
