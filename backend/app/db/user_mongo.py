from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from typing import Optional

class UserMongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    async def connect_to_database(self):
        if not settings.USER_MONGODB_DATABASE_URL:
            print("WARN: USER_MONGODB_DATABASE_URL not found. User management will not work.")
            return

        print("Connecting to User Management MongoDB...")
        self.client = AsyncIOMotorClient(settings.USER_MONGODB_DATABASE_URL)
        
        try:
            await self.client.admin.command('ping')
            print("Successfully connected to User Management MongoDB!")
            self.db = self.client['queryflow-ai-user-management']
            print(f"Using database: {self.db.name}")
            
            # Create indexes for performance
            await self.db.users.create_index("email", unique=True)
            await self.db.users.create_index("user_id", unique=True)  # For backward compatibility
            await self.db.roles.create_index("name", unique=True)
            print("MongoDB indexes created successfully")
        except Exception as e:
            print(f"Error connecting to User Management MongoDB: {e}")
            self.client = None
            self.db = None

    async def close_database_connection(self):
        if self.client:
            self.client.close()
            print("User Management MongoDB connection closed")

user_mongo_db = UserMongoDB()

async def get_user_mongo_db():
    """Get the user management MongoDB database instance"""
    if user_mongo_db.db is None:
        await user_mongo_db.connect_to_database()
    return user_mongo_db.db
