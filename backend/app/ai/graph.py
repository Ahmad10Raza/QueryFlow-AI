from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Optional, Dict, Any, List
import operator
from app.ai.nodes.intent import intent_classifier
from app.ai.nodes.intent import intent_classifier
from app.ai.nodes.impact import impact_analyzer
from app.ai.nodes.explainer import sql_explainer
from app.sql_guardrails.validator import validate_sql
# RBAC
from app.rbac.evaluator import evaluate_access, determine_required_permission
# Mock User context (In real app, pass user in state)
from app.models.user import User
from app.models.role import Role

class State(TypedDict):
    question: str
    connection_id: int
    user: Any # User object
    intent: str # READ, UPDATE_SINGLE, etc.
    schema_context: str
    sql_query: str
    validation_error: Optional[str]
    impact: Dict[str, Any]
    explanation: str
    access_status: str # APPROVED, REJECTED, NEEDS_APPROVAL
    access_message: str
    retry_count: int
    last_error: Optional[str]
    
    # Phase 4: Schema Safeguards
    candidate_tables: List[str] # From vector search
    selected_tables: List[str] # From LLM scoring
    confidence_score: float
    is_ambiguous: bool
    disambiguation_options: Optional[List[Dict[str, Any]]] # Options for user
    grounded_schema: str # JSON string of locked schema (tables + columns)

def rbac_node(state: State):
    user = state.get("user")
    intent = state.get("intent")
    
    # Fallback if no user passed (e.g. CLI test)
    if not user:
        # Create dummy admin for dev
        user = User(id=1, username="dev", role=Role(name="ADMIN"))

    required_perm = determine_required_permission(intent)
    result = evaluate_access(user, required_perm)
    
    status = result["status"]
    status_value = status.value if hasattr(status, 'value') else status
    
    return {
        "access_status": status_value,
        "access_message": result["message"]
    }

from app.ai.nodes.table_candidate_retriever import table_candidate_retriever
from app.ai.nodes.table_relevance_scorer import table_relevance_scorer
from app.ai.nodes.ambiguity_detector import ambiguity_detector
from app.ai.nodes.column_grounder import column_grounder
from app.ai.nodes.sql_repair_agent import sql_repair_agent

# ... existing RBAC node ...

def validate_node(state: State):
    sql = state["sql_query"]
    if not sql:
        return {"validation_error": "No SQL generated"}
        
    is_safe, message = validate_sql(sql)
    if not is_safe:
        return {"validation_error": f"Guardrail Alert: {message}"}
    return {}

workflow = StateGraph(State)

# Nodes
workflow.add_node("intent", intent_classifier)
workflow.add_node("rbac", rbac_node)
workflow.add_node("candidate_retriever", table_candidate_retriever)
workflow.add_node("relevance_scorer", table_relevance_scorer)
workflow.add_node("ambiguity_check", ambiguity_detector)
workflow.add_node("column_grounder", column_grounder)
workflow.add_node("generator", sql_repair_agent) # New Agent
workflow.add_node("validator", validate_node)
workflow.add_node("impact", impact_analyzer)
workflow.add_node("explainer", sql_explainer)

# Routers
def intent_router(state: State):
    if state["intent"] == "OTHER": return END
    return "rbac"

def rbac_router(state: State):
    if state["access_status"] == "REJECTED": return END
    return "candidate_retriever"

def ambiguity_router(state: State):
    if state.get("is_ambiguous"):
        # In a real app we would output the options to user.
        # For now, we set a flag that the API layer can detect and return to frontend.
        # We end the graph here, API sees "is_ambiguous" and handles it.
        return END
    return "column_grounder"

def generation_router(state: State):
    if state.get("validation_error"): return END
    
    intent = state.get("intent")
    if intent == "READ": return "explainer"
    else: return "impact"

# Edges
workflow.set_entry_point("intent")

workflow.add_conditional_edges("intent", intent_router)
workflow.add_conditional_edges("rbac", rbac_router, {
    "candidate_retriever": "candidate_retriever",
    END: END
})

workflow.add_edge("candidate_retriever", "relevance_scorer")
workflow.add_edge("relevance_scorer", "ambiguity_check")

workflow.add_conditional_edges("ambiguity_check", ambiguity_router, {
    "column_grounder": "column_grounder",
    END: END
})

workflow.add_edge("column_grounder", "generator")
workflow.add_edge("generator", "validator")

workflow.add_conditional_edges("validator", generation_router, {
    "explainer": "explainer",
    "impact": "impact",
    END: END
})

workflow.add_edge("impact", "explainer")
workflow.add_edge("explainer", END)

app = workflow.compile()
