from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.ai.utils.llm_factory import get_llm

def sql_generator(state: Dict[str, Any]):
    question = state["question"]
    schema_context = state["schema_context"]
    user = state.get("user")
    llm = get_llm(user)
    last_error = state.get("last_error")
    
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
    Given the following database schema context:
    {schema_context}
    
    {instruction}
    Question: "{question}"
    
    Rules:
    1. Generate ONLY the SQL query. No markdown, no explanation.
    2. Use only SELECT statements.
    3. Use the table and column names EXACTLY as provided in the schema context above.
    4. DO NOT assume the existence of any tables (like 'users', 'products', 'orders') unless they are explicitly listed in the schema context.
    5. If the question cannot be answered with the given schema, return "ERROR: Insufficient schema context".
    6. Do NOT add a LIMIT clause unless the user explicitly asks for it or it is necessary for syntax correctness.
    """
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=question)
    ]
    
    response = llm.invoke(messages)
    sql_query = response.content.strip()
    
    # Simple markdown cleanup if LLM still adds it
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    
    return {"sql_query": sql_query}
