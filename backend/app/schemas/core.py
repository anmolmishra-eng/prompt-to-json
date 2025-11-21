from typing import Dict, Optional

from pydantic import BaseModel


class CoreRunRequest(BaseModel):
    user_id: str
    prompt: str
    project_id: Optional[str] = None
    context: Optional[Dict] = None


class MessageResponse(BaseModel):
    message: str


class Report(BaseModel):
    report_id: str
    data: Dict
