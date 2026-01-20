from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.ai.utils.llm_factory import get_llm
import json

def sql_repair_agent(state: Dict[str, Any]):
    """
    Enhanced SQL Generator with Repair capabilities.
    Uses 'grounded_schema' to enforce strict column usage.
    """
    question = state["question"]
    grounded_schema = state.get("grounded_schema", "{}")
    user = state.get("user")
    llm = get_llm(user)
    last_error = state.get("last_error")
    
    # Check if grounded schema is valid
    try:
        schema_dict = json.loads(grounded_schema)
        # Convert back to readable string for prompt
        formatted_schema = json.dumps(schema_dict, indent=2)
    except:
        formatted_schema = grounded_schema

    instruction = "Generate a SQL query to answer the user's question."
    
    if last_error:
        instruction = f"""
        PREVIOUS ATTEMPT FAILED.
        Error Message: {last_error}
        
        CORRECT THE SQL QUERY based on the error.
        - If the error says "Table doesn't exist", check the schema and use the Correct table name.
        - If the error says "Column doesn't exist", use the correct column name.
        """

    prompt = f"""
    You are an expert SQL generator for PostgreSQL.
    
    STRICT CONSTRAINT: You must ONLY use the tables and columns defined in the Allowed Schema below.
    Do NOT assume other columns exist.
    
    Allowed Schema:
    {formatted_schema}
    
    {instruction}
    Question: "{question}"
    
    Rules:
    1. Generate ONLY the SQL query. No markdown, no explanation.
    2. Use only SELECT statements (unless intent is Update/Delete, but start with Select).
    3. Use table aliases for clarity (e.g. t1, t2).
    4. If the question cannot be answered with the Allowed Schema, return "ERROR: Insufficient schema context".
    """
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=question)
    ]
    
    response = llm.invoke(messages)
    sql_query = response.content.strip()
    
    # Simple markdown cleanup
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    
    # If returned error string
    if sql_query.startswith("ERROR:"):
        return {"sql_query": None, "validation_error": sql_query}
    
    return {"sql_query": sql_query}
