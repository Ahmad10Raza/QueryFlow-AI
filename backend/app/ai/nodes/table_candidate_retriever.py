from typing import Dict, Any, List
from langchain_community.vectorstores import Chroma
from app.core.config import settings
from app.ai.utils.llm_factory import get_embeddings
import json

def table_candidate_retriever(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 1: Fast initial retrieval using vector search.
    Goal: Narrow 100+ tables -> Top-K (e.g. 10) candidates.
    """
    question = state["question"]
    connection_id = state["connection_id"]
    
    print(f"DEBUG: Stage 1 - Retrieving candidates for connection {connection_id}")
    
    try:
        # Initialize Vector Store
        embeddings = get_embeddings()
        vector_store = Chroma(
            collection_name=f"schema_conn_{connection_id}",
            embedding_function=embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        )
        
        # Retrieve more candidates than usual (high recall)
        # We want to catch everything relevant, even if score is lower
        k = 12 
        docs = vector_store.similarity_search(question, k=k)
        
        # Extract table names
        candidate_tables = []
        seen = set()
        
        for doc in docs:
            # Metadata should have 'table_name'
            table_name = doc.metadata.get("table_name")
            if table_name and table_name not in seen:
                candidate_tables.append(table_name)
                seen.add(table_name)
        
        print(f"DEBUG: Found {len(candidate_tables)} candidates: {candidate_tables}")
        
        return {
            "candidate_tables": candidate_tables
        }
        
    except Exception as e:
        print(f"ERROR: Candidate retrieval failed: {e}")
        # Fallback: If DB has few tables, maybe return all? 
        # For now return empty, downstream might fail or fallback
        return {"candidate_tables": [], "error": str(e)}
