from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_database(self):
        if not settings.MONGO_DATABASE_URL:
            print("WARN: MONGO_DATABASE_URL not found in settings. MongoDB features will be disabled.")
            return

        print("Connecting to MongoDB...")
        self.client = AsyncIOMotorClient(settings.MONGO_DATABASE_URL)
        # Verify connection
        try:
            await self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            # Use dedicated database for audit logs
            self.db = self.client['queryflow-ai-log']
            print(f"Using database: {self.db.name}")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.client = None

    async def close_database_connection(self):
        if self.client:
            print("Closing MongoDB connection...")
            self.client.close()
            print("MongoDB connection closed.")

mongo_db = MongoDB()

async def get_mongo_db():
    return mongo_db.db
