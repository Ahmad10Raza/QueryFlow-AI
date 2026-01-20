from sqlalchemy import Column, Integer, JSON, ForeignKey, DateTime, String, Text
from sqlalchemy.sql import func
from app.db.base_class import Base

class SchemaMetadata(Base):
    __tablename__ = "schema_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    db_connection_id = Column(Integer, ForeignKey("db_connection.id"))
    schema_json = Column(JSON) # Stores the full schema structure
    description_text = Column(Text) # For vector embeddings
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
