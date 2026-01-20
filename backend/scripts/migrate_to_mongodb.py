"""
Migration script to move users and roles from SQL to MongoDB
Run this once to migrate existing data
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.query_history import QueryHistory
from app.models.db_connection import DBConnection
from app.services.user_mongodb import UserMongoService, RoleMongoService
from app.models.user_mongo import UserDocument, RoleDocument

async def migrate_roles():
    """Migrate roles from SQL to MongoDB"""
    db = SessionLocal()
    try:
        roles = db.query(Role).all()
        print(f"Found {len(roles)} roles to migrate")
        
        for role in roles:
            try:
                existing_role = await RoleMongoService.get_role_by_id(role.id)
                if existing_role:
                    print(f"Role {role.name} already exists, skipping...")
                    continue
                
                await RoleMongoService.create_role(
                    role_id=role.id,
                    name=role.name,
                    description=role.description
)
                print(f"✓ Migrated role: {role.name} (ID: {role.id})")
            except Exception as e:
                print(f"✗ Failed to migrate role {role.name}: {e}")
        
        print(f"\n✅ Role migration complete!")
    finally:
        db.close()

async def migrate_users():
    """Migrate users from SQL to MongoDB"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"\nFound {len(users)} users to migrate")
        
        for user in users:
            try:
                existing_user = await UserMongoService.get_user_by_id(user.id)
                if existing_user:
                    print(f"User {user.email} already exists, skipping...")
                    continue
                
                # Get role name
                role_name = user.role.name if user.role else "USER"
                
                user_doc = UserDocument(
                    user_id=user.id,
                    email=user.email,
                    hashed_password=user.hashed_password,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser,
                    role_id=user.role_id if user.role_id else 1,
                    role_name=role_name,
                    llm_provider=getattr(user, 'llm_provider', None),
                    llm_model=getattr(user, 'llm_model', None),
                    llm_api_key_encrypted=getattr(user, 'llm_api_key_encrypted', None),
                    created_at=getattr(user, 'created_at', datetime.utcnow()),
                    last_login_at=getattr(user, 'last_login_at', None)
                )
                
                from app.db.user_mongo import get_user_mongo_db
                mongo_db = await get_user_mongo_db()
                await mongo_db.users.insert_one(user_doc.model_dump(by_alias=True, exclude={"id"}))
                
                print(f"✓ Migrated user: {user.email} (ID: {user.id}, Role: {role_name})")
            except Exception as e:
                print(f"✗ Failed to migrate user {user.email}: {e}")
        
        print(f"\n✅ User migration complete!")
    finally:
        db.close()

async def verify_migration():
    """Verify migration was successful"""
    print("\n" + "="*50)
    print("VERIFICATION")
    print("="*50)
    
    from app.db.user_mongo import get_user_mongo_db
    mongo_db = await get_user_mongo_db()
    
    user_count = await mongo_db.users.count_documents({})
    role_count = await mongo_db.roles.count_documents({})
    
    print(f"MongoDB Users: {user_count}")
    print(f"MongoDB Roles: {role_count}")
    
    # Show sample users
    print("\nSample users:")
    cursor = mongo_db.users.find().limit(5)
    async for user in cursor:
        print(f"  - {user['email']} (ID: {user['user_id']}, Role: {user.get('role_name', 'N/A')})")

async def main():
    print("="*50)
    print("SQL TO MONGODB MIGRATION")
    print("="*50)
    
    # Connect to MongoDB
    from app.db.user_mongo import user_mongo_db
    await user_mongo_db.connect_to_database()
    
    # Migrate roles first (users depend on roles)
    await migrate_roles()
    
    # Migrate users
    await migrate_users()
    
    # Verify
    await verify_migration()
    
    print("\n" + "="*50)
    print("MIGRATION COMPLETE!")
    print("="*50)
    print("\nNext steps:")
    print("1. Restart the backend server")
    print("2. Test login with existing credentials")
    print("3. Verify admin dashboard works")
    print("4. Once verified, you can remove SQL user tables if desired")

if __name__ == "__main__":
    asyncio.run(main())
