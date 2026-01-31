from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.db_connection import DBConnection
from app.auth import dependencies
from app.models.user import User
from app.ai.graph import app as workflow_app
from app.query_executor.executor import execute_sql_query, execute_mongo_query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import re

router = APIRouter()


def execute_query_for_connection(conn: DBConnection, sql_or_query: str) -> Dict[str, Any]:
    """
    Routes query execution to the appropriate executor based on database type.
    For MongoDB, converts simple SQL patterns to MongoDB queries.
    """
    if conn.db_type == "mongodb":
        # Parse SQL-like query to MongoDB format
        mongo_query = sql_to_mongo_query(sql_or_query)
        return execute_mongo_query(conn, mongo_query)
    else:
        return execute_sql_query(conn, sql_or_query)


from bson import ObjectId

def sql_to_mongo_query(sql: str) -> Dict[str, Any]:
    """
    Converts simple SQL-like queries to MongoDB query format.
    Supports basic SELECT, DELETE, WHERE clauses.
    """
    sql = sql.strip().rstrip(';')
    
    # Pattern: SELECT * FROM collection_name [WHERE conditions] [LIMIT n]
    select_pattern = r"SELECT\s+(.+?)\s+FROM\s+[`'\"]?(\w+)[`'\"]?(?:\s+WHERE\s+(.+?))?(?:\s+LIMIT\s+(\d+))?$"
    match = re.match(select_pattern, sql, re.IGNORECASE)
    
    if match:
        fields = match.group(1).strip()
        collection = match.group(2)
        where_clause = match.group(3)
        limit = int(match.group(4)) if match.group(4) else 100
        
        # Build MongoDB query
        mongo_filter = {}
        if where_clause:
            mongo_filter = parse_where_to_mongo(where_clause)
        
        return {
            "collection": collection,
            "operation": "find",
            "filter": mongo_filter,
            "limit": limit
        }

    # Pattern: DELETE FROM collection_name [WHERE conditions]
    delete_pattern = r"DELETE\s+FROM\s+[`'\"]?(\w+)[`'\"]?(?:\s+WHERE\s+(.+?))?$"
    match_delete = re.match(delete_pattern, sql, re.IGNORECASE)
    
    if match_delete:
        collection = match_delete.group(1)
        where_clause = match_delete.group(2)
        
        mongo_filter = {}
        if where_clause:
            mongo_filter = parse_where_to_mongo(where_clause)
            
        return {
            "collection": collection,
            "operation": "delete",
            "filter": mongo_filter
        }
    
    # Fallback: treat as collection name with find all
    return {
        "collection": sql.replace("SELECT * FROM ", "").strip().strip('`"\''),
        "operation": "find",
        "filter": {},
        "limit": 100
    }


def parse_where_to_mongo(where_clause: str) -> Dict[str, Any]:
    """
    Parses simple WHERE clauses to MongoDB filter format.
    Supports: field = value, field > value, field < value, AND
    Handles _id ObjectId conversion.
    """
    mongo_filter = {}
    
    # Split by AND
    conditions = re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE)
    
    for condition in conditions:
        condition = condition.strip()
        
        # Match: field = 'value' or field = value
        eq_match = re.match(r"[`'\"]?(\w+)[`'\"]?\s*=\s*['\"]?([^'\"]+)['\"]?", condition)
        if eq_match:
            field, value = eq_match.groups()
            
            # Special handling for _id
            if field == "_id" and ObjectId.is_valid(value):
                mongo_filter[field] = ObjectId(value)
                continue

            # Try to convert to number if possible
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass  # Keep as string
            mongo_filter[field] = value
            continue
        
        # Match: field > value
        gt_match = re.match(r"[`'\"]?(\w+)[`'\"]?\s*>\s*['\"]?([^'\"]+)['\"]?", condition)
        if gt_match:
            field, value = gt_match.groups()
            try:
                value = float(value)
            except ValueError:
                pass
            mongo_filter[field] = {"$gt": value}
            continue
        
        # Match: field < value
        lt_match = re.match(r"[`'\"]?(\w+)[`'\"]?\s*<\s*['\"]?([^'\"]+)['\"]?", condition)
        if lt_match:
            field, value = lt_match.groups()
            try:
                value = float(value)
            except ValueError:
                pass
            mongo_filter[field] = {"$lt": value}
            continue
    
    return mongo_filter


class NLQueryRequest(BaseModel):
    connection_id: int
    question: str

class NLQueryResponse(BaseModel):
    intent: str
    sql_query: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    approval_id: Optional[int] = None
    access_status: Optional[str] = None
    # Phase 4
    is_ambiguous: bool = False
    disambiguation_options: Optional[List[Dict[str, str]]] = None
    # Phase 5
    query_id: Optional[int] = None
    insights: Optional[Dict[str, Any]] = None

