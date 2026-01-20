from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.auth import dependencies
from app.services.user_mongodb import UserMongoService
from app.models.user_mongo import UserDocument, UserCreate, UserUpdate, UserResponse
from pydantic import BaseModel

router = APIRouter()

class UserOut(BaseModel):
    user_id: int
    email: str
    is_active: bool
    is_superuser: bool
    role_name: str | None = None

@router.get("/me", response_model=UserOut)
async def read_user_me(
    current_user: UserDocument = Depends(dependencies.get_current_user),
) -> Any:
    return UserOut(
        user_id=current_user.user_id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        role_name=current_user.role_name
    )

# LLM Configuration
class LLMConfigUpdate(BaseModel):
    llm_provider: str
    llm_model: str
    llm_api_key: str | None = None  # Optional, if updating

class LLMConfigOut(BaseModel):
    llm_provider: str | None
    llm_model: str | None
    has_api_key: bool

@router.get("/me/llm-config", response_model=LLMConfigOut)
async def read_user_llm_config(
    current_user: UserDocument = Depends(dependencies.get_current_user),
) -> Any:
    return LLMConfigOut(
        llm_provider=current_user.llm_provider,
        llm_model=current_user.llm_model,
        has_api_key=bool(current_user.llm_api_key_encrypted)
    )

@router.put("/me/llm-config", response_model=LLMConfigOut)
async def update_user_llm_config(
    config: LLMConfigUpdate,
    current_user: UserDocument = Depends(dependencies.get_current_user),
) -> Any:
    update_data = UserUpdate(
        llm_provider=config.llm_provider,
        llm_model=config.llm_model
    )
    
    if config.llm_api_key:
        from app.services.credential_encryptor import encryptor
        update_data.llm_api_key_encrypted = encryptor.encrypt(config.llm_api_key)
    
    updated_user = await UserMongoService.update_user(current_user.user_id, update_data)
    
    return LLMConfigOut(
        llm_provider=updated_user.llm_provider if updated_user else None,
        llm_model=updated_user.llm_model if updated_user else None,
        has_api_key=bool(updated_user.llm_api_key_encrypted) if updated_user else False
    )
