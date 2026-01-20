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
                        "message": "Query executed successfully."
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
