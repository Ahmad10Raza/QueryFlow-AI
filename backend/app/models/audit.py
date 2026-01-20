from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.base_class import Base

class ActionAudit(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    action_type = Column(String(50)) # "QUERY_EXECUTION", "APPROVAL_REQUEST", "LOGIN", etc.
    
    # Context
    db_connection_id = Column(Integer, ForeignKey("db_connection.id"), nullable=True)
    
    # Details
    prompt_text = Column(Text, nullable=True) # The NLP question
    generated_sql = Column(Text, nullable=True) # The SQL
    execution_result = Column(Text, nullable=True) # JSON string or summary
    rows_affected = Column(Integer, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
