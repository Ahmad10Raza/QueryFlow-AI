
import sys
import os
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.join(os.getcwd()))

from app.ai.graph import app as workflow_app
from app.models.user import User
from app.models.role import Role

def verify_pipeline():
    print("--- Starting Pipeline Verification ---")
    
    # Mock User
    user = User(id=1, email="test@example.com", is_superuser=True, role=Role(name="ADMIN"))
    
    # Test Case 3: Read Query on Connection 2 (Verify Ingestion Fix)
    question = "Show 5 rows from livonia_cdb"
    connection_id = 2
    
    inputs = {
        "question": question,
        "connection_id": connection_id,
        "user": user,
        "intent": "",
        "schema_context": "",
        "sql_query": "",
        "result": "",
        "error": None,
        # Phase 4 init
        "candidate_tables": [],
        "selected_tables": [],
        "confidence_score": 0.0,
        "is_ambiguous": False,
        "disambiguation_options": [],
        "grounded_schema": "",
        "access_status": "",
        "access_message": "",
        "retry_count": 0,
        "last_error": None
    }
    
    print(f"\n[Test 1] Question: '{question}'")
    try:
        final_state = workflow_app.invoke(inputs)
        
        print("\n--- Verification Results ---")
        print(f"Intent: {final_state.get('intent')}")
        print(f"Candidates: {final_state.get('candidate_tables')}")
        print(f"Selected: {final_state.get('selected_tables')}")
        print(f"Confidence: {final_state.get('confidence_score')}")
        print(f"Ambiguous: {final_state.get('is_ambiguous')}")
        print(f"Grounded Schema: {final_state.get('grounded_schema')}")
        print(f"Generated SQL: {final_state.get('sql_query')}")
        print(f"Access Status: {final_state.get('access_status')}")
        print(f"Validation Error: {final_state.get('validation_error')}")
        
    except Exception as e:
        print(f"Pipeline Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_pipeline()
