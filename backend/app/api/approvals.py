from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.session import get_db
from app.models.approval import QueryApproval, ApprovalStatus
from app.models.user import User
from app.auth import dependencies
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()

# Pydantic Models
class ApprovalOut(BaseModel):
    id: int
    requested_by_user_id: int
    reviewed_by_user_id: Optional[int]
    db_connection_id: int
    prompt_text: Optional[str]
    generated_sql: Optional[str]
    impact_summary: Optional[str]
    risk_level: Optional[str]
    status: str
    reviewer_comment: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ApprovalActionRequest(BaseModel):
    comment: Optional[str] = None

@router.get("/", response_model=List[ApprovalOut])
def list_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user),
):
    """List all pending approvals (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    approvals = db.query(QueryApproval).filter(
        QueryApproval.status == ApprovalStatus.PENDING
    ).order_by(desc(QueryApproval.created_at)).all()
    
    return approvals

@router.get("/my-requests", response_model=List[ApprovalOut])
def list_my_approval_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user),
):
    """List current user's approval requests"""
    approvals = db.query(QueryApproval).filter(
        QueryApproval.requested_by_user_id == current_user.user_id
    ).order_by(desc(QueryApproval.created_at)).all()
    
    return approvals

@router.get("/{approval_id}", response_model=ApprovalOut)
def get_approval_details(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user),
):
    """Get approval details"""
    approval = db.query(QueryApproval).filter(QueryApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    # Check permissions: owner or admin
    if approval.requested_by_user_id != current_user.user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return approval

@router.post("/{approval_id}/approve", response_model=ApprovalOut)
def approve_request(
    approval_id: int,
    action: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user),
):
    """Approve an approval request (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    approval = db.query(QueryApproval).filter(QueryApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail="Approval already processed")
    
    approval.status = ApprovalStatus.APPROVED
    approval.reviewed_by_user_id = current_user.user_id
    approval.reviewed_at = datetime.utcnow()
    approval.reviewer_comment = action.comment
    
    db.commit()
    db.refresh(approval)
    
    return approval

@router.post("/{approval_id}/reject", response_model=ApprovalOut)
def reject_request(
    approval_id: int,
    action: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user),
):
    """Reject an approval request (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    approval = db.query(QueryApproval).filter(QueryApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail="Approval already processed")
    
    approval.status = ApprovalStatus.REJECTED
    approval.reviewed_by_user_id = current_user.user_id
    approval.reviewed_at = datetime.utcnow()
    approval.reviewer_comment = action.comment
    
    db.commit()
    db.refresh(approval)
    
    return approval
