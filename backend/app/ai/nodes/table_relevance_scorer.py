from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from app.ai.utils.llm_factory import get_llm
import json

def table_relevance_scorer(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 2: LLM-based ranking of candidates.
    Goal: Select ONLY the tables strictly required to answer the question.
    """
    question = state["question"]
    candidates = state.get("candidate_tables", [])
    user = state.get("user")
    
    if not candidates:
        print("DEBUG: No candidates to score.")
        return {"selected_tables": [], "confidence_score": 0.0}

    print(f"DEBUG: Stage 2 - Scoring {len(candidates)} candidates")
    
    llm = get_llm(user=user)
    
    # We ideally need table signatures/descriptions here.
    # For now we'll assume the names are descriptive enough, 
    # OR we could fetch descriptions from the vector retrieval docs if we passed them.
    # Let's rely on names for speed in this pass.
    
    system_prompt = """You are a senior database architect. 
    Your task is to identify which database tables are STRICTLY required to answer the user's question.
    
    Input:
    1. User Question
    2. List of Candidate Tables
    
    Instructions:
    - Select ONLY tables that contain data needed for the answer.
    - If multiple tables seem relevant (e.g. 'orders' and 'transactions'), pick the most specific one.
    - If you need to join tables, select all of them.
    - Return a JSON object with:
      - "selected_tables": List of table names
      - "reasoning": Brief explanation
      - "confidence_score": Float between 0.0 and 1.0 depending on how well the tables match the question.
    """
    
    human_prompt = f"""Question: {question}
    
    Candidate Tables:
    {json.dumps(candidates, indent=2)}
    
    Return JSON:"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", human_prompt),
    ])
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({})
        content = response.content
        print(f"DEBUG: Scorer Raw LLM Output: {content}")
        
        # Robust JSON extraction
        try:
            # Try to find JSON block
            import re
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
            else:
                # If no JSON found, try standard cleaning
                cleaned = content.replace("```json", "").replace("```", "").strip()
                result = json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"ERROR: Could not parse JSON from: {content}")
            raise
        
        selected = result.get("selected_tables", [])
        # Filter to ensure we only return tables that were in candidates (hallucination check)
        valid_selected = [t for t in selected if t in candidates]
        
        print(f"DEBUG: Selected {len(valid_selected)} tables: {valid_selected}")
        
        return {
            "selected_tables": valid_selected,
            "confidence_score": result.get("confidence_score", 0.5)
        }
        
    except Exception as e:
        print(f"ERROR: Relevance scoring failed: {e}")
        # Fallback: maybe select all candidates? Or top 3?
        return {"selected_tables": candidates[:3], "confidence_score": 0.3}
