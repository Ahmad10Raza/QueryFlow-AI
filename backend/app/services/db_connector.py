
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Dict, Any, Tuple
import urllib.parse

class DBConnector:
    @staticmethod
    def build_uri(connection_details: Dict[str, Any], decrypted_password: str) -> str:
        """Constructs a database connection URI."""
        db_type = connection_details.get("db_type", "postgres")
        user = connection_details.get("username")
        password = urllib.parse.quote_plus(decrypted_password)
        host = connection_details.get("host")
        port = connection_details.get("port")
        db_name = connection_details.get("database_name")
        
        if db_type == "postgres":
            return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        elif db_type == "mysql":
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    def test_connection(connection_details: Dict[str, Any], password: str) -> Tuple[bool, str]:
        """Tries to connect to the database and runs a simple query."""
        try:
            uri = DBConnector.build_uri(connection_details, password)
            # Create a throwaway engine for testing
            engine = create_engine(uri, connect_args={"connect_timeout": 5})
            
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def create_engine_for_connection(db_connection_model, decrypted_password: str) -> Engine:
        """Creates a SQLAlchemy engine for a stored DBConnection."""
        details = {
            "db_type": db_connection_model.db_type,
            "username": db_connection_model.username,
            "host": db_connection_model.host,
            "port": db_connection_model.port,
            "database_name": db_connection_model.database_name
        }
        uri = DBConnector.build_uri(details, decrypted_password)
        return create_engine(uri)

db_connector = DBConnector()
