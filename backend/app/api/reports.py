from app.database import get_current_user, get_db
from app.models import Evaluation, Iteration, Spec
from app.schemas import Report
from app.storage import (
    get_signed_url,
    storage_manager,
    upload_compliance,
    upload_geometry,
    upload_preview,
)
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/reports/{spec_id}", response_model=Report)
async def get_report(
    spec_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    spec = db.query(Spec).filter(Spec.spec_id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")

    iterations = db.query(Iteration).filter(Iteration.spec_id == spec_id).all()
    evaluations = db.query(Evaluation).filter(Evaluation.spec_id == spec_id).all()

    # List preview URLs (assuming each version stored as previews/{spec_id}_v{n}.glb)
    previews = []
    for version in range(1, spec.spec_version + 1):
        path = f"{spec_id}_v{version}.glb"
        try:
            signed = await get_signed_url("previews", path, expires=600)
            previews.append(signed)
        except Exception:
            # Skip if preview doesn't exist
            continue

    return Report(
        spec=spec.spec_json,
        iterations=[it.after_spec for it in iterations],
        evaluations=[{"score": ev.score, "notes": ev.notes} for ev in evaluations],
        preview_urls=previews,
    )


@router.post("/reports")
async def create_report(request: dict, current_user: str = Depends(get_current_user)):
    title = request.get("title", "")
    content = request.get("content", "")

    return {
        "message": "Report created",
        "title": title,
        "content": content,
        "user": current_user,
    }


@router.post("/upload")
async def upload_report_file(
    file: UploadFile = File(...), current_user: str = Depends(get_current_user)
):
    file_content = await file.read()
    file_path = await storage_manager.upload_file(file_content, file.filename)
    signed_url = await storage_manager.get_signed_url(file_path)

    return {
        "message": "File uploaded",
        "filename": file.filename,
        "file_path": file_path,
        "signed_url": signed_url,
        "user": current_user,
    }


@router.post("/upload-preview")
async def upload_preview_file(
    spec_id: str,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    """Upload preview GLB file"""
    preview_bytes = await file.read()
    signed_url = await upload_preview(spec_id, preview_bytes)

    return {
        "message": "Preview uploaded",
        "spec_id": spec_id,
        "signed_url": signed_url,
        "expires_in": 600,
        "user": current_user,
    }


@router.post("/upload-geometry")
async def upload_geometry_file(
    spec_id: str,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    """Upload geometry STL file"""
    geometry_bytes = await file.read()
    file_type = file.filename.split(".")[-1] if "." in file.filename else "stl"
    signed_url = await upload_geometry(spec_id, geometry_bytes, file_type)

    return {
        "message": "Geometry uploaded",
        "spec_id": spec_id,
        "signed_url": signed_url,
        "file_type": file_type,
        "user": current_user,
    }


@router.post("/upload-compliance")
async def upload_compliance_file(
    case_id: str,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    """Upload compliance ZIP file"""
    compliance_bytes = await file.read()
    signed_url = await upload_compliance(case_id, compliance_bytes)

    return {
        "message": "Compliance file uploaded",
        "case_id": case_id,
        "signed_url": signed_url,
        "user": current_user,
    }
