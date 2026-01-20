
import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.query_history import QueryHistory
from app.models.db_connection import DBConnection
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_super_admin():
    db = SessionLocal()
    try:
        # 1. Create all roles if they don't exist
        roles_to_create = [
            ("USER", "Standard user with basic access"),
            ("MANAGER", "Manager with elevated permissions"),
            ("ADMIN", "Administrator with advanced permissions"),
            ("SUPER_ADMIN", "Platform Super Administrator")
        ]
        
        for role_name, role_desc in roles_to_create:
            existing_role = db.query(Role).filter(Role.name == role_name).first()
            if not existing_role:
                print(f"Creating {role_name} role...")
                new_role = Role(name=role_name, description=role_desc)
                db.add(new_role)
        
        db.commit()
        
        # 2. Get SUPER_ADMIN role
        sa_role = db.query(Role).filter(Role.name == "SUPER_ADMIN").first()
        
        # 2. Check for existing Super Admin User
        # Replace this email with the one you want to promote or create
        ADMIN_EMAIL = "superadmin@queryflow.ai"
        DEFAULT_PASS = "admin123"
        
        user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if not user:
            print(f"Creating Super Admin user: {ADMIN_EMAIL}")
            user = User(
                email=ADMIN_EMAIL,
                hashed_password=pwd_context.hash(DEFAULT_PASS),
                is_active=True,
                is_superuser=True,
                role_id=sa_role.id
            )
            db.add(user)
            db.commit()
            print(f"Super Admin created. Login with {ADMIN_EMAIL} / {DEFAULT_PASS}")
        else:
            # Upgrade existing user
            print(f"Upgrading existing user {ADMIN_EMAIL} to SUPER_ADMIN")
            user.role_id = sa_role.id
            user.is_superuser = True
            db.commit()
            print("User upgraded.")

    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_super_admin()
