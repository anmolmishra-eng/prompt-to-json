from datetime import datetime, timedelta, timezone

import jwt
from app.config import settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

# Hardcoded users for demo
USERS_DB = {"user": "pass", "admin": "bhiv2024", "demo": "demo123"}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate user credentials
    if form_data.username not in USERS_DB or USERS_DB[form_data.username] != form_data.password:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {"code": "INVALID_CREDENTIALS", "message": "Invalid username or password", "status_code": 401}
            },
        )

    # Create JWT token
    token_data = {
        "sub": form_data.username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
    }
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
