from typing import Any, Dict, Optional
from app.models.user import User
from app.models.approval import ApprovalStatus
from app.rbac.permissions import Permission, ROLE_PERMISSIONS

class AccessResult(Dict):
    allowed: bool
    status: ApprovalStatus
    message: str

def evaluate_access(user: User, required_permission: Permission) -> AccessResult:
    """
    Checks if a user has the required permission.
    Returns:
        AccessResult(allowed=True/False, status=..., message=...)
    """
    
    # Get user role (Support both SQL User and MongoDB UserDocument)
    if hasattr(user, "role_name") and user.role_name:
        user_role = user.role_name.upper()
    elif hasattr(user, "role") and user.role:
        user_role = user.role.name.upper()
    else:
        user_role = "VIEWER"
    
    # Get permissions for this role
    allowed_permissions = ROLE_PERMISSIONS.get(user_role, set())
    
    if required_permission in allowed_permissions:
        return {"allowed": True, "status": ApprovalStatus.APPROVED, "message": "Access Granted"}
    
    # Check if this is a WRITE operation that needs approval
    write_permissions = {Permission.UPDATE_SINGLE, Permission.UPDATE_MULTI, Permission.DELETE}
    if required_permission in write_permissions and user_role != "ADMIN":
        return {"allowed": False, "status": "NEEDS_APPROVAL", "message": "This operation requires admin approval"}
    
    # Otherwise, denied
    return {"allowed": False, "status": ApprovalStatus.REJECTED, "message": f"User role '{user_role}' lacks permission '{required_permission}'"}

def determine_required_permission(intent: str, risk_level: str = "LOW") -> Permission:
    """
    Maps an AI intent (e.g. "UPDATE") to a Permission enum.
    """
    if intent == "READ":
        return Permission.READ
    elif intent == "UPDATE_SINGLE":
        return Permission.UPDATE_SINGLE
    elif intent == "UPDATE_MULTI":
        return Permission.UPDATE_MULTI
    elif intent == "DELETE":
        return Permission.DELETE
    else:
        return Permission.READ # Default safety
