from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.db.session import get_db
from app.auth import dependencies
from app.models.user import User
from app.models.query_request import QueryRequest
from app.models.db_connection import DBConnection
from app.query_executor.executor import execute_sql_query, execute_mongo_query
from app.services.credential_encryptor import encryptor

router = APIRouter()


# Pydantic Schemas
class QueryRequestCreate(BaseModel):
    connection_id: int
    question: str
    generated_sql: str
    intent: str


class QueryRequestOut(BaseModel):
    id: int
    user_id: int
    connection_id: int
    connection_name: str
    question: str
    generated_sql: str
    intent: str
    status: str
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: Optional[datetime]
    executed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApprovalRequest(BaseModel):
    rejection_reason: Optional[str] = None


# Helper: Check if user is admin
def is_admin(user) -> bool:
    return user.is_superuser or user.role_name == "ADMIN"


@router.post("/", response_model=QueryRequestOut)
def create_query_request(
    request: QueryRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    """Create a new query request for admin approval."""
    # Verify connection exists and user has access
    conn = db.query(DBConnection).filter(DBConnection.id == request.connection_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    if conn.owner_id != current_user.user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to use this connection")
    
    query_request = QueryRequest(
        user_id=current_user.user_id,
        connection_id=request.connection_id,
        question=request.question,
        generated_sql=request.generated_sql,
        intent=request.intent,
        status="PENDING"
    )
    
    db.add(query_request)
    db.commit()
    db.refresh(query_request)
    
    conn_name = conn.name if conn else "Unknown"
    
    return QueryRequestOut(
        id=query_request.id,
        user_id=query_request.user_id,
        connection_id=query_request.connection_id,
        connection_name=conn_name,
        question=query_request.question,
        generated_sql=query_request.generated_sql,
        intent=query_request.intent,
        status=query_request.status,
        approved_by=query_request.approved_by,
        approved_at=query_request.approved_at,
        rejection_reason=query_request.rejection_reason,
        created_at=query_request.created_at,
        executed_at=query_request.executed_at
    )


@router.get("/", response_model=List[QueryRequestOut])
def list_my_requests(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    """List query requests created by the current user."""
    requests = (
        db.query(QueryRequest)
        .filter(QueryRequest.user_id == current_user.user_id)
        .order_by(QueryRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    results = []
    for req in requests:
        conn_name = req.connection.name if req.connection else "Unknown"
        results.append(QueryRequestOut(
            id=req.id,
            user_id=req.user_id,
            connection_id=req.connection_id,
            connection_name=conn_name,
            question=req.question,
            generated_sql=req.generated_sql,
            intent=req.intent,
            status=req.status,
            approved_by=req.approved_by,
            approved_at=req.approved_at,
            rejection_reason=req.rejection_reason,
            created_at=req.created_at,
            executed_at=req.executed_at
        ))
    
    return results


@router.get("/pending", response_model=List[QueryRequestOut])
def list_pending_requests(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    """List all pending query requests (Admin only)."""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    requests = (
        db.query(QueryRequest)
        .filter(QueryRequest.status == "PENDING")
        .order_by(QueryRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    results = []
    for req in requests:
        conn_name = req.connection.name if req.connection else "Unknown"
        results.append(QueryRequestOut(
            id=req.id,
            user_id=req.user_id,
            connection_id=req.connection_id,
            connection_name=conn_name,
            question=req.question,
            generated_sql=req.generated_sql,
            intent=req.intent,
            status=req.status,
            approved_by=req.approved_by,
            approved_at=req.approved_at,
            rejection_reason=req.rejection_reason,
            created_at=req.created_at,
            executed_at=req.executed_at
        ))
    
    return results


@router.put("/{request_id}/approve", response_model=QueryRequestOut)
def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    """Approve a pending query request (Admin only)."""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    req = db.query(QueryRequest).filter(QueryRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Request is already {req.status}")
    
    req.status = "APPROVED"
    req.approved_by = current_user.user_id
    req.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(req)
    
    conn_name = req.connection.name if req.connection else "Unknown"
    
    return QueryRequestOut(
        id=req.id,
        user_id=req.user_id,
        connection_id=req.connection_id,
        connection_name=conn_name,
        question=req.question,
        generated_sql=req.generated_sql,
        intent=req.intent,
        status=req.status,
        approved_by=req.approved_by,
        approved_at=req.approved_at,
        rejection_reason=req.rejection_reason,
        created_at=req.created_at,
        executed_at=req.executed_at
    )


@router.put("/{request_id}/reject", response_model=QueryRequestOut)
def reject_request(
    request_id: int,
    body: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    """Reject a pending query request (Admin only)."""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    req = db.query(QueryRequest).filter(QueryRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Request is already {req.status}")
    
    req.status = "REJECTED"
    req.approved_by = current_user.user_id
    req.approved_at = datetime.utcnow()
    req.rejection_reason = body.rejection_reason
    
    db.commit()
    db.refresh(req)
    
    conn_name = req.connection.name if req.connection else "Unknown"
    
    return QueryRequestOut(
        id=req.id,
        user_id=req.user_id,
        connection_id=req.connection_id,
        connection_name=conn_name,
        question=req.question,
        generated_sql=req.generated_sql,
        intent=req.intent,
        status=req.status,
        approved_by=req.approved_by,
        approved_at=req.approved_at,
        rejection_reason=req.rejection_reason,
        created_at=req.created_at,
        executed_at=req.executed_at
    )


@router.post("/{request_id}/execute")
def execute_approved_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    """Execute an approved query request."""
    req = db.query(QueryRequest).filter(QueryRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Only the original requester can execute their approved request
    if req.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only the requester can execute approved queries")
    
    if req.status != "APPROVED":
        raise HTTPException(status_code=400, detail=f"Request must be APPROVED to execute. Current status: {req.status}")
    
    # Get connection
    conn = db.query(DBConnection).filter(DBConnection.id == req.connection_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # Execute the query
    try:
        if conn.db_type == "mongodb":
            # Parse SQL to MongoDB format
            from app.api.query import sql_to_mongo_query
            mongo_query = sql_to_mongo_query(req.generated_sql)
            result = execute_mongo_query(conn, mongo_query)
        else:
            # Determine if commit is needed based on intent
            # Intents: READ, UPDATE, DELETE, CREATE
            require_commit = req.intent in ["UPDATE", "DELETE", "CREATE", "INSERT"]
            
            result = execute_sql_query(conn, req.generated_sql, require_commit=require_commit)
        
        # Update request status
        req.status = "EXECUTED"
        req.executed_at = datetime.utcnow()
        db.commit()
        
        return {
            "status": "success",
            "request_id": request_id,
            "result": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")
