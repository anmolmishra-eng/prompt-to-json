from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt
from app.config import settings

router = APIRouter()

# Hardcoded users for demo
USERS_DB = {
    "user": "pass",
    "admin": "bhiv2024",
    "demo": "demo123"
}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate user credentials
    if form_data.username not in USERS_DB or USERS_DB[form_data.username] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    token_data = {
        "sub": form_data.username,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}