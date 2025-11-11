from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import GenerateRequest, EvaluateRequest, IterateRequest, SwitchRequest
from app.database import get_current_user, get_db
from app.api.generate import generate
from app.api.evaluate import evaluate
from app.api.iterate import iterate
from app.api.switch import switch

router = APIRouter()

@router.post("/mobile/generate")
async def mobile_generate(
    req: GenerateRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mobile wrapper for generate endpoint"""
    return await generate(req, current_user, db)

@router.post("/mobile/evaluate")
async def mobile_evaluate(
    req: EvaluateRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mobile wrapper for evaluate endpoint"""
    return await evaluate(req, current_user, db)

@router.post("/mobile/iterate")
async def mobile_iterate(
    req: IterateRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mobile wrapper for iterate endpoint"""
    return await iterate(req, current_user, db)

@router.post("/mobile/switch")
async def mobile_switch(
    req: SwitchRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mobile wrapper for switch endpoint"""
    return await switch(req, current_user, db)

@router.get("/mobile/health")
async def mobile_health():
    """Mobile-specific health check"""
    return {
        "status": "ok",
        "platform": "mobile",
        "api_version": "v1"
    }