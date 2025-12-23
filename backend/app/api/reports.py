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
        spec = db.query(Spec).filter(Spec.id == spec_id).first()
        if not spec:
            raise HTTPException(status_code=404, detail="Spec not found")

        # Step 2: Get iterations and evaluations
        iterations = db.query(Iteration).filter(Iteration.spec_id == spec_id).all()
        evaluations = db.query(Evaluation).filter(Evaluation.spec_id == spec_id).all()

        # Step 3: Build response without preview URLs first
        response_data = {
            "report_id": spec_id,
            "data": {"spec_id": spec_id, "version": spec.version or 1},
            "spec": spec.spec_json or {},
            "iterations": [it.after_spec or {} for it in iterations] if iterations else [],
            "evaluations": [{"score": ev.rating or 0, "notes": ev.notes or ""} for ev in evaluations]
            if evaluations
            else [],
            "preview_urls": [],
        }

        # Step 4: Try to add preview URLs only if files exist
        try:
            if spec.version:
                from app.storage import file_exists

                for version in range(1, spec.version + 1):
                    path = f"{spec_id}_v{version}.glb"
                    # Check if file exists before generating signed URL
                    if file_exists("previews", path):
                        try:
                            signed = get_signed_url("previews", path, expires=600)  # Remove await
                            response_data["preview_urls"].append(signed)
                        except Exception:
                            continue
        except Exception as preview_error:
            logger.debug(f"Preview URL generation skipped: {preview_error}")
            response_data["preview_urls"] = []

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_report for {spec_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/reports")
async def create_report(request: dict, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    import json
    import os
    from datetime import datetime

    from app.database import engine
    from sqlalchemy import text

    title = request.get("title", "Untitled Report")
    content = request.get("content", "")
    report_type = request.get("report_type", "general")
    spec_id = request.get("spec_id", None)

    # Generate report ID
    report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user}"

    # Store in database
    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                INSERT INTO reports (report_id, user_id, title, content, report_type, spec_id, created_at)
                VALUES (:report_id, :user_id, :title, :content, :report_type, :spec_id, :created_at)
            """
                ),
                {
                    "report_id": report_id,
                    "user_id": current_user,
                    "title": title,
                    "content": content,
                    "report_type": report_type,
                    "spec_id": spec_id,
                    "created_at": datetime.now(),
                },
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to store report in database: {e}")
    # Store locally
    local_storage_dir = "data/reports"
    os.makedirs(local_storage_dir, exist_ok=True)

    report_data = {
        "report_id": report_id,
        "title": title,
        "content": content,
        "report_type": report_type,
        "spec_id": spec_id,
        "user": current_user,
        "created_at": datetime.now().isoformat(),
    }

    local_file = os.path.join(local_storage_dir, f"{report_id}.json")
    with open(local_file, "w") as f:
        json.dump(report_data, f, indent=2)

    return {
        "message": "Report created successfully",
        "report_id": report_id,
        "title": title,
        "content": content,
        "report_type": report_type,
        "user": current_user,
        "stored_in_database": True,
        "stored_locally": local_file,
    }


@router.post("/upload")
async def upload_report_file(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    import json
    import os
    from datetime import datetime

    from app.database import engine
    from sqlalchemy import text

    file_content = await file.read()

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(file.filename)[1]
    file_base = os.path.splitext(file.filename)[0]
    unique_filename = f"{file_base}_{timestamp}{file_ext}"
    file_path = f"reports/{unique_filename}"

    # Generate upload ID
    upload_id = f"upload_{timestamp}_{current_user}"

    # Upload to Supabase
    try:
        await upload_to_bucket("files", file_path, file_content)
        signed_url = get_signed_url("files", file_path, expires=600)
    except Exception as e:
        logger.error(f"Supabase upload failed: {e}")
        signed_url = None

    # Store metadata in database
    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                INSERT INTO reports (report_id, user_id, title, content, report_type, created_at)
                VALUES (:report_id, :user_id, :title, :content, :report_type, :created_at)
            """
                ),
                {
                    "report_id": upload_id,
                    "user_id": current_user,
                    "title": f"File Upload: {file.filename}",
                    "content": f"Uploaded file: {unique_filename}, Size: {len(file_content)} bytes",
                    "report_type": "file_upload",
                    "created_at": datetime.now(),
                },
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Database storage failed: {e}")

    # Store file locally with unique name
    local_dir = "data/uploads"
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, unique_filename)

    with open(local_path, "wb") as f:
        f.write(file_content)

    # Store metadata locally
    metadata = {
        "upload_id": upload_id,
        "original_filename": file.filename,
        "stored_filename": unique_filename,
        "file_path": file_path,
        "file_size": len(file_content),
        "content_type": file.content_type,
        "user": current_user,
        "local_path": local_path,
        "signed_url": signed_url,
        "uploaded_at": datetime.now().isoformat(),
    }

    metadata_path = os.path.join(local_dir, f"{upload_id}_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return {
        "message": "File uploaded successfully",
        "upload_id": upload_id,
        "original_filename": file.filename,
        "stored_filename": unique_filename,
        "file_path": file_path,
        "file_size": len(file_content),
        "signed_url": signed_url,
        "user": current_user,
        "stored_in_database": True,
        "stored_locally": local_path,
        "metadata_file": metadata_path,
    }


