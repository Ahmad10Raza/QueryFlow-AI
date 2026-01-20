import os
from dotenv import load_dotenv

# Load .env file explicitly before importing app modules
# This ensures Pydantic settings can find the variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash
import sys

def create_initial_user():
    db = SessionLocal()
    try:
        # Check if Admin Role exists, create if not
        admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
        if not admin_role:
            print("Creating ADMIN role...")
            admin_role = Role(name="ADMIN")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        # Create User
        email = "admin@example.com"
        password = "password123"
        
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User {email} already exists.")
            return

        print(f"Creating user {email}...")
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            role_id=admin_role.id,
            is_superuser=True
        )
        db.add(user)
        db.commit()
        print("User created successfully!")
        print(f"Login with: Email={email}, Password={password}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_user()
