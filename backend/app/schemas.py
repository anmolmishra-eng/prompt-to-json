from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr


# Generate endpoint schemas
class GenerateRequest(BaseModel):
    user_id: str
    prompt: str
    context: Optional[Dict[str, Any]] = None
    project_id: Optional[str] = None


class GenerateResponse(BaseModel):
    spec_id: str
    spec_json: Dict[str, Any]
    preview_url: str
    created_at: datetime


# Switch endpoint schemas (material switching)
class SwitchTarget(BaseModel):
    object_id: Optional[str] = None
    object_query: Optional[Dict[str, Any]] = None


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


class SwitchChanged(BaseModel):
    object_id: str
    field: str
    before: str
    after: str


class SwitchResponse(BaseModel):
    spec_id: str
    iteration_id: str
    updated_spec_json: Dict[str, Any]
    preview_url: str
    changed: SwitchChanged
    saved_at: datetime


# Provider switch schemas
class ProviderSwitchRequest(BaseModel):
    provider: str


# Evaluate endpoint schemas
class EvaluateRequest(BaseModel):
    spec_id: str
    user_id: str
    rating: int
    notes: Optional[str] = None


class EvaluateResponse(BaseModel):
    ok: bool
    saved_id: str


# Iterate endpoint schemas
class IterateRequest(BaseModel):
    spec_id: str
    strategy: str  # e.g., "improve_materials"
    user_id: str


class IterateResponse(BaseModel):
    before: Dict[str, Any]
    after: Dict[str, Any]
    feedback: str


# Compliance endpoint schemas
class ComplianceRequest(BaseModel):
    spec_id: str
    user_id: str


class ComplianceResponse(BaseModel):
    compliance_url: str
    status: str


# Core run endpoint schemas
class CoreRunRequest(BaseModel):
    pipeline: List[str]  # e.g., ["generate", "evaluate", "iterate"]
    input: Dict[str, Any]  # input data for pipeline steps


class CoreRunResponse(BaseModel):
    outputs: Dict[str, Any]  # aggregated outputs from all steps


# Report schema
class Report(BaseModel):
    spec: Dict[str, Any]
    iterations: List[Dict[str, Any]]
    evaluations: List[Dict[str, Any]]
    preview_urls: List[str]


# Generic response
class MessageResponse(BaseModel):
    message: str
