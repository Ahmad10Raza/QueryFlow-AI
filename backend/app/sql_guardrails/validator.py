import sqlglot
from sqlglot import exp

def validate_sql(sql_query: str) -> bool:
    """
    Validates that the SQL query is a safe SELECT statement.
    """
    try:
        parsed = sqlglot.parse_one(sql_query)
        
        # 1. Must be a permitted statement type (SELECT, UPDATE, INSERT, DELETE)
        allowed_types = (exp.Select, exp.Update, exp.Insert, exp.Delete)
        if not isinstance(parsed, allowed_types):
             return False, "Only SELECT, UPDATE, INSERT, DELETE statements are allowed."
            
        # 2. Check for unsafe DDL/System commands
        # Scan for Drop, Alter, Grant, Revoke. Use Command for generic.
        unsafe_types = (exp.Drop, exp.Alter, exp.Create, exp.Command)
        for node in parsed.find_all(exp.Expression):
             if isinstance(node, unsafe_types):
                 return False, f"Unsafe operation detected: {node.key}."
                 
        return True, "Query is safe."
        
    except Exception as e:
        return False, f"SQL Parsing Error: {str(e)}"
