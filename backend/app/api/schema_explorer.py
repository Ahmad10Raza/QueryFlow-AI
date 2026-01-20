from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.models.db_connection import DBConnection
from app.auth import dependencies
from app.models.user import User
from app.services.db_connector import db_connector
from app.services.credential_encryptor import encryptor

router = APIRouter()

def get_mysql_schema_structure(engine) -> Dict[str, Any]:
    """Fetch schema structure for the connected database in MySQL."""
    with engine.connect() as conn:
        # Get connected database name
        db_name_result = conn.execute(text("SELECT DATABASE()"))
        current_db = db_name_result.scalar()
        
        # Only process the connected database
        databases = [current_db] if current_db else []
        
        db_structures = []
        for db_name in databases:
            # Get tables with column count
            tables_query = text("""
                SELECT 
                    TABLE_NAME as name,
                    TABLE_TYPE as type,
                    TABLE_ROWS as row_count,
                    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                     WHERE TABLE_SCHEMA = :db_name AND TABLE_NAME = t.TABLE_NAME) as column_count
                FROM INFORMATION_SCHEMA.TABLES t
                WHERE TABLE_SCHEMA = :db_name AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            tables = [dict(row._mapping) for row in conn.execute(tables_query, {"db_name": db_name})]
            
            # Get views
            views_query = text("""
                SELECT TABLE_NAME as name
                FROM INFORMATION_SCHEMA.VIEWS
                WHERE TABLE_SCHEMA = :db_name
                ORDER BY TABLE_NAME
            """)
            views = [dict(row._mapping) for row in conn.execute(views_query, {"db_name": db_name})]
            
            # Get indexes
            indexes_query = text("""
                SELECT DISTINCT INDEX_NAME as name, TABLE_NAME as table_name
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = :db_name AND INDEX_NAME != 'PRIMARY'
                ORDER BY INDEX_NAME
            """)
            indexes = [dict(row._mapping) for row in conn.execute(indexes_query, {"db_name": db_name})]
            
            # Get procedures
            procedures_query = text("""
                SELECT ROUTINE_NAME as name, ROUTINE_TYPE as type
                FROM INFORMATION_SCHEMA.ROUTINES
                WHERE ROUTINE_SCHEMA = :db_name AND ROUTINE_TYPE = 'PROCEDURE'
                ORDER BY ROUTINE_NAME
            """)
            procedures = [dict(row._mapping) for row in conn.execute(procedures_query, {"db_name": db_name})]
            
            # Get triggers
            triggers_query = text("""
                SELECT TRIGGER_NAME as name, EVENT_OBJECT_TABLE as table_name
                FROM INFORMATION_SCHEMA.TRIGGERS
                WHERE TRIGGER_SCHEMA = :db_name
                ORDER BY TRIGGER_NAME
            """)
            triggers = [dict(row._mapping) for row in conn.execute(triggers_query, {"db_name": db_name})]
            
            # Get events
            events_query = text("""
                SELECT EVENT_NAME as name, STATUS as status
                FROM INFORMATION_SCHEMA.EVENTS
                WHERE EVENT_SCHEMA = :db_name
                ORDER BY EVENT_NAME
            """)
            events = [dict(row._mapping) for row in conn.execute(events_query, {"db_name": db_name})]
            
            db_structures.append({
                "database_name": db_name,
                "tables": tables,
                "views": views,
                "indexes": indexes,
                "procedures": procedures,
                "triggers": triggers,
                "events": events
            })
            
        return {
            "is_multi_db": True,
            "databases": db_structures
        }

def get_postgres_schema_structure(engine) -> Dict[str, Any]:
    """Fetch schema structure for PostgreSQL database."""
    with engine.connect() as conn:
        # Get database name
        db_name_result = conn.execute(text("SELECT current_database()"))
        db_name = db_name_result.scalar()
        
        # Get tables from all non-system schemas
        tables_query = text("""
            SELECT 
                schemaname || '.' || tablename as name,
                'BASE TABLE' as type,
                (SELECT COUNT(*) FROM information_schema.columns 
                 WHERE table_name = t.tablename AND table_schema = t.schemaname) as column_count,
                schemaname as schema
            FROM pg_tables t
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schemaname, tablename
        """)
        tables_result = conn.execute(tables_query)
        tables = [dict(row._mapping) for row in tables_result]
        
        # Get views from all non-system schemas
        views_query = text("""
            SELECT 
                schemaname || '.' || viewname as name,
                schemaname as schema
            FROM pg_views
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schemaname, viewname
        """)
        views_result = conn.execute(views_query)
        views = [dict(row._mapping) for row in views_result]
        
        # Get indexes from all non-system schemas
        indexes_query = text("""
            SELECT 
                schemaname || '.' || indexname as name,
                schemaname || '.' || tablename as table_name,
                schemaname as schema
            FROM pg_indexes
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schemaname, indexname
        """)
        indexes_result = conn.execute(indexes_query)
        indexes = [dict(row._mapping) for row in indexes_result]
        
        # PostgreSQL doesn't have procedures/triggers/events in the same way as MySQL
        # Return empty arrays for now
        procedures = []
        triggers = []
        events = []
        
        return {
            "database_name": db_name,
            "tables": tables,
            "views": views,
            "indexes": indexes,
            "procedures": procedures,
            "triggers": triggers,
            "events": events
        }

@router.get("/{connection_id}/structure")
def get_schema_structure(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user),
) -> Any:
    """Get the schema structure for a database connection."""
    # Get connection
    # Get connection
    db_conn = db.query(DBConnection).filter(DBConnection.id == connection_id).first()
    
    if not db_conn:
        raise HTTPException(status_code=404, detail="Database connection not found")

    # Check Authorization (Owner OR Super User OR Admin)
    # Using user_id (int) instead of id (ObjectId)
    if db_conn.owner_id != current_user.user_id and not current_user.is_superuser and current_user.role_name != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Decrypt password and create engine
    decrypted_password = encryptor.decrypt(db_conn.password_encrypted)
    engine = db_connector.create_engine_for_connection(db_conn, decrypted_password)
    
    try:
        if db_conn.db_type == "mysql":
            structure = get_mysql_schema_structure(engine)
        elif db_conn.db_type == "postgres":
            structure = get_postgres_schema_structure(engine)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported database type: {db_conn.db_type}")
        
        return structure
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch schema structure: {str(e)}")
    finally:
        engine.dispose()
