from enum import Enum
from typing import Dict, List, Set

class Permission(str, Enum):
    # Data Access
    READ = "data:read"
    KEYWORD_SEARCH = "data:search"
    
    # Write Operations
    UPDATE_SINGLE = "data:update:single" # Safe update (single row/where clause)
    UPDATE_MULTI = "data:update:multi"   # Riskier update (multiple rows)
    DELETE = "data:delete"               # Delete rows
    
    # Schema
    SCHEMA_READ = "schema:read"
    SCHEMA_INGEST = "schema:ingest"
    
    # Administration
    MANAGE_USERS = "admin:users"
    MANAGE_CONNECTIONS = "admin:connections"
    APPROVE_QUERIES = "admin:approval"

# Role Definitions
# Supports both legacy (VIEWER/EDITOR) and new (USER/MANAGER) role names
ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
    # Legacy role names
    "VIEWER": {
        Permission.READ,
        Permission.KEYWORD_SEARCH,
        Permission.SCHEMA_READ,
    },
    "EDITOR": {
        Permission.READ,
        Permission.KEYWORD_SEARCH,
        Permission.SCHEMA_READ,
        Permission.SCHEMA_INGEST,
        Permission.UPDATE_SINGLE,
        Permission.UPDATE_MULTI,
    },
    "ADMIN": {
        Permission.READ,
        Permission.KEYWORD_SEARCH,
        Permission.SCHEMA_READ,
        Permission.SCHEMA_INGEST,
        Permission.UPDATE_SINGLE,
        Permission.UPDATE_MULTI,
        Permission.DELETE,
        Permission.MANAGE_USERS,
        Permission.MANAGE_CONNECTIONS,
        Permission.APPROVE_QUERIES
    },
    # New role names (aliases)
    "USER": {
        Permission.READ,
        Permission.KEYWORD_SEARCH,
        Permission.SCHEMA_READ,
    },
    "MANAGER": {
        Permission.READ,
        Permission.KEYWORD_SEARCH,
        Permission.SCHEMA_READ,
        Permission.SCHEMA_INGEST,
        Permission.UPDATE_SINGLE,
        Permission.UPDATE_MULTI,
    },
}


def can_execute_directly(user, intent: str) -> bool:
    """
    Check if user can execute query type directly without approval.
    
    RBAC Rules:
    - ADMIN/SUPERUSER: Can execute any query directly
    - EDITOR (Manager): Can execute READ/UPDATE directly, needs approval for DELETE
    - VIEWER (User): Can only execute READ directly, needs approval for UPDATE/DELETE
    
    Args:
        user: Current user object with role_name and is_superuser
        intent: Query intent (READ, UPDATE, DELETE)
    
    Returns:
        True if user can execute directly, False if approval required
    """
    # Admins and superusers can do anything
    if user.is_superuser:
        return True
    
    role_name = getattr(user, 'role_name', 'VIEWER')
    
    if role_name == "ADMIN":
        return True  # Admin can do everything
    
    if role_name in ["EDITOR", "MANAGER"]:  # Manager
        # Can READ and UPDATE directly, needs approval for DELETE
        return intent in ["READ", "UPDATE"]
    
    if role_name in ["VIEWER", "USER"]:  # Regular user
        # Can only READ directly
        return intent == "READ"
    
    # Default: deny direct execution
    return False


def get_user_permissions(role_name: str) -> Set[Permission]:
    """Get permissions for a given role."""
    return ROLE_PERMISSIONS.get(role_name, set())
