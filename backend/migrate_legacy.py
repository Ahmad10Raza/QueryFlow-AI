import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Setup DB connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate():
    db = SessionLocal()
    try:
        # Fetch all legacy approvals
        print("Fetching legacy approvals...")
        result = db.execute(text("SELECT * FROM query_approvals"))
        approvals = result.fetchall()
        
        print(f"Found {len(approvals)} legacy approvals.")
        
        migrated_count = 0
        
        for row in approvals:
            # Check if already migrated? (Maybe duplicate check?)
            # For simple migration, we assume we want to move them all.
            # Convert Row to dict-like access if needed
            
            # Map fields
            user_id = row.requested_by_user_id
            connection_id = row.db_connection_id
            question = row.prompt_text
            generated_sql = row.generated_sql
            status = row.status
            approved_by = None # Legacy doesn't store WHO approved easily (maybe in logs), but table has no 'reviewer_id' column usuall? 
            # Wait, legacy table definition?
            # Let's assume approved_by is missing or we leave it null.
            
            approved_at = row.reviewed_at
            rejection_reason = row.reviewer_comment
            created_at = row.created_at
            
            # Infer Intent
            sql_upper = generated_sql.upper()
            if "DELETE" in sql_upper:
                intent = "DELETE"
            elif "UPDATE" in sql_upper:
                intent = "UPDATE"
            elif "INSERT" in sql_upper:
                intent = "CREATE"
            else:
                intent = "READ"
                
            # Insert into query_requests
            # We use raw SQL or models. Using raw SQL to avoid model constraints/issues
            
            insert_query = text("""
                INSERT INTO query_requests 
                (user_id, connection_id, question, generated_sql, intent, status, approved_at, rejection_reason, created_at, approved_by)
                VALUES (:user_id, :connection_id, :question, :generated_sql, :intent, :status, :approved_at, :rejection_reason, :created_at, :approved_by)
            """)
            
            db.execute(insert_query, {
                "user_id": user_id,
                "connection_id": connection_id,
                "question": question,
                "generated_sql": generated_sql,
                "intent": intent,
                "status": status,
                "approved_at": approved_at,
                "rejection_reason": rejection_reason,
                "created_at": created_at,
                "approved_by": None # Cannot easily map
            })
            
            migrated_count += 1
            
        # Commit
        db.commit()
        print(f"Successfully migrated {migrated_count} records.")
        
        # Optional: Delete from old table?
        # db.execute(text("DELETE FROM query_approvals"))
        # db.commit()
        # print("Cleared legacy table.")
        
    except Exception as e:
        print(f"Error migrating: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
