from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.ai.utils.llm_factory import get_llm

def intent_classifier(state: Dict[str, Any]):
    question = state["question"]
    user = state.get("user")
    llm = get_llm(user)
    
    prompt = """
    You are a database AI assistant. Analyze the user's question to determine the SQL operation type.
    
    Classify into one of the following categories:
    - READ: Retrieving data (SELECT, SHOW, DESCRIBE). Also includes general questions like "is there any data", "do we have info about", "list tables", etc.
    - UPDATE_SINGLE: Modifying existing data for a specific single record (e.g. "update user 123", "change password for email x"). Usually has a specific ID or unique identifier.
    - UPDATE_MULTI: Modifying multiple records or general updates (e.g. "give everyone a raise", "update all users"). Riskier.
    - DELETE: Removing data (DELETE, DROP, TRUNCATE).
    - OTHER: Unrelated to databases or chit-chat (e.g. "hello", "how are you").
    
    IMPORTANT: If the user asks about data existence (e.g. "is there data about X"), classify as READ.
    
    Return ONLY the classification word.
    """
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=question)
    ]
    
    response = llm.invoke(messages)
    classification = response.content.strip().upper()
    
    # Fallback / Normalization
    valid_intents = ["READ", "UPDATE_SINGLE", "UPDATE_MULTI", "DELETE", "OTHER"]
    
    # Simple keyword check fallback if LLM is verbose
    if classification not in valid_intents:
        if "DELETE" in classification or "DROP" in classification: classification = "DELETE"
        elif "UPDATE" in classification and "ALL" in classification.upper(): classification = "UPDATE_MULTI"
        elif "UPDATE" in classification: classification = "UPDATE_SINGLE"
        elif "SELECT" in classification or "SHOW" in classification: classification = "READ"
        else: classification = "READ" # Default safe fallback
    
    return {"intent": classification}
