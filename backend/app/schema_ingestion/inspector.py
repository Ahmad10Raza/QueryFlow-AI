from sqlalchemy import create_engine, inspect
from app.models.db_connection import DBConnection
from app.services.credential_encryptor import encryptor
from app.services.db_connector import db_connector

def inspect_schema(db_connection: DBConnection):
    """
    Connects to the target database and extracts schema information.
    Uses information_schema for PostgreSQL to avoid permission issues with system catalogs.
    """
    # Decrypt password
    decrypted_password = encryptor.decrypt(db_connection.password_encrypted)
    
    schema_info = {}
    
    # Handle MongoDB separately (no SQLAlchemy engine needed)
    if db_connection.db_type == 'mongodb':
        from app.services.mongo_client import mongo_client
        
        client = mongo_client.get_client(
            {
                "username": db_connection.username,
                "host": db_connection.host,
                "port": db_connection.port,
                "database_name": db_connection.database_name
            },
            decrypted_password
        )
        
        try:
            collections = mongo_client.list_collections(client, db_connection.database_name)
            
            for collection_name in collections:
                try:
                    print(f"DEBUG: Inspecting MongoDB collection {collection_name}")
                    documents = mongo_client.sample_documents(
                        client, db_connection.database_name, collection_name, limit=20
                    )
                    columns = mongo_client.infer_schema_from_documents(documents)
                    
                    schema_info[collection_name] = {
                        "columns": columns,
                        "foreign_keys": []  # MongoDB doesn't have formal FK constraints
                    }
                except Exception as e:
                    print(f"Warning: Could not inspect collection {collection_name}: {e}")
                    schema_info[collection_name] = {
                        "columns": [],
                        "foreign_keys": []
                    }
        finally:
            client.close()
        
        return schema_info
    
    # Create SQLAlchemy engine for SQL databases only
    engine = db_connector.create_engine_for_connection(db_connection, decrypted_password)
    
    if db_connection.db_type in ('postgresql', 'postgres'):
        # Use information_schema for PostgreSQL (works with read-only users)
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Get all tables from non-system schemas
            tables_query = text("""
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                  AND table_type = 'BASE TABLE'
                ORDER BY table_schema, table_name
            """)
            
            tables_result = conn.execute(tables_query)
            
            for row in tables_result:
                schema_name = row[0]
                table_name = row[1]
                full_table_name = f"{schema_name}.{table_name}"
                
                try:
                    # Get columns for this table
                    columns_query = text("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_schema = :schema AND table_name = :table
                        ORDER BY ordinal_position
                    """)
                    
                    print(f"DEBUG: Inspecting table {full_table_name}")
                    columns_result = conn.execute(columns_query, {"schema": schema_name, "table": table_name})
                    
                    columns = []
                    for col_row in columns_result:
                        columns.append({
                            "name": col_row[0],
                            "type": col_row[1],
                            "primary_key": False,  # We'll skip PK detection to avoid permission issues
                            "nullable": col_row[2] == 'YES'
                        })
                    
                    schema_info[full_table_name] = {
                        "columns": columns,
                        "foreign_keys": []  # Skip FK detection to avoid permission issues
                    }
                    
                except Exception as e:
                    print(f"Warning: Could not inspect table {full_table_name}: {e}")
                    # Still add the table with minimal info so it's searchable
                    schema_info[full_table_name] = {
                        "columns": [],
                        "foreign_keys": []
                    }
    else:
        # Use SQLAlchemy inspector for MySQL (works fine)
        inspector = inspect(engine)
        
        for table_name in inspector.get_table_names():
            try:
                columns = []
                for col in inspector.get_columns(table_name):
                    columns.append({
                        "name": col["name"],
                        "type": str(col["type"]),
                        "primary_key": col.get("primary_key", False),
                        "nullable": col.get("nullable", True)
                    })
                    
                # Get Foreign Keys
                fks = []
                try:
                    for fk in inspector.get_foreign_keys(table_name):
                        fks.append({
                            "constrained_columns": fk["constrained_columns"],
                            "referred_table": fk["referred_table"],
                            "referred_columns": fk["referred_columns"]
                        })
                except Exception as fk_error:
                    print(f"Warning: Could not inspect foreign keys for {table_name}: {fk_error}")
                    fks = []
                    
                schema_info[table_name] = {
                    "columns": columns,
                    "foreign_keys": fks
                }
            except Exception as e:
                print(f"Warning: Could not inspect table {table_name}: {e}")
                schema_info[table_name] = {
                    "columns": [],
                    "foreign_keys": []
                }
        
    return schema_info
