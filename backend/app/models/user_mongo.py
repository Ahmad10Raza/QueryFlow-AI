from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core import core_schema
from typing import Optional, Any, Annotated
from datetime import datetime
from bson import ObjectId

# Pydantic v2 compatible ObjectId
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ],
        serialization=core_schema.plain_serializer_function_ser_schema(
            lambda x: str(x)
        ))
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

class RoleDocument(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    role_id: int  # For backward compatibility with SQL
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserDocument(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: int  # For backward compatibility with SQL (used in Query History FK)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    role_id: int  # References role.role_id
    role_name: Optional[str] = None  # Denormalized for quick access
    
    # LLM Configuration
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_api_key_encrypted: Optional[bytes] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, bytes: lambda b: b.decode() if b else None}

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_superuser: bool = False
    role_id: int = 1  # Default to USER role

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role_id: Optional[int] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_api_key_encrypted: Optional[bytes] = None

class UserResponse(BaseModel):
    user_id: int
    email: str
    is_active: bool
    is_superuser: bool
    role_name: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    has_api_key: bool = False
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True
