from fastapi import APIRouter
from app.schemas import MessageResponse

router = APIRouter()

@router.get("/", response_model=MessageResponse, name="Service Status")
async def service_status():
    return MessageResponse(message="Design Engine API is running")