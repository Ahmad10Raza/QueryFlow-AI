from langchain_core.prompts import ChatPromptTemplate
from app.ai.utils.llm_factory import get_llm

def repair_sql_query(state: dict) -> dict:
    """
    Repairs a failed SQL query using an LLM.
    
    Expected state keys:
    - sql_query: The failed SQL
    - error: The error message
    - connection_id: (Optional) to get dialect context if needed
    
    Returns:
    - cleaned_sql: The fixed SQL
    """
    failed_sql = state.get("sql_query")
    error_msg = state.get("error")
    user = state.get("user")
    
    llm = get_llm(user=user)
    
    system_prompt = """You are an expert SQL Database Administrator.
    Your task is to fix a SQL query that failed to execute on a MySQL 8.x database.
    
    RULES:
    1. Fix ONLY the syntax error described.
    2. Maintain the original logic.
    3. Use MySQL compatible syntax (backticks ` for identifiers, single quotes ' for strings).
    4. Do NOT output markdown or explanations. Output ONLY the raw SQL.
    """
    
    human_prompt = f"""
    Failed SQL: 
    {failed_sql}
    
    Error Message:
    {error_msg}
    
    Corrected SQL:
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({})
        # Clean up code blocks if LLM adds them despite instructions
        cleaned_sql = response.content.replace("```sql", "").replace("```", "").strip()
        return {"sql_query": cleaned_sql}
    except Exception as e:
        # If repair fails, return original and let execution fail again or handle upstream
        print(f"Repair loop failed: {e}")
        return {"sql_query": failed_sql}
