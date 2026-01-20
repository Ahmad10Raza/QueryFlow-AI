from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.db_connection import DBConnection
from app.auth import dependencies
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class DBConnectionCreate(BaseModel):
    name: str
    db_type: str
    host: str
    port: int
    username: str
    password: str
    database_name: str

class DBConnectionOut(BaseModel):
    id: int
    name: str
    db_type: str
    host: str
    username: str
    database_name: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[DBConnectionOut])
def read_db_connections(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(dependencies.get_current_user),
) -> Any:
    connections = db.query(DBConnection).filter(DBConnection.owner_id == current_user.user_id).offset(skip).limit(limit).all()
    return connections

@router.post("/test")
def test_db_connection(
    *,
    connection_in: DBConnectionCreate,
    current_user: User = Depends(dependencies.get_current_user),
) -> Any:
    """Test a database connection without saving it."""
    from app.services.db_connector import db_connector
    
    connection_details = {
        "db_type": connection_in.db_type,
        "username": connection_in.username,
        "host": connection_in.host,
        "port": connection_in.port,
        "database_name": connection_in.database_name
    }
    
    success, message = db_connector.test_connection(connection_details, connection_in.password)
    
    return {
        "success": success,
        "message": message
    }

@router.post("/", response_model=DBConnectionOut)
def create_db_connection(
    *,
    db: Session = Depends(get_db),
    connection_in: DBConnectionCreate,
    current_user: User = Depends(dependencies.get_current_user),
) -> Any:
    from app.services.db_connector import db_connector
    from app.services.credential_encryptor import encryptor
    
    print(f"DEBUG: Received connection request: {connection_in.name}, {connection_in.db_type}")
    
    # Test connection first
    connection_details = {
        "db_type": connection_in.db_type,
        "username": connection_in.username,
        "host": connection_in.host,
        "port": connection_in.port,
        "database_name": connection_in.database_name
    }
    
    print(f"DEBUG: Testing connection to {connection_in.host}:{connection_in.port}/{connection_in.database_name}")
    success, message = db_connector.test_connection(connection_details, connection_in.password)
    print(f"DEBUG: Connection test result: success={success}, message={message}")
    
    if not success:
        print(f"DEBUG: Raising HTTPException with message: {message}")
        raise HTTPException(status_code=400, detail=f"Connection test failed: {message}")
    
    # Encrypt password
    encrypted_password = encryptor.encrypt(connection_in.password)
    
    # Create connection with encrypted password
    db_conn = DBConnection(
        name=connection_in.name,
        db_type=connection_in.db_type,
        host=connection_in.host,
        port=connection_in.port,
        username=connection_in.username,
        password_encrypted=encrypted_password,
        database_name=connection_in.database_name,
        owner_id=current_user.user_id
    )
    db.add(db_conn)
    db.commit()
    db.refresh(db_conn)
    return db_conn


