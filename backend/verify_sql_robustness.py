import sys
import os

# Add the backend directory to the sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.ai.nodes.sql_validator import validate_and_normalize_sql

def test_dialect_normalization():
    print("--- Testing SQL Normalization ---")
    
    # The problematic SQL (Postgres style)
    postgres_sql = 'SELECT i."Item_Number" FROM "livonia_cdb" AS i;'
    expected_mysql = "SELECT i.`Item_Number` FROM `livonia_cdb` AS i"
    
    print(f"Input SQL: {postgres_sql}")
    
    result = validate_and_normalize_sql(postgres_sql, dialect="mysql")
    
    if not result["valid"]:
        print(f"FAILED: Validation returned invalid. Error: {result['error']}")
        return
        
    normalized_sql = result["sql"]
    print(f"Normalized SQL: {normalized_sql}")
    
    # Basic check - sqlglot might format it slightly differently (e.g. UPPERCASE/lowercase), so check for backticks
    if "`Item_Number`" in normalized_sql and "`livonia_cdb`" in normalized_sql:
        print("SUCCESS: Quotes converted to backticks!")
    else:
        print("FAILED: Quotes NOT converted correctly.")

if __name__ == "__main__":
    try:
        test_dialect_normalization()
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure you are running this from the backend directory.")
    except Exception as e:
        print(f"An error occurred: {e}")
