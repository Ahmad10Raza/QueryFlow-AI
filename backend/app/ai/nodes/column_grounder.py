from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from app.ai.utils.llm_factory import get_llm, get_embeddings
from app.core.config import settings
import json

def column_grounder(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 4: Column Grounding.
    Goal: Select specific columns from the selected tables to prevent hallucination.
    Input: Question + Selected Tables
    Output: Grounded Schema (JSON string of tables + specific columns)
    """
    question = state["question"]
    selected_tables = state.get("selected_tables", [])
    connection_id = state["connection_id"]
    user = state.get("user")

    if not selected_tables:
        print("DEBUG: No selected tables for grounding.")
        return {"grounded_schema": "[]"}
    
    print(f"DEBUG: Stage 4 - Grounding columns for tables: {selected_tables}")
    
    # We need to fetch the FULL schema for these specific tables to let LLM pick columns.
    # We can use the textifier or just fetch from vector store metadata if available.
    # For now, let's fetch from vector store logic again or use a helper.
    # A robust way: Retrieve the documents for these tables from Chroma.
    
    embeddings = get_embeddings()
    vector_store = Chroma(
        collection_name=f"schema_conn_{connection_id}",
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIRECTORY
    )
    
    # We can't easily query by metadata in standard LC retrieval without iterating or using specific filter.
    # Let's filter by table_name metadata.
    
    full_schemas = []
    
    # This might be slow if we do N queries. 
    # Optimization: One query with "OR" filter if supported, or just loop for now (N is small, < 5).
    try:
        for table in selected_tables:
            # We want to get the doc that has this table name. 
            # Chroma get() allows filtering.
            results = vector_store.get(where={"table_name": table})
            if results and results['documents']:
                # Assume one doc per table as per our textifier strategy
                full_schemas.append(results['documents'][0])
            else:
                print(f"WARN: Could not find schema for table {table}")
                
        schema_context = "\n\n".join(full_schemas)
        
    except Exception as e:
        print(f"ERROR: Failed to fetch schema for grounding: {e}")
        return {"grounded_schema": "[]"}
    
    llm = get_llm(user=user)
    
    system_prompt = """You are a strict data engineer.
    Your task is to identify specific columns from the provided schema that are required to answer the user's question.
    
    Input:
    1. User Question
    2. Full Schema of Selected Tables
    
    Instructions:
    - Select ONLY columns strictly needed (SELECT clause, WHERE clause, JOIN keys).
    - Do NOT include columns that are not mentioned or implied.
    - Return a JSON object mapping table names to list of column names.
    - Format: {{"table_name": ["col1", "col2"]}}
    """
    
    human_prompt = f"""Question: {question}
    
    Schema:
    {schema_context}
    
    Return JSON:"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", human_prompt),
    ])
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({})
        content = response.content
        print(f"DEBUG: Column Grounder Raw Response: {content}")
        
        # Robust cleanup
        clean_content = content.replace("```json", "").replace("```", "").strip()
        # Sometimes key is single quoted
        if clean_content.startswith("'") and clean_content.endswith("'"):
             clean_content = clean_content[1:-1]
             
        # Extract JSON substring if needed
        import re
        json_match = re.search(r'\{.*\}', clean_content, re.DOTALL)
        if json_match:
            clean_content = json_match.group(0)
            
        # Verify JSON
        grounded = json.loads(clean_content)
        
        # Security: Allow all selected tables, but trust LLM's column choices for now.
        # Strict implementation checks if columns actually exist in source schema.
        
        return {
            "grounded_schema": json.dumps(grounded)
        }
        
    except Exception as e:
        print(f"ERROR: Column grounding failed: {e}")
        # On error print content to help debug
        try: print(f"Failed Content: {response.content}") 
        except: pass
        # Fallback: Return empty or full schema? 
        # For safety, let's return full schema context we fetched, formatted as JSON logic if possible, 
        # or simplified.
        return {"grounded_schema": "ERROR"}
