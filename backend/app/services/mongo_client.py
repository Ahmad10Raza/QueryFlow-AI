"""
MongoDB Client Wrapper for QueryFlow AI.
Provides connection testing and schema inspection for MongoDB databases.
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from typing import Dict, Any, Tuple, List, Optional
import urllib.parse


class MongoDBClient:
    @staticmethod
    def build_uri(connection_details: Dict[str, Any], decrypted_password: Optional[str]) -> str:
        """Constructs a MongoDB connection URI. Supports both standard and Atlas SRV connections."""
        user = connection_details.get("username")
        host = connection_details.get("host", "")
        port = connection_details.get("port", 27017)
        db_name = connection_details.get("database_name")
        
        # Detect MongoDB Atlas (SRV) connections
        # Atlas hostnames typically end in .mongodb.net
        is_atlas = ".mongodb.net" in host.lower()
        
        if is_atlas:
            # Use mongodb+srv:// for Atlas (no port needed)
            if user and decrypted_password:
                password = urllib.parse.quote_plus(decrypted_password)
                return f"mongodb+srv://{user}:{password}@{host}/{db_name}?retryWrites=true&w=majority"
            elif user:
                return f"mongodb+srv://{user}@{host}/{db_name}?retryWrites=true&w=majority"
            else:
                return f"mongodb+srv://{host}/{db_name}?retryWrites=true&w=majority"
        else:
            # Standard mongodb:// for self-hosted MongoDB
            if user and decrypted_password:
                password = urllib.parse.quote_plus(decrypted_password)
                return f"mongodb://{user}:{password}@{host}:{port}/{db_name}"
            elif user:
                return f"mongodb://{user}@{host}:{port}/{db_name}"
            else:
                return f"mongodb://{host}:{port}/{db_name}"

    @staticmethod
    def test_connection(connection_details: Dict[str, Any], password: Optional[str]) -> Tuple[bool, str]:
        """Tests connection to a MongoDB database."""
        try:
            uri = MongoDBClient.build_uri(connection_details, password)
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            # Force connection by running a command
            client.admin.command('ping')
            client.close()
            return True, "Connection successful"
        except ConnectionFailure as e:
            return False, f"Connection failed: {str(e)}"
        except OperationFailure as e:
            return False, f"Authentication failed: {str(e)}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_client(connection_details: Dict[str, Any], decrypted_password: Optional[str]) -> MongoClient:
        """Creates and returns a MongoDB client."""
        uri = MongoDBClient.build_uri(connection_details, decrypted_password)
        return MongoClient(uri)

    @staticmethod
    def list_collections(client: MongoClient, db_name: str) -> List[str]:
        """Lists all collections in the specified database."""
        db = client[db_name]
        return db.list_collection_names()

    @staticmethod
    def sample_documents(client: MongoClient, db_name: str, collection_name: str, limit: int = 10) -> List[Dict]:
        """Samples documents from a collection to infer schema."""
        db = client[db_name]
        collection = db[collection_name]
        return list(collection.find().limit(limit))

    @staticmethod
    def infer_schema_from_documents(documents: List[Dict]) -> List[Dict[str, Any]]:
        """Infers column schema from sampled documents."""
        if not documents:
            return []
        
        # Aggregate all keys across documents
        all_keys: Dict[str, set] = {}
        for doc in documents:
            for key, value in doc.items():
                if key not in all_keys:
                    all_keys[key] = set()
                all_keys[key].add(type(value).__name__)
        
        columns = []
        for key, types in all_keys.items():
            # Join multiple types if field has mixed types
            type_str = " | ".join(sorted(types))
            columns.append({
                "name": key,
                "type": type_str,
                "primary_key": key == "_id",
                "nullable": True  # MongoDB fields are inherently nullable
            })
        
        return columns


mongo_client = MongoDBClient()
