from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=True)
    
    # LLM Configuration
    llm_provider = Column(String(50), nullable=True) # e.g. 'openai', 'gemini'
    llm_model = Column(String(100), nullable=True) # e.g. 'gpt-4o'
    llm_api_key_encrypted = Column(String(1000), nullable=True)

    role = relationship("Role")
