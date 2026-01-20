from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core import security
from app.auth import jwt
from app.core.config import settings
from app.services.user_mongodb import UserMongoService

router = APIRouter()

@router.post("/login", response_model=dict)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = await UserMongoService.get_user_by_email(form_data.username)
    if not user or not await UserMongoService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    # Update last login
    await UserMongoService.update_last_login(user.user_id)
    
    # Audit Log
    from app.services.audit import AuditService
    try:
        await AuditService.log_user_activity(
            user_id=user.user_id,
            user_email=user.email,
            action="LOGIN",
            details={"ip": "unknown"} # In real app, extract from Request object
        )
    except Exception as e:
        print(f"WARN: Failed to log login: {e}")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": jwt.create_access_token(
            {"sub": user.email}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
