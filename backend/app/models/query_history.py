from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class QueryHistory(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    connection_id = Column(Integer, ForeignKey("db_connection.id"), nullable=False)
    
    # Input
    question = Column(Text, nullable=False)
    
    # AI Output
    generated_sql = Column(Text, nullable=True)
    intent = Column(String(50), nullable=True) # READ, WRITE, etc.
    confidence_score = Column(Float, default=0.0)
    is_ambiguous = Column(Boolean, default=False)
    
    # Insights (Phase 5)
    insights = Column(JSON, nullable=True) # Stores structured insights {impact, scope, etc}
    
    # Execution Result
    execution_status = Column(String(50), default="PENDING") # PENDING, SUCCESS, ERROR
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="query_history")
    connection = relationship("DBConnection", back_populates="query_history")
