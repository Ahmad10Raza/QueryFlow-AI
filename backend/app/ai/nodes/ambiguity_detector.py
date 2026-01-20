from typing import Dict, Any
import json

def ambiguity_detector(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 3: Ambiguity Check.
    Goal: Detect if we are unsure about the table selection.
    """
    selected = state.get("selected_tables", [])
    confidence = state.get("confidence_score", 0.0)
    
    print(f"DEBUG: Stage 3 - Checking ambiguity. Confidence: {confidence}, Selected: {len(selected)}")
    
    # Heuristic 1: Low confidence
    # Lowered to 0.3 to be less annoying. 
    # If we have a selection (1-5 tables), we should try to answer instead of blocking.
    if confidence < 0.3 and not selected:
        return {
            "is_ambiguous": True,
            "disambiguation_options": [
                {"message": "I'm not sure which tables to use. Could you be more specific?"}
            ]
        }
    
    # Heuristic 1.5: If we selected tables but confidence is marginally low (0.2-0.3), let it slide.
    # Only block if it's really bad (< 0.2) AND we have no clear winner.
    if confidence < 0.2:
         return {
            "is_ambiguous": True,
            "disambiguation_options": [
                {"message": "I found some potential tables, but I'm not confident enough. Can you provide more details?"}
            ]
        }
    
    # Heuristic 2: No tables selected
    if not selected:
        return {
            "is_ambiguous": True, 
            "disambiguation_options": [
                {"message": "I couldn't find any relevant tables for your question."}
            ]
        }
        
    return {"is_ambiguous": False}
