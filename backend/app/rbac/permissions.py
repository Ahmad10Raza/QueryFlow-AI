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
# In a real app, these might come from the DB, but hardcoded policies are safer for Phase 2.
ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
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
    }
}
