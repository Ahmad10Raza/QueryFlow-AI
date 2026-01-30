from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class QueryRequest(Base):
    """
    Model for storing query execution requests that require admin approval.
    Used for UPDATE/DELETE operations by non-admin users.
    """
    __tablename__ = "query_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Requester (MongoDB user_id)
    connection_id = Column(Integer, ForeignKey("db_connection.id"), nullable=False)
    
    # Query Details
    question = Column(Text, nullable=False)  # Original NL question
    generated_sql = Column(Text, nullable=False)  # SQL/MongoDB query to execute
    intent = Column(String(50), nullable=False)  # READ, UPDATE, DELETE
    
    # Request Status: PENDING, APPROVED, REJECTED, EXECUTED
    status = Column(String(20), default="PENDING", nullable=False)
    
    # Approval Details
    approved_by = Column(Integer, nullable=True)  # Admin user_id who approved/rejected
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    connection = relationship("DBConnection")
