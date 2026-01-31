from sqlalchemy import text
from app.models.db_connection import DBConnection
from app.services.db_connector import db_connector
from app.services.credential_encryptor import encryptor
from typing import List, Dict, Any

def execute_sql_query(db_connection: DBConnection, sql: str, require_commit: bool = False) -> Dict[str, Any]:
    """
    Executes the validated SQL query on the target database.
    """
    # Decrypt password and create engine using the service
    decrypted_password = encryptor.decrypt(db_connection.password_encrypted)
    engine = db_connector.create_engine_for_connection(db_connection, decrypted_password)
    
    try:
        with engine.connect() as conn:
            # Begin transaction if writing
            if require_commit:
                trans = conn.begin()
                try:
                    result = conn.execute(text(sql))
                    # Check row count limits here if desired
                    trans.commit()
                    return {
                        "status": "success",
                        "rows_affected": result.rowcount,
                        "message": "Query executed successfully.",
                        "columns": [],
                        "rows": []
                    }
                except Exception as e:
                    trans.rollback()
                    raise e
            else:
                # Read-only execution
                result = conn.execute(text(sql))
                columns = result.keys()
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                
                return {
                    "columns": list(columns),
                    "rows": rows
                }
    except Exception as e:
        # Re-raise or return error dict depending on caller's expectation
        # The caller (api/query.py) expects raised exceptions to handle them in try/except block
        raise e
    finally:
        engine.dispose()


def execute_mongo_query(db_connection: DBConnection, query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a MongoDB query on the target database.
    
    Expected query format:
    {
        "collection": "collection_name",
        "operation": "find" | "aggregate",
        "filter": {...},  # For find operations
        "pipeline": [...]  # For aggregate operations
        "limit": 100  # Optional
    }
    """
    from app.services.mongo_client import mongo_client
    from bson import ObjectId
    from datetime import datetime
    
    def serialize_mongo_doc(doc):
        """Recursively converts BSON types to JSON-serializable types."""
        if isinstance(doc, dict):
            return {key: serialize_mongo_doc(value) for key, value in doc.items()}
        elif isinstance(doc, list):
            return [serialize_mongo_doc(item) for item in doc]
        elif isinstance(doc, ObjectId):
            return str(doc)
        elif isinstance(doc, datetime):
            return doc.isoformat()
        elif isinstance(doc, bytes):
            return doc.decode('utf-8', errors='replace')
        else:
            return doc
    
    decrypted_password = encryptor.decrypt(db_connection.password_encrypted)
    
    connection_details = {
        "username": db_connection.username,
        "host": db_connection.host,
        "port": db_connection.port,
        "database_name": db_connection.database_name
    }
    
    client = mongo_client.get_client(connection_details, decrypted_password)
    
    try:
        db = client[db_connection.database_name]
        collection_name = query.get("collection")
        operation = query.get("operation", "find")
        limit = query.get("limit", 100)
        
        if not collection_name:
            raise ValueError("Missing 'collection' in query")
        
        collection = db[collection_name]
        
        if operation == "find":
            filter_dict = query.get("filter", {})
            cursor = collection.find(filter_dict).limit(limit)
            rows = []
            for doc in cursor:
                # Convert all BSON types to JSON-serializable
                rows.append(serialize_mongo_doc(doc))
            
            # Infer columns from results
            if rows:
                columns = list(rows[0].keys())
            else:
                columns = []
            
            return {
                "columns": columns,
                "rows": rows
            }
        
        elif operation == "aggregate":
            pipeline = query.get("pipeline", [])
            cursor = collection.aggregate(pipeline)
            rows = []
            for doc in cursor:
                # Convert all BSON types to JSON-serializable
                rows.append(serialize_mongo_doc(doc))
            
            if rows:
                columns = list(rows[0].keys())
            else:
                columns = []
            
            return {
                "columns": columns,
                "rows": rows
            }

        elif operation == "delete":
            filter_dict = query.get("filter", {})
            result = collection.delete_many(filter_dict)
            return {
                "status": "success",
                "rows_affected": result.deleted_count,
                "message": f"Deleted {result.deleted_count} documents.",
                "columns": [],
                "rows": []
            }
        
        else:
            raise ValueError(f"Unsupported MongoDB operation: {operation}")
    
    finally:
        client.close()

