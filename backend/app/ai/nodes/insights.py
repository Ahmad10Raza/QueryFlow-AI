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
    - result_metadata: dict (rows_count, columns etc)
    - sample_data: list (first few rows of actual data)
    """
    print("DEBUG: Generating Query Insights...")
    
    question = state.get("question", "")
    sql = state.get("sql_query", "")
    metadata = state.get("result_metadata", {})
    sample_data = state.get("sample_data", [])
    user = state.get("user")
    
    if not sql:
        return {"insights": None}

    llm = get_llm(user=user)
    
    system_prompt = """You are a Senior Data Intelligence Strategist analyzing ACTUAL query results to provide actionable business insights.

Your task is to analyze the SAMPLE DATA provided and give meaningful, data-driven insights - not generic descriptions of what the query does.

CRITICAL INSTRUCTIONS:
1. ANALYZE THE ACTUAL DATA VALUES in the sample - look for patterns, distributions, notable values
2. Provide specific observations like "3 out of 5 projects are marked as 'In Progress'" or "The titles suggest a focus on web development technologies"
3. DO NOT just describe what the SQL query does - describe what the DATA SHOWS
4. Output ONLY the raw JSON object - no markdown, no explanations

Output strictly in JSON format with these keys:
- "impact": (String) "High Risk", "Medium Risk", "Low Risk", "Informational" - based on data sensitivity
- "data_scope": (String) Summary of what data was retrieved - mention specific patterns you see in the sample
- "business_meaning": (String) ANALYZE THE ACTUAL DATA. What patterns do you see? What insights can be drawn from the sample values? Be specific about what the data contains.
- "performance_note": (String) Query efficiency feedback
- "risk_assessment": (String) Any PII, security, or data concerns based on the actual data values

REMEMBER: Your "business_meaning" must reference specific observations from the sample data, not generic statements about the query type.
"""
    
    human_prompt = """
Context:
User Question: "{question}"
Executed Query: {sql}
Result Metadata: {metadata_json}

ACTUAL DATA SAMPLE (analyze this!):
{sample_data_json}

Based on the ACTUAL DATA SAMPLE above, generate insights that analyze what the data shows, not just what the query does.
If the sample shows project titles, comment on the types of projects. If it shows user data, identify patterns. Be specific and data-driven.
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    
    import re
    
    try:
        # Format sample data nicely for the LLM
        sample_str = json.dumps(sample_data, indent=2, default=str) if sample_data else "No data returned"
        
        response = chain.invoke({
            "question": question,
            "sql": sql,
            "metadata_json": json.dumps(metadata),
            "sample_data_json": sample_str
        })
        content = response.content
        print(f"DEBUG: Insights Raw LLM Content: {content}")
        
        # Robust JSON extraction
        json_match = re.search(r'(\{.*\})', content, re.DOTALL)
        if json_match:
            clean_content = json_match.group(1)
            parsed = json.loads(clean_content)
            return {"insights": parsed}
        else:
            print("ERROR: No JSON object found in response")
            raise ValueError("No JSON block found")

    except Exception as e:
        print(f"ERROR: Insights generation failed: {e}")
        # Return fallback
        return {
            "insights": {
                "impact": "Informational",
                "data_scope": f"Query returned {metadata.get('rows_returned', 0)} rows",
                "business_meaning": "Insights generation encountered an issue. Please review the data manually.",
                "performance_note": "",
                "risk_assessment": "N/A"
            }
        }

