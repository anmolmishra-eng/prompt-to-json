from typing import Optional

from pydantic import BaseModel


class EvaluateRequest(BaseModel):
    user_id: str
    spec_id: str
    rating: float
    notes: Optional[str] = None
    feedback_text: Optional[str] = None


class EvaluateResponse(BaseModel):
    ok: bool
    saved_id: str
    feedback_processed: bool
    training_triggered: Optional[bool] = None
    message: str = "Evaluation saved successfully"