@router.post("/nl", response_model=NLQueryResponse)
async def run_natural_language_query(
    request: NLQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user),
):
    conn = db.query(DBConnection).filter(DBConnection.id == request.connection_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    if conn.owner_id != current_user.user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Run AI Pipeline
    inputs = {
        "question": request.question,
        "connection_id": conn.id,
        "intent": "",
        "schema_context": "",
        "sql_query": "",
        "result": "",
        "error": None,
        "user": current_user # Pass user to state
    }
    
    print(f"DEBUG: Running AI Pipeline for user={current_user.email} with inputs={inputs}")
    MAX_RETRIES = 2
    retry_count = 0
    final_response = None
    
    # Import Robustness Nodes
    from app.ai.nodes.sql_validator import validate_and_normalize_sql
    from app.ai.nodes.sql_repair import repair_sql_query
    
    while retry_count <= MAX_RETRIES:
        if retry_count > 0:
            print(f"DEBUG: Retry attempt {retry_count} for user={current_user.email}")
            inputs["retry_count"] = retry_count
            
        try:
            # workflow_app.invoke(inputs) returns the final state
            final_state = workflow_app.invoke(inputs)
            print(f"DEBUG: AI Pipeline Result (Attempt {retry_count}): {final_state}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return NLQueryResponse(intent="ERROR", sql_query=None, result=None, error=f"AI Pipeline Error: {str(e)}")
            
        if final_state.get("error"):
             print(f"DEBUG: Pipeline returned error: {final_state['error']}")
             return NLQueryResponse(
                 intent=final_state.get("intent", "UNKNOWN"),
                 sql_query=final_state.get("sql_query"),
                 result=None,
                 error=final_state["error"]
             )

        # Check for Ambiguity (Phase 4)
        if final_state.get("is_ambiguous"):
             return NLQueryResponse(
                 intent=final_state.get("intent", "READ"),
                 sql_query=None,
                 result=None,
                 error=None,
                 is_ambiguous=True,
                 disambiguation_options=final_state.get("disambiguation_options", [])
             )
        
        # Check if approval is required
        access_status = final_state.get("access_status")
        
        if access_status == "NEEDS_APPROVAL":
            # ... existing approval logic (abbreviated for clarity, but preserved in actual replace) ...
            # To avoid huge diff, we will trust the existing logic is here or we re-insert it if needed. 
            # Actually, replace_file_content replaces the whole block. I need to be careful.
            # Re-inserting Approval Logic:
            # Use QueryRequest for AI-triggered approvals
            from app.models.query_request import QueryRequest
            
            # Determine intent if not set
            intent = final_state.get("intent", "READ").upper()
            
            query_request = QueryRequest(
                user_id=current_user.user_id,
                connection_id=conn.id,
                question=request.question,
                generated_sql=final_state.get("sql_query", ""),
                intent=intent,
                status="PENDING"
            )
            db.add(query_request)
            db.commit()
            db.refresh(query_request)
            
            return NLQueryResponse(
                intent=intent,
                sql_query=final_state.get("sql_query"),
                result=None,
                error=None,
                approval_id=query_request.id,
                access_status="PENDING_APPROVAL"
            )
        
        # If we have a valid SQL, Validate -> Normalize -> Execute
        if final_state.get("sql_query"):
            current_sql = final_state["sql_query"]
            intent = final_state.get("intent", "READ").upper()
            
            # RBAC Permission Check
            from app.rbac.permissions import can_execute_directly
            
            if not can_execute_directly(current_user, intent):
                # User cannot execute directly - create QueryRequest
                from app.models.query_request import QueryRequest
                
                query_request = QueryRequest(
                    user_id=current_user.user_id,
                    connection_id=conn.id,
                    question=request.question,
                    generated_sql=current_sql,
                    intent=intent,
                    status="PENDING"
                )
                db.add(query_request)
                db.commit()
                db.refresh(query_request)
                
                return NLQueryResponse(
                    intent=intent,
                    sql_query=current_sql,
                    result=None,
                    error=None,
                    approval_id=query_request.id,
                    access_status="PENDING_APPROVAL"
                )
            
            # STEP 1: Validate & Normalize
            validation_result = validate_and_normalize_sql(current_sql, dialect="mysql")
            if validation_result["valid"]:
                current_sql = validation_result["sql"] # Use normalized SQL
                print(f"DEBUG: SQL Normalized: {current_sql}")
            else:
                print(f"WARN: SQL Validation failed: {validation_result['error']}. Proceeding with caution.")
            
            try:
                execution_result = execute_query_for_connection(conn, current_sql)
                
                # Phase 5: Generate Insights (Success path)
                from app.ai.nodes.insights import query_insights_generator
                
                # Calculate metadata
                rows = execution_result.get("rows", execution_result.get("data", []))
                row_count = len(rows) if rows else 0
                cols = execution_result.get("columns", []) if execution_result else []
                
                # Get sample data (first 5 rows) for meaningful insights
                sample_data = rows[:5] if rows else []
                
                metadata = {
                    "rows_returned": row_count,
                    "columns": cols,
                    "execution_time": "Unknown" 
                }
                
                insights_inputs = {
                    "question": request.question,
                    "sql_query": current_sql,
                    "result_metadata": metadata,
                    "sample_data": sample_data,  # Pass actual data for analysis
                    "user": current_user
                }
                
                insights_result = query_insights_generator(insights_inputs)
                insights_data = insights_result.get("insights")
                
                # Phase 5: Save to History
                from app.models.query_history import QueryHistory
                history_entry = QueryHistory(
                    user_id=current_user.user_id,
                    connection_id=conn.id,
                    question=request.question,
                    generated_sql=current_sql,
                    intent=final_state.get("intent"),
                    confidence_score=final_state.get("confidence_score", 0.0),
                    is_ambiguous=final_state.get("is_ambiguous", False),
                    insights=insights_data,
                    execution_status="SUCCESS"
                )
                db.add(history_entry)
                db.commit()
                
                # Audit log: Track query execution
                try:
                    from app.services.audit import AuditService
                    await AuditService.log_user_activity(
                        user_id=current_user.user_id,
                        user_email=current_user.email,
                        action="EXECUTE_QUERY",
                        target_id=conn.id,
                        target_type="DB_CONNECTION",
                        details={
                            "database": conn.database_name,
                            "connection_name": conn.name,
                            "question": request.question,
                            "sql_query": current_sql,
                            "intent": final_state.get("intent"),
                            "rows_returned": len(execution_result.get("data", [])),
                            "execution_status": "SUCCESS"
                        }
                    )
                except Exception as audit_error:
                    print(f"WARN: Failed to log audit: {audit_error}")
                
                final_response = NLQueryResponse(
                    intent=final_state["intent"],
                    sql_query=current_sql,
                    result=execution_result,
                    error=None,
                    access_status=access_status,
                    is_ambiguous=False,
                    insights=insights_data,
                    query_id=history_entry.id
                )
                
                break # Success!
            except Exception as e:
                 error_msg = str(e)
                 print(f"DEBUG: Execution Error (Attempt {retry_count}): {error_msg}")
                 
                 # STEP 2: Repair Loop
                 repair_input = {
                     "sql_query": current_sql,
                     "error": error_msg,
                     "user": current_user
                 }
                 repaired_result = repair_sql_query(repair_input)
                 repaired_sql = repaired_result.get("sql_query")
                 
                 if repaired_sql and repaired_sql != current_sql:
                     print(f"DEBUG: Attempting repair... New SQL: {repaired_sql}")
                     # Update inputs so workflow loop knows (or we just hijack the loop)
                     # Since we are inside the 'while' loop of the API, we can just update 'inputs' sql_query?
                     # No, 'inputs' drives the 'workflow_app'. 
                     # Ideally, we should feed this back into the workflow, but our workflow is 'Text -> SQL'.
                     # A quick fix is to manually set the new SQL for the next loop iteration OR 
                     # simply retry the execution logic here.
                     
                     # Better approach for this structure:
                     # We can't easily re-invoke 'workflow_app' with SQL. 
                     # So we will try to execute the REPAIRED SQL immediately in the *next* iteration of this while loop?
                     # No, let's keep it simple: We have a retry_count.
                     # We need to tell the system to use the REPAIRED sql next time.
                     # But 'workflow_app' generates SQL from scratch.
                     
                     # Correct Logic: 
                     # We are handling retries here in the API for now (Architecture Decision).
                     # So let's just update 'final_state["sql_query"]' and 'current_sql' and loop?
                     # But we are utilizing the 'while retry_count <= MAX_RETRIES' which calls 'workflow_app.invoke'
                     
                     # FIX: We should rely on the REPAIR node to provide the SQL.
                     # If we failed, we enter the next iteration.
                     # BUT 'workflow_app' creates a NEW plan.
                     # If we want to support repair, we need to pass the error back to the workflow.
                     # 'inputs["last_error"]' is passed.
                     # Does 'workflow_app' handle 'last_error'? 
                     # Assuming current 'workflow_app' does NOT. 
                     
                     # ALTERNATIVE: 
                     # Modify the loop to use the repaired SQL directly if available, bypassing 'workflow_app' invoke?
                     # OR, trust that 'repair_sql_query' gives us a good SQL and we just try to execute IT?
                     
                     # Let's try to execute the repaired SQL immediately in a sub-loop or recursion?
                     # Or cleaner:
                     # Just update 'final_state["sql_query"]' to repaired_sql and 'continue' the loop,
                     # BUT skip 'workflow_app.invoke' if we have a repair?
                     
                     # Let's implement a "local repair retry" inside this block to be safe.
                     try:
                         print("DEBUG: Executing Repaired SQL...")
                         # Validate repaired SQL?
                         val_rep = validate_and_normalize_sql(repaired_sql, dialect="mysql")
                         if val_rep["valid"]: repaired_sql = val_rep["sql"]
                         
                         execution_result = execute_query_for_connection(conn, repaired_sql)
                         
                         # Success! Generate insights/history/etc.
                         # (Duplicate success logic - implies refactor needed, but for now copying is safer than abstracting blindly)
                         
                         # ... [Copy success logic or function call] ...
                         # To avoid code duplication, let's just break and handle success at end?
                         # Or just return here.
                         pass
                         
                         # SUCCESS COPY
                         from app.ai.nodes.insights import query_insights_generator
                         rows = execution_result.get("rows", execution_result.get("data", []))
                         row_count = len(rows) if rows else 0
                         cols = execution_result.get("columns", []) if execution_result else []
                         sample_data = rows[:5] if rows else []
                         metadata = {"rows_returned": row_count, "columns": cols, "execution_time": "Unknown"}
                         
                         insights_inputs = {"question": request.question, "sql_query": repaired_sql, "result_metadata": metadata, "sample_data": sample_data, "user": current_user}
                         insights_result = query_insights_generator(insights_inputs)
                         insights_data = insights_result.get("insights")
                         
                         from app.models.query_history import QueryHistory
                         history_entry = QueryHistory(
                             user_id=current_user.user_id, connection_id=conn.id, question=request.question,
                             generated_sql=repaired_sql, intent=final_state.get("intent"),
                             confidence_score=final_state.get("confidence_score", 0.0), is_ambiguous=False,
                             insights=insights_data, execution_status="SUCCESS"
                         )
                         db.add(history_entry)
                         db.commit()
                         
                         final_response = NLQueryResponse(
                             intent=final_state["intent"], sql_query=repaired_sql, result=execution_result,
                             error=None, access_status=access_status, is_ambiguous=False,
                             insights=insights_data, query_id=history_entry.id
                         )
                         return final_response
                         
                     except Exception as e2:
                         print(f"DEBUG: Repair failed too: {e2}")
                         retry_count += 1
                         inputs["last_error"] = str(e2)
                         continue # Retry full generation
                 
                 retry_count += 1
                 inputs["last_error"] = error_msg
                 
                 if retry_count > MAX_RETRIES:
                     # Translate raw error to user friendly message
                     user_error = "I couldn't run this query. "
                     if "syntax" in error_msg.lower():
                         user_error += "It looks like there's a syntax issue I couldn't automatically fix."
                     elif "column" in error_msg.lower():
                         user_error += "I might represent a column name that doesn't exist."
                     else:
                         user_error += "There was a database error."
                     
                     final_response = NLQueryResponse(
                        intent=final_state["intent"],
                        sql_query=final_state["sql_query"],
                        result=None,
                        error=f"{user_error} (Raw: {error_msg})",
                        access_status=access_status
                    )
        else:
            final_response = NLQueryResponse(
                intent=final_state.get("intent", "UNKNOWN"),
                sql_query=None,
                result=None,
                error="No SQL generated",
                access_status=access_status
            )
            break
            
    if final_response is None:
        return NLQueryResponse(
            intent="ERROR",
            sql_query=None,
            result=None,
            error="Failed to generate a valid query after multiple attempts."
        )
        
    return final_response
class RunSQLRequest(BaseModel):
    connection_id: int
    sql_query: str

@router.post("/run", response_model=NLQueryResponse)
def run_raw_sql_query(
    request: RunSQLRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user),
):
    conn = db.query(DBConnection).filter(DBConnection.id == request.connection_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    if conn.owner_id != current_user.user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    try:
        execution_result = execute_query_for_connection(conn, request.sql_query)
        return NLQueryResponse(
            intent="DIRECT_EXECUTION",
            sql_query=request.sql_query,
            result=execution_result,
            error=None
        )
    except Exception as e:
        return NLQueryResponse(
            intent="ERROR",
            sql_query=request.sql_query,
            result=None,
            error=f"Execution Error: {str(e)}"
        )
