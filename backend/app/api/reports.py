import logging

from app.database import get_current_user, get_db
from app.models import Evaluation, Iteration, Spec
from app.schemas import Report
from app.storage import get_signed_url, upload_geometry, upload_preview, upload_to_bucket
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/reports/{spec_id}")
async def get_report(
    spec_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Step 1: Check if spec exists
        spec = db.query(Spec).filter(Spec.spec_id == spec_id).first()
        if not spec:
            raise HTTPException(status_code=404, detail="Spec not found")

        # Step 2: Get iterations and evaluations
        iterations = db.query(Iteration).filter(Iteration.spec_id == spec_id).all()
        evaluations = db.query(Evaluation).filter(Evaluation.spec_id == spec_id).all()

        # Step 3: Build response without preview URLs first
        response_data = {
            "report_id": spec_id,
            "data": {"spec_id": spec_id, "version": spec.spec_version or 1},
            "spec": spec.spec_json or {},
            "iterations": [it.after_spec or {} for it in iterations] if iterations else [],
            "evaluations": [{"score": ev.score or 0, "notes": ev.notes or ""} for ev in evaluations]
            if evaluations
            else [],
            "preview_urls": [],
        }

        # Step 4: Try to add preview URLs (this might be causing the issue)
        try:
            if spec.spec_version:
                for version in range(1, spec.spec_version + 1):
                    path = f"{spec_id}_v{version}.glb"
                    try:
                        signed = await get_signed_url("previews", path, expires=600)
                        response_data["preview_urls"].append(signed)
                    except Exception:
                        # Skip if preview doesn't exist
                        continue
        except Exception as preview_error:
            # Don't fail the whole request if preview generation fails
            logger.warning(f"Preview URL generation failed: {preview_error}")
            response_data["preview_urls"] = []

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_report for {spec_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
async def upload_report_file(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    file_content = await file.read()
    file_path = f"reports/{file.filename}"
    await upload_to_bucket("files", file_path, file_content)
    signed_url = await get_signed_url("files", file_path, expires=600)

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
    """Upload preview file (GLB, JPG, PNG, etc.)"""
    try:
        preview_bytes = await file.read()

        # Get file extension from uploaded file
        file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else "glb"

        # Upload with correct extension and timestamp to avoid duplicates
        import time

        timestamp = int(time.time())
        path = f"{spec_id}_{timestamp}.{file_extension}"
        await upload_to_bucket("previews", path, preview_bytes)
        signed_url = await get_signed_url("previews", path, expires=600)

        return {
            "message": "Preview uploaded",
            "spec_id": spec_id,
            "filename": file.filename,
            "file_type": file_extension,
            "signed_url": signed_url,
            "expires_in": 600,
            "user": current_user,
        }
    except Exception as e:
        logger.error(f"Preview upload failed for {spec_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Preview upload failed: {str(e)}")


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
    file_path = f"compliance/{case_id}.zip"
    await upload_to_bucket("compliance", file_path, compliance_bytes)
    signed_url = await get_signed_url("compliance", file_path, expires=600)

    return {
        "message": "Compliance file uploaded",
        "case_id": case_id,
        "signed_url": signed_url,
        "user": current_user,
    }
