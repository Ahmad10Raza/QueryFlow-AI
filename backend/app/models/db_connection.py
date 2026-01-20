from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class DBConnection(Base):
    __tablename__ = "db_connection" # Explicit table name
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    db_type = Column(String(50)) # postgres, mysql, etc
    host = Column(String(255))
    port = Column(Integer)
    username = Column(String(255))
    # Encrypted password placeholder - in real app use encryption
    # Encrypted password
    password_encrypted = Column(Text) 
    connection_mode = Column(String(50), default="guided") # guided, string
    is_active = Column(Boolean, default=True) 
    database_name = Column(String(255))
    
    owner_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    query_history = relationship("QueryHistory", back_populates="connection")
