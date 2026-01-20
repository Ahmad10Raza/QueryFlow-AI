from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import require_super_admin, require_admin
from app.services.user_mongodb import UserMongoService, RoleMongoService
from app.services.audit import AuditService
from app.models.user_mongo import UserDocument, UserCreate, UserUpdate
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Schema for User Response
class AdminUserResponse(BaseModel):
    user_id: int
    email: str
    is_active: bool
    is_superuser: bool
    role_name: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

# Schema for Role Update
class RoleUpdate(BaseModel):
    role_name: str

# Schema for Status Update
class StatusUpdate(BaseModel):
    is_active: bool

# Schema for User Creation (admin version)
class AdminUserCreate(BaseModel):
    email: str
    password: str
    role_name: str = "USER"

@router.get("/", response_model=List[AdminUserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserDocument = Depends(require_admin)
):
    users = await UserMongoService.get_all_users(skip=skip, limit=limit)
    return [
        AdminUserResponse(
            user_id=u.user_id,
            email=u.email,
            is_active=u.is_active,
            is_superuser=u.is_superuser,
            role_name=u.role_name,
            created_at=u.created_at,
            last_login_at=u.last_login_at
        )
        for u in users
    ]

@router.put("/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_update: RoleUpdate,
    current_user: UserDocument = Depends(require_super_admin)
):
    target_user = await UserMongoService.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if role exists
    new_role = await RoleMongoService.get_role_by_name(role_update.role_name)
    if not new_role:
        raise HTTPException(status_code=400, detail="Invalid role name")
        
    old_role = target_user.role_name or "None"
    
    # Update
    update_data = UserUpdate(
        role_id=new_role.role_id,
        is_superuser=(new_role.name == "SUPER_ADMIN")
    )
    await UserMongoService.update_user(user_id, update_data)
    
    # Audit
    await AuditService.log_user_activity(
        user_id=current_user.user_id,
        user_email=current_user.email,
        action="UPDATE_ROLE",
        target_id=target_user.user_id,
        target_type="USER",
        details={
            "target_email": target_user.email,
            "old_role": old_role,
            "new_role": new_role.name
        }
    )
    
    return {"message": "Role updated successfully"}

@router.put("/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_update: StatusUpdate,
    current_user: UserDocument = Depends(require_super_admin)
):
    target_user = await UserMongoService.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-deactivation
    if target_user.user_id == current_user.user_id and not status_update.is_active:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")

    old_status = target_user.is_active
    update_data = UserUpdate(is_active=status_update.is_active)
    await UserMongoService.update_user(user_id, update_data)
    
    # Audit
    await AuditService.log_user_activity(
        user_id=current_user.user_id,
        user_email=current_user.email,
        action="UPDATE_STATUS",
        target_id=target_user.user_id,
        target_type="USER",
        details={
            "target_email": target_user.email,
            "old_status": old_status,
            "new_status": status_update.is_active
        }
    )
    
    return {"message": "User status updated"}

@router.get("/audit/logs")
async def get_audit_logs(
    limit: int = 50,
    skip: int = 0,
    current_user: UserDocument = Depends(require_admin)
):
    """
    Fetch user activity audit logs from MongoDB
    """
    logs = await AuditService.get_audit_logs(limit=limit, skip=skip)
    return logs

@router.post("/", response_model=AdminUserResponse)
async def create_user(
    user_data: AdminUserCreate,
    current_user: UserDocument = Depends(require_admin)
):
    """
    Create a new user (Super Admin only)
    """
    # Get role
    role = await RoleMongoService.get_role_by_name(user_data.role_name)
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role name")
    
    # Create user
    user_create = UserCreate(
        email=user_data.email,
        password=user_data.password,
        is_superuser=(user_data.role_name == "SUPER_ADMIN"),
        role_id=role.role_id
    )
    
    try:
        new_user = await UserMongoService.create_user(user_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Audit
    await AuditService.log_user_activity(
        user_id=current_user.user_id,
        user_email=current_user.email,
        action="CREATE_USER",
        target_id=new_user.user_id,
        target_type="USER",
        details={
            "created_email": new_user.email,
            "role": user_data.role_name
        }
    )
    
    return AdminUserResponse(
        user_id=new_user.user_id,
        email=new_user.email,
        is_active=new_user.is_active,
        is_superuser=new_user.is_superuser,
        role_name=new_user.role_name,
        created_at=new_user.created_at,
        last_login_at=new_user.last_login_at
    )

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: UserDocument = Depends(require_super_admin)
):
    """
    Soft delete a user (Super Admin only)
    """
    target_user = await UserMongoService.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-deletion
    if target_user.user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Soft delete
    old_email = target_user.email
    await UserMongoService.delete_user(user_id)
    
    # Audit
    await AuditService.log_user_activity(
        user_id=current_user.user_id,
        user_email=current_user.email,
        action="DELETE_USER",
        target_id=target_user.user_id,
        target_type="USER",
        details={
            "deleted_email": old_email
        }
    )
    
    return {"message": "User deleted successfully"}
