from typing import Dict, Any
from app.rag.store import vector_store

def schema_retriever(state: Dict[str, Any]):
    question = state["question"]
    conn_id = state.get("connection_id")
    
    if not conn_id:
        return {"error": "Connection ID missing"}
        
    # Retrieve relevant tables
    results = vector_store.query(
        collection_name=f"schema_conn_{conn_id}",
        query_text=question,
        n_results=5 # Retrieve top 5 most relevant context chunks
    )
    
    # Flatten results
    retrieved_schema = "\n\n".join(results["documents"][0])
    
    return {"schema_context": retrieved_schema}
