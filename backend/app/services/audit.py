from datetime import datetime
from app.db.mongo import get_mongo_db
from app.core.config import settings

class AuditService:
    @staticmethod
    async def log_user_activity(
        user_id: int,
        user_email: str,
        action: str,
        target_id: int = None,
        target_type: str = None,
        details: dict = None
    ):
        """
        Logs any user activity to MongoDB (queries, admin actions, logins, etc.)
        """
        if not settings.MONGO_DATABASE_URL:
            return  # MongoDB not configured

        db = await get_mongo_db()
        if db is None:
            print("WARN: MongoDB not connected. Audit log skipped.")
            return

        log_entry = {
            "user_id": user_id,
            "user_email": user_email,
            "action": action,
            "target_id": target_id,
            "target_type": target_type,
            "details": details or {},
            "timestamp": datetime.utcnow()
        }

        try:
            await db.activity_logs.insert_one(log_entry)
        except Exception as e:
            print(f"ERROR: Failed to write audit log: {e}")

    @staticmethod
    async def get_audit_logs(limit: int = 50, skip: int = 0):
        db = await get_mongo_db()
        if db is None:
            return []

        cursor = db.activity_logs.find().sort("timestamp", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for log in logs:
            log["_id"] = str(log["_id"])
            
        return logs
