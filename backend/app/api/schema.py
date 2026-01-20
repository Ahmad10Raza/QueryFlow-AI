from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.db_connection import DBConnection
from app.models.schema import SchemaMetadata
from app.auth import dependencies
from app.models.user import User
from app.schema_ingestion.inspector import inspect_schema
# Trigger reload
from app.schema_ingestion.textifier import textify_schema
from app.rag.store import vector_store

router = APIRouter()

def process_schema_background(connection_id: int, db: Session):
    # Re-fetch connection
    conn = db.query(DBConnection).filter(DBConnection.id == connection_id).first()
    if not conn:
        return
    
    try:
        # 1. Introspect
        schema_info = inspect_schema(conn)
        
        # 2. Convert to text
        docs, _, _ = textify_schema(schema_info)
        schema_text = "\n\n".join(docs)
        
        # 3. Store in DB
        # Check if exists
        metadata = db.query(SchemaMetadata).filter(SchemaMetadata.db_connection_id == conn.id).first()
        if metadata:
            metadata.schema_json = schema_info
            metadata.description_text = schema_text
            metadata.version += 1
        else:
            metadata = SchemaMetadata(
                db_connection_id=conn.id,
                schema_json=schema_info,
                description_text=schema_text
            )
            db.add(metadata)
            
        db.commit()
        
        # 4. Embed to Chroma
        # We store each table description as a separate document
        documents = []
        metadatas = []
        ids = []
        
        for table, details in schema_info.items():
            # Generate text just for this table
            single_table_schema = {table: details}
            table_docs, _, _ = textify_schema(single_table_schema)
            
            if table_docs:
                desc = table_docs[0]
                
                documents.append(desc)
                metadatas.append({
                    "table_name": table,
                    "connection_id": conn.id,
                    "type": "table_schema"
                })
                ids.append(f"conn_{conn.id}_table_{table}")
            else:
                # Handle case where textify returns empty (unlikely but good for safety)
                pass
            
        vector_store.add_documents(
            collection_name=f"schema_conn_{conn.id}",
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully ingested schema for connection {conn.name}")
        
    except Exception as e:
        print(f"Error ingesting schema: {e}")
        # In real app, update a status field on DBConnection

@router.post("/{connection_id}/ingest")
def ingest_schema(
    connection_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user),
):
    conn = db.query(DBConnection).filter(DBConnection.id == connection_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    # Allow Owner OR Super Admin OR Admin
    if conn.owner_id != current_user.user_id and not current_user.is_superuser and current_user.role_name != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    background_tasks.add_task(process_schema_background, connection_id, db)
    
    return {"message": "Schema ingestion started in background"}
