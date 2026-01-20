import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.db_connection import DBConnection
from app.schema_ingestion.inspector import inspect_schema
from app.schema_ingestion.textifier import textify_schema
from app.rag.store import vector_store

def ingest(connection_id: int):
    db = SessionLocal()
    try:
        conn = db.query(DBConnection).filter(DBConnection.id == connection_id).first()
        if not conn:
            print(f"Connection {connection_id} not found")
            return
            
        print(f"Inspecting schema for {conn.name}...")
        schema_info = inspect_schema(conn)
        print(f"Found {len(schema_info)} tables.")
        
        print("Textifying schema...")
        docs, metadatas, ids = textify_schema(schema_info)
        
        collection_name = f"schema_conn_{connection_id}"
        
        # Delete existing collection to reset embeddings (e.g. 384 -> 768)
        try:
            vector_store.client.delete_collection(collection_name)
            print(f"Deleted existing collection {collection_name}")
        except:
            pass # Collection might not exist

        print(f"Storing {len(docs)} documents in vector store for connection {connection_id}...")
        vector_store.add_documents(
            collection_name=collection_name,
            documents=docs,
            metadatas=metadatas,
            ids=ids
        )
        print("Done!")
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    ingest(2)
