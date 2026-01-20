from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum

class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class QueryApproval(Base):
    __tablename__ = "query_approvals"

    id = Column(Integer, primary_key=True, index=True)
    
    requested_by_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    reviewed_by_user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    
    db_connection_id = Column(Integer, ForeignKey("db_connection.id"), nullable=False)
    
    # The Query
    prompt_text = Column(Text)
    generated_sql = Column(Text)
    
    # Risk Info
    impact_summary = Column(Text) # JSON string of impact analysis
    risk_level = Column(String(50)) # "MEDIUM", "HIGH"
    
    status = Column(SqlEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    reviewer_comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
