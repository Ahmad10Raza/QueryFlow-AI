from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.ai.utils.llm_factory import get_llm

def sql_explainer(state: Dict[str, Any]):
    """
    Generates a natural language explanation of what the SQL query does.
    """
    sql_query = state.get("sql_query")
    question = state.get("question")
    
    if not sql_query:
        return {"explanation": "No query generated."}
        
    user = state.get("user")
    llm = get_llm(user)
    
    prompt = """
    You are a database expert. Explain the following SQL query to a non-technical user.
    - Be concise (1-2 sentences).
    - Mention which table is being modified and what the criteria is.
    - If it is a read query, explain what data is being fetched.
    - Do NOT mention ID columns or technical jargon if possible.
    
    User Question: {question}
    SQL Query: {sql_query}
    """
    
    messages = [
        SystemMessage(content=prompt.format(question=question, sql_query=sql_query))
    ]
    
    response = llm.invoke(messages)
    explanation = response.content.strip()
    
    return {"explanation": explanation}
