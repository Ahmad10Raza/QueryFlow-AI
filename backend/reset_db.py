
from app.db.session import engine
from app.db.base import Base

print("Dropping all tables...")
# Reflect all tables first to handle dependencies correctly if needed, 
# but drop_all usually handles this if metadata is complete. 
# However, if there are tables NOT in metadata (like Alembic's), we might need to be forceful.
# Base.metadata.drop_all(bind=engine) 

# Let's use raw SQL to disable FK checks for a clean wipe, 
# because just Base.metadata.drop_all might miss tables that are not in the models or issues with FKs.
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    
    # Get all tables
    result = conn.execute(text("SHOW TABLES"))
    tables = [row[0] for row in result]
    
    for table in tables:
        print(f"Dropping {table}...")
        conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
        
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    conn.commit()

print("All tables dropped.")
