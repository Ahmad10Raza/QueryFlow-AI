from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.ai.utils.llm_factory import get_llm
import json

def query_insights_generator(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes the executed query and results to provide business insights.
    State requirements:
    - question: str
    - sql_query: str
    - result_metadata: dict (rows_count, columns etc, NOT full data)
    """
    print("DEBUG: Generating Query Insights...")
    
    question = state.get("question", "")
    sql = state.get("sql_query", "")
    metadata = state.get("result_metadata", {})
    user = state.get("user")
    
    if not sql:
        return {"insights": None}

    llm = get_llm(user=user)
    
    # We must properly escape curly braces {{ }} for LangChain prompt templates
    system_prompt = """You are a Senior Data Intelligence Strategist. Your goal is to translate SQL results into high-value business insights for stakeholders.
    
    Provide a robust analysis. Even if the query is simple, explain *what* is being retrieved and *why* it might be useful generally.
    
    CRITICAL INSTRUCTION: Output ONLY the raw JSON object. Do not wrap it in markdown code blocks. Do not ignore this. Do not say "Here is the JSON". Just start with {{ and end with }}.
    
    Output strictly in JSON format with the following keys:
    - "impact": (String) "High Risk", "Medium Risk", "Low Risk", "Informational".
    - "data_scope": (String) Detailed summary of tables, row weight, and data freshness if detectable.
    - "business_meaning": (String) A multi-sentence explanation. What does this data tell the user? If specific business meaning is unclear, explain the *general utility* of this type of data (e.g., "Retrieving item numbers allows for inventory tracking and cross-referencing orders.").
    - "performance_note": (String) Technical efficiency feedback.
    - "risk_assessment": (String) Security, privacy (PII), or data integrity concerns.
    
    CRITICAL: "business_meaning" MUST be populated. Do not say "Could not generate insights". Make a reasonable inference about the data's utility.
    """
    
    # Using f-strings to inject variable values into the message string itself.
    # When passed to ChatPromptTemplate.from_messages, the braces in the JSON dump must remain as braces.
    # BUT wait, simpler approach:
    # Pass the variables via .invoke(input) instead of f-string injection if possible.
    # However, to be safe and consistent with current pattern, we will construct the message string here.
    # If using f-strings, we inject the values directly.
    # But if the string contains { } that assume variables for ChatPromptTemplate, we fail.
    # Since we are constructing the *message content* as a fully formed string,
    # we should check if ChatPromptTemplate tries to re-format it.
    # Yes, .from_messages does.
    # So we need to escape { and } in the *content* of the message if we don't want them treated as variables.
    
    # A cleaner way: Use simpler PromptTemplate or just pass messages directly to LLM if we don't need further templating within LangChain.
    # But sticking to structure:
    
    # Let's escape the JSON in the f-string result before creating the prompt template?
    # No, it's easier to just pass input variables to invoke.
    
    human_prompt = """
    Context:
    User Question: "{question}"
    Executed SQL: {sql}
    Result Metadata: {metadata_json}
    
    Generate the insights JSON. Even if metadata is empty, explain the INTENT of the query in 'business_meaning'.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    
    import re
    
    try:
        # Pass variables to invoke so LangChain handles insertion and escaping issues properly
        response = chain.invoke({
            "question": question,
            "sql": sql,
            "metadata_json": json.dumps(metadata)
        })
        content = response.content
        print(f"DEBUG: Insights Raw LLM Content: {content}")
        
        # Robust JSON extraction
        # Find the first { and last }
        json_match = re.search(r'(\{.*\})', content, re.DOTALL)
        if json_match:
            clean_content = json_match.group(1)
            parsed = json.loads(clean_content)
            return {"insights": parsed}
        else:
            # Try to parse the whole thing if no braces found (unlikely for JSON, but fallback)
            # Or just fail
            print("ERROR: No JSON object found in response")
            raise ValueError("No JSON block found")

    except Exception as e:
        print(f"ERROR: Insights generation failed: {e}")
        # Return fallback
        return {
            "insights": {
                "impact": "Informational",
                "data_scope": "Unknown",
                "business_meaning": "Could not generate insights.",
                "performance_note": "",
                "risk_assessment": "Unknown"
            }
        }
