from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from app.db.session import get_db
from app.auth import dependencies
from app.models.user import User
from app.models.query_history import QueryHistory
from app.models.db_connection import DBConnection
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class QueryHistoryOut(BaseModel):
    id: int
    question: str
    generated_sql: Optional[str]
    intent: Optional[str]
    confidence_score: Optional[float]
    execution_status: Optional[str]
    error_message: Optional[str]
    created_at: Optional[datetime]
    connection_name: str
    insights: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[QueryHistoryOut])
def list_query_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    """
    List query history for the current user.
    """
    history = (
        db.query(QueryHistory)
        .filter(QueryHistory.user_id == current_user.id)
        .order_by(QueryHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Enrich with connection name manually or use DB relationship
    results = []
    for h in history:
        # Access relationship
        conn_name = h.connection.name if h.connection else "Unknown"
        results.append(QueryHistoryOut(
            id=h.id,
            question=h.question,
            generated_sql=h.generated_sql,
            intent=h.intent,
            confidence_score=h.confidence_score,
            execution_status=h.execution_status,
            error_message=h.error_message,
            created_at=h.created_at,
            connection_name=conn_name,
            insights=h.insights
        ))
    return results

@router.get("/{history_id}", response_model=QueryHistoryOut)
def get_query_history_item(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    """
    Get details of a specific query execution.
    """
    item = db.query(QueryHistory).filter(QueryHistory.id == history_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="History item not found")
        
    if item.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    conn_name = item.connection.name if item.connection else "Unknown"
    return QueryHistoryOut(
        id=item.id,
        question=item.question,
        generated_sql=item.generated_sql,
        intent=item.intent,
        confidence_score=item.confidence_score,
        execution_status=item.execution_status,
        error_message=item.error_message,
        created_at=item.created_at,
        connection_name=conn_name,
        insights=item.insights
    )
