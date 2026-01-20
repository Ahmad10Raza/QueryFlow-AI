from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.auth.dependencies import require_admin
from app.db.user_mongo import get_user_mongo_db
from app.models.user_mongo import UserDocument
from app.models.query_history import QueryHistory
from app.models.approval import QueryApproval
from datetime import datetime, time
from pydantic import BaseModel

router = APIRouter()

class SystemStats(BaseModel):
    total_users: int
    active_users_today: int
    total_queries: int
    queries_today: int
    failed_queries_today: int
    pending_approvals: int

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: UserDocument = Depends(require_admin)
):
    """
    Get real-time system statistics
    """
    # MongoDB connections
    mongo_db = await get_user_mongo_db()
    
    # 1. User Stats (MongoDB)
    total_users = await mongo_db.users.count_documents({})
    
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    active_users_today = await mongo_db.users.count_documents({
        "last_login_at": {"$gte": today_start}
    })
    
    # 2. Query Stats (SQL)
    # We use sync SQL queries here. For high load, consider async SQL or run_in_threadpool
    today_date = datetime.utcnow().date()
    
    total_queries = db.query(func.count(QueryHistory.id)).scalar()
    
    queries_today = db.query(func.count(QueryHistory.id)).filter(
        func.date(QueryHistory.created_at) == today_date
    ).scalar() or 0
    
    failed_queries_today = db.query(func.count(QueryHistory.id)).filter(
        func.date(QueryHistory.created_at) == today_date,
        QueryHistory.execution_status == "ERROR"
    ).scalar() or 0
    
    pending_approvals = db.query(func.count(QueryApproval.id)).filter(
        QueryApproval.status == "PENDING"
    ).scalar() or 0
    
    return SystemStats(
        total_users=total_users,
        active_users_today=active_users_today,
        total_queries=total_queries or 0,
        queries_today=queries_today,
        failed_queries_today=failed_queries_today,
        pending_approvals=pending_approvals
    )