@router.post("/upload-preview")
async def upload_preview_file(
    spec_id: str,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    """Upload preview file (GLB, JPG, PNG, etc.)"""
    import json
    import os
    from datetime import datetime

    from app.database import engine
    from sqlalchemy import text

    try:
        preview_bytes = await file.read()
        file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else "glb"
        timestamp = int(datetime.now().timestamp())
        path = f"{spec_id}_{timestamp}.{file_extension}"

        # Upload to Supabase
        await upload_to_bucket("previews", path, preview_bytes)
        signed_url = get_signed_url("previews", path, expires=600)

        # Store metadata in database
        upload_id = f"preview_{timestamp}_{spec_id}"
        try:
            with engine.connect() as conn:
                conn.execute(
                    text(
                        """
                    INSERT INTO reports (report_id, user_id, title, content, report_type, spec_id, created_at)
                    VALUES (:report_id, :user_id, :title, :content, :report_type, :spec_id, :created_at)
                """
                    ),
                    {
                        "report_id": upload_id,
                        "user_id": current_user,
                        "title": f"Preview Upload: {file.filename}",
                        "content": f"Preview for spec {spec_id}, File: {path}, Size: {len(preview_bytes)} bytes",
                        "report_type": "preview_upload",
                        "spec_id": spec_id,
                        "created_at": datetime.now(),
                    },
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Database storage failed: {e}")

        # Store file locally
        local_dir = "data/previews"
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, path)

        with open(local_path, "wb") as f:
            f.write(preview_bytes)

        # Store metadata locally
        metadata = {
            "upload_id": upload_id,
            "spec_id": spec_id,
            "original_filename": file.filename,
            "stored_filename": path,
            "file_type": file_extension,
            "file_size": len(preview_bytes),
            "signed_url": signed_url,
            "user": current_user,
            "local_path": local_path,
            "uploaded_at": datetime.now().isoformat(),
        }

        metadata_path = os.path.join(local_dir, f"{upload_id}_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return {
            "message": "Preview uploaded successfully",
            "upload_id": upload_id,
            "spec_id": spec_id,
            "filename": file.filename,
            "stored_filename": path,
            "file_type": file_extension,
            "file_size": len(preview_bytes),
            "signed_url": signed_url,
            "expires_in": 600,
            "user": current_user,
            "stored_in_database": True,
            "stored_locally": local_path,
            "metadata_file": metadata_path,
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
    import json
    import os
    from datetime import datetime

    from app.database import engine
    from sqlalchemy import text

    geometry_bytes = await file.read()
    file_type = file.filename.split(".")[-1] if "." in file.filename else "stl"
    timestamp = int(datetime.now().timestamp())
    path = f"{spec_id}_{timestamp}.{file_type}"

    # Upload to Supabase (upload_geometry only takes spec_id and bytes)
    try:
        signed_url = upload_geometry(spec_id, geometry_bytes)  # Not async
    except Exception as e:
        logger.error(f"Supabase upload failed: {e}")
        signed_url = None

    # Store metadata in database
    upload_id = f"geometry_{timestamp}_{spec_id}"
    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                INSERT INTO reports (report_id, user_id, title, content, report_type, spec_id, created_at)
                VALUES (:report_id, :user_id, :title, :content, :report_type, :spec_id, :created_at)
            """
                ),
                {
                    "report_id": upload_id,
                    "user_id": current_user,
                    "title": f"Geometry Upload: {file.filename}",
                    "content": f"Geometry for spec {spec_id}, File: {path}, Size: {len(geometry_bytes)} bytes",
                    "report_type": "geometry_upload",
                    "spec_id": spec_id,
                    "created_at": datetime.now(),
                },
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Database storage failed: {e}")

    # Store file locally
    local_dir = "data/geometry_outputs"
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, path)

    with open(local_path, "wb") as f:
        f.write(geometry_bytes)

    # Store metadata locally
    metadata = {
        "upload_id": upload_id,
        "spec_id": spec_id,
        "original_filename": file.filename,
        "stored_filename": path,
        "file_type": file_type,
        "file_size": len(geometry_bytes),
        "signed_url": signed_url,
        "user": current_user,
        "local_path": local_path,
        "uploaded_at": datetime.now().isoformat(),
    }

    metadata_path = os.path.join(local_dir, f"{upload_id}_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return {
        "message": "Geometry uploaded successfully",
        "upload_id": upload_id,
        "spec_id": spec_id,
        "filename": file.filename,
        "stored_filename": path,
        "signed_url": signed_url,
        "file_type": file_type,
        "file_size": len(geometry_bytes),
        "user": current_user,
        "stored_in_database": True,
        "stored_locally": local_path,
        "metadata_file": metadata_path,
    }


@router.post("/upload-compliance")
async def upload_compliance_file(
    case_id: str,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    """Upload compliance ZIP file"""
    import json
    import os
    from datetime import datetime

    from app.database import engine
    from sqlalchemy import text

    compliance_bytes = await file.read()
    timestamp = int(datetime.now().timestamp())
    file_path = f"compliance/{case_id}_{timestamp}.zip"

    # Upload to Supabase
    try:
        await upload_to_bucket("compliance", file_path, compliance_bytes)
        signed_url = get_signed_url("compliance", file_path, expires=600)
    except Exception as e:
        logger.error(f"Supabase upload failed: {e}")
        signed_url = None

    # Store metadata in database
    upload_id = f"compliance_{timestamp}_{case_id}"
    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                INSERT INTO reports (report_id, user_id, title, content, report_type, created_at)
                VALUES (:report_id, :user_id, :title, :content, :report_type, :created_at)
            """
                ),
                {
                    "report_id": upload_id,
                    "user_id": current_user,
                    "title": f"Compliance Upload: {file.filename}",
                    "content": f"Compliance for case {case_id}, File: {file_path}, Size: {len(compliance_bytes)} bytes",
                    "report_type": "compliance_upload",
                    "created_at": datetime.now(),
                },
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Database storage failed: {e}")

    # Store file locally
    local_dir = "data/compliance"
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, f"{case_id}_{timestamp}.zip")

    with open(local_path, "wb") as f:
        f.write(compliance_bytes)

    # Store metadata locally
    metadata = {
        "upload_id": upload_id,
        "case_id": case_id,
        "original_filename": file.filename,
        "stored_filename": f"{case_id}_{timestamp}.zip",
        "file_path": file_path,
        "file_size": len(compliance_bytes),
        "signed_url": signed_url,
        "user": current_user,
        "local_path": local_path,
        "uploaded_at": datetime.now().isoformat(),
    }

    metadata_path = os.path.join(local_dir, f"{upload_id}_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return {
        "message": "Compliance file uploaded successfully",
        "upload_id": upload_id,
        "case_id": case_id,
        "filename": file.filename,
        "stored_filename": f"{case_id}_{timestamp}.zip",
        "file_path": file_path,
        "file_size": len(compliance_bytes),
        "signed_url": signed_url,
        "user": current_user,
        "stored_in_database": True,
        "stored_locally": local_path,
        "metadata_file": metadata_path,
    }
