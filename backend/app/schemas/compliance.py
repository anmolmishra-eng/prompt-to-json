from typing import List, Optional

from pydantic import BaseModel


class ComplianceRequest(BaseModel):
    spec_id: str
    regulations: List[str] = []
    location: Optional[str] = None


class ComplianceResponse(BaseModel):
    compliance_url: str
    status: str
