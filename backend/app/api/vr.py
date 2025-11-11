from app.database import get_current_user
from app.storage import get_signed_url
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.get("/vr/preview/{spec_id}")
async def vr_preview(spec_id: str, current_user: str = Depends(get_current_user)):
    """Get VR-optimized preview URL for spec"""
    try:
        # Get latest version preview
        preview_url = await get_signed_url("previews", f"{spec_id}.glb", expires=600)

        return {
            "spec_id": spec_id,
            "preview_url": preview_url,
            "format": "glb",
            "expires_in": 600,
            "vr_optimized": True,
        }
    except Exception:
        raise HTTPException(status_code=404, detail="Preview not found")


@router.get("/vr/render/{spec_id}")
async def vr_render(
    spec_id: str, quality: str = "high", current_user: str = Depends(get_current_user)
):
    """VR rendering endpoint stub"""
    # Placeholder for Bhavesh's VR rendering integration
    return {
        "spec_id": spec_id,
        "render_status": "queued",
        "quality": quality,
        "estimated_time": "30s",
        "render_id": f"vr_render_{spec_id}_{quality}",
    }


@router.get("/vr/status/{render_id}")
async def vr_render_status(
    render_id: str, current_user: str = Depends(get_current_user)
):
    """Check VR render status"""
    # Placeholder for render status checking
    return {
        "render_id": render_id,
        "status": "completed",
        "progress": 100,
        "vr_url": f"https://storage.supabase.co/vr/{render_id}.glb?signed=...",
    }


@router.post("/vr/feedback")
async def vr_feedback(feedback: dict, current_user: str = Depends(get_current_user)):
    """Submit VR experience feedback"""
    return {
        "feedback_id": f"vr_fb_{feedback.get('spec_id', 'unknown')}",
        "status": "received",
        "message": "VR feedback recorded",
    }
