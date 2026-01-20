import sqlglot
from sqlglot.errors import ParseError

def validate_and_normalize_sql(sql: str, dialect: str = "mysql") -> dict:
    """
    Validates and normalizes SQL for the target dialect.
    
    Args:
        sql: The raw SQL string
        dialect: The target dialect (default: mysql)
        
    Returns:
        dict: {
            "valid": bool,
            "sql": str (normalized if valid, original if invalid),
            "error": str (if invalid)
        }
    """
    try:
        # Parse logic
        # sqlglot.parse_one handles parsing. 
        # read=None means auto-detect or generic, but specifying source dialect helps if we know it.
        # However, LLMs mix dialects, so letting sqlglot try to parse generic is often best,
        # OR we can try to read as postgres (common LLM default) and transpile to mysql.
        
        # Strategy: Transpile directly. 
        # This takes the input SQL (potentially mixed/postgres) and output valid MySQL.
        logger_mode = "postgres" # Assume LLM often defaults to postgres style quotes
        
        transpiled = sqlglot.transpile(sql, read=None, write=dialect)[0]
        
        return {
            "valid": True,
            "sql": transpiled,
            "error": None
        }
        
    except ParseError as e:
        return {
            "valid": False,
            "sql": sql,
            "error": f"SQL Parse Error: {str(e)}"
        }
    except Exception as e:
         return {
            "valid": False,
            "sql": sql,
            "error": f"Validation Error: {str(e)}"
        }
