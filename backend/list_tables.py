
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    print('Listing all tables across all databases:')
    result = conn.execute(text("""
        SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """))
    
    current_schema = None
    for row in result:
        schema_name = row[0]
        table_name = row[1]
        table_type = row[2]
        if schema_name != current_schema:
            current_schema = schema_name
            print(f'\nSchema: {current_schema}')
        print(f'  - {table_name} ({table_type})')
