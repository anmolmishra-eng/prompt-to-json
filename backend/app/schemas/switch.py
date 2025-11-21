from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class SwitchTarget(BaseModel):
    object_id: Optional[str] = None
    object_query: Optional[str] = None


class SwitchUpdate(BaseModel):
    material: Optional[str] = None
    color_hex: Optional[str] = None
    texture_override: Optional[str] = None


class SwitchRequest(BaseModel):
    user_id: str
    spec_id: str
    target: SwitchTarget
    update: SwitchUpdate
    note: Optional[str] = None
    expected_version: Optional[int] = None


class SwitchChanged(BaseModel):
    object_id: str
    field: str
    before: str
    after: str


class SwitchResponse(BaseModel):
    spec_id: str
    iteration_id: str
    updated_spec_json: Dict
    preview_url: str = ""
    changed: SwitchChanged
    saved_at: datetime
    spec_version: int
