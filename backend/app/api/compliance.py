from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import ComplianceRequest, ComplianceResponse
from app.database import get_current_user, get_db
from app.models import Spec
from app.storage import upload_to_bucket, get_signed_url
from app.config import settings
import httpx
import json
import base64

router = APIRouter()

SOHAM_URL = settings.SOHAM_URL
API_KEY = settings.COMPLIANCE_API_KEY

@router.post("/run_case")
async def run_case(
    case: dict,
    current_user: str = Depends(get_current_user)
):
    # Forward the request to Soham's /run_case
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{SOHAM_URL}/run_case",
            json=case,
            headers=headers
        )
    
    # On success, parse returned case_id and maybe geometry
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Compliance run failed")
    
    data = res.json()
    case_id = data.get("case_id")
    
    # Assume response includes output geometry (STL) or a URL; store to Supabase
    geometry_bytes = data.get("geometry_zip_bytes")
    if geometry_bytes and case_id:
        # Decode base64 if needed
        if isinstance(geometry_bytes, str):
            geometry_bytes = base64.b64decode(geometry_bytes)
        await upload_to_bucket("compliance", f"{case_id}.zip", geometry_bytes)
    
    # Return Soham's response through the API
    return data

@router.post("/feedback")
async def feedback(
    feedback_req: dict,
    current_user: str = Depends(get_current_user)
):
    # Simply proxy to Soham's /feedback
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{SOHAM_URL}/feedback",
            json=feedback_req,
            headers=headers
        )
    
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Compliance feedback failed")
    
    return res.json()

@router.get("/regulations")
async def get_regulations(current_user: str = Depends(get_current_user)):
    """Get available compliance regulations"""
    return {
        "regulations": [
            {"id": "ISO_9001", "name": "ISO 9001 Quality Management"},
            {"id": "OSHA", "name": "OSHA Safety Standards"},
            {"id": "CE_MARKING", "name": "CE Marking Requirements"},
            {"id": "FDA_510K", "name": "FDA 510(k) Medical Device"}
        ]
    }

@router.post("/check", response_model=ComplianceResponse)
async def compliance_check(
    request: ComplianceRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get spec for compliance check
    spec = db.query(Spec).filter(Spec.spec_id == request.spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")
    
    # Generate compliance report (placeholder)
    compliance_report = {
        "spec_id": request.spec_id,
        "compliance_status": "PASSED",
        "checks": [
            {"rule": "Safety Standards", "status": "PASSED"},
            {"rule": "Material Requirements", "status": "PASSED"},
            {"rule": "Dimensional Constraints", "status": "PASSED"}
        ],
        "generated_at": "2024-01-01T00:00:00Z"
    }
    
    # Create compliance ZIP file
    compliance_data = json.dumps(compliance_report, indent=2).encode('utf-8')
    case_id = f"case_{request.spec_id}"
    
    # Upload compliance report
    await upload_to_bucket("compliance", f"{case_id}.zip", compliance_data)
    compliance_url = await get_signed_url("compliance", f"{case_id}.zip", expires=600)
    
    return ComplianceResponse(
        compliance_url=compliance_url,
        status="PASSED"
    )