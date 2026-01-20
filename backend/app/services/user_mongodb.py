from passlib.context import CryptContext
from app.db.user_mongo import get_user_mongo_db
from app.models.user_mongo import UserDocument, RoleDocument, UserCreate, UserUpdate
from typing import Optional, List
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserMongoService:
    @staticmethod
    async def get_next_user_id() -> int:
        """Generate next sequential user_id for backward compatibility"""
        db = await get_user_mongo_db()
        if db is None:
            raise Exception("User MongoDB not connected")
        
        # Find the highest user_id
        last_user = await db.users.find_one(sort=[("user_id", -1)])
        if last_user:
            return last_user["user_id"] + 1
        return 1

    @staticmethod
    async def create_user(user_data: UserCreate) -> UserDocument:
        """Create a new user in MongoDB"""
        db = await get_user_mongo_db()
        if db is None:
            raise Exception("User MongoDB not connected")
        
        # Check if email already exists
        existing = await db.users.find_one({"email": user_data.email})
        if existing:
            raise ValueError("Email already registered")
        
        # Get role name
        role = await db.roles.find_one({"role_id": user_data.role_id})
        role_name = role["name"] if role else "USER"
        
        # Generate user_id
        user_id = await UserMongoService.get_next_user_id()
        
        user_doc = UserDocument(
            user_id=user_id,
            email=user_data.email,
            hashed_password=pwd_context.hash(user_data.password),
            is_superuser=user_data.is_superuser,
            role_id=user_data.role_id,
            role_name=role_name,
            is_active=True
        )
        
        result = await db.users.insert_one(user_doc.model_dump(by_alias=True, exclude={"id"}))
        user_doc.id = result.inserted_id
        return user_doc

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[UserDocument]:
        """Get user by email"""
        db = await get_user_mongo_db()
        if db is None:
            return None
        
        user_data = await db.users.find_one({"email": email})
        if user_data:
            return UserDocument(**user_data)
        return None

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[UserDocument]:
        """Get user by user_id (SQL compatibility)"""
        db = await get_user_mongo_db()
        if db is None:
            return None
        
        user_data = await db.users.find_one({"user_id": user_id})
        if user_data:
            return UserDocument(**user_data)
        return None

    @staticmethod
    async def get_all_users(skip: int = 0, limit: int = 100) -> List[UserDocument]:
        """Get all users with pagination"""
        db = await get_user_mongo_db()
        if db is None:
            return []
        
        cursor = db.users.find().skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        return [UserDocument(**u) for u in users]

    @staticmethod
    async def update_user(user_id: int, update_data: UserUpdate) -> Optional[UserDocument]:
        """Update user information"""
        db = await get_user_mongo_db()
        if db is None:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_dict:
            update_dict["hashed_password"] = pwd_context.hash(update_dict.pop("password"))
        
        # Update role_name if role_id changed
        if "role_id" in update_dict:
            role = await db.roles.find_one({"role_id": update_dict["role_id"]})
            if role:
                update_dict["role_name"] = role["name"]
        
        if update_dict:
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": update_dict}
            )
        
        return await UserMongoService.get_user_by_id(user_id)

    @staticmethod
    async def update_last_login(user_id: int):
        """Update last login timestamp"""
        db = await get_user_mongo_db()
        if db is None:
            return
        
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"last_login_at": datetime.utcnow()}}
        )

    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def delete_user(user_id: int):
        """Soft delete user by marking inactive and changing email"""
        db = await get_user_mongo_db()
        if db is None:
            return
        
        user = await UserMongoService.get_user_by_id(user_id)
        if user:
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "is_active": False,
                    "email": f"deleted_{user_id}_{user.email}"
                }}
            )

class RoleMongoService:
    @staticmethod
    async def create_role(role_id: int, name: str, description: str = None) -> RoleDocument:
        """Create a new role"""
        db = await get_user_mongo_db()
        if db is None:
            raise Exception("User MongoDB not connected")
        
        role_doc = RoleDocument(
            role_id=role_id,
            name=name,
            description=description
        )
        
        result = await db.roles.insert_one(role_doc.model_dump(by_alias=True, exclude={"id"}))
        role_doc.id = result.inserted_id
        return role_doc

    @staticmethod
    async def get_role_by_name(name: str) -> Optional[RoleDocument]:
        """Get role by name"""
        db = await get_user_mongo_db()
        if db is None:
            return None
        
        role_data = await db.roles.find_one({"name": name})
        if role_data:
            return RoleDocument(**role_data)
        return None

    @staticmethod
    async def get_role_by_id(role_id: int) -> Optional[RoleDocument]:
        """Get role by role_id"""
        db = await get_user_mongo_db()
        if db is None:
            return None
        
        role_data = await db.roles.find_one({"role_id": role_id})
        if role_data:
            return RoleDocument(**role_data)
        return None
