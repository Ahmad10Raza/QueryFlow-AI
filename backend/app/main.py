from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

from fastapi.middleware.cors import CORSMiddleware
from app.db.mongo import mongo_db
from app.db.user_mongo import user_mongo_db

@app.on_event("startup")
async def startup_db_client():
    await mongo_db.connect_to_database()
    await user_mongo_db.connect_to_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    await mongo_db.close_database_connection()
    await user_mongo_db.close_database_connection()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to QueryFlow AI API"}

from app.api import auth, users, db_connections, schema, query, schema_explorer, approvals, history, query_requests

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(db_connections.router, prefix=f"{settings.API_V1_STR}/db_connections", tags=["db_connections"])
app.include_router(schema.router, prefix=f"{settings.API_V1_STR}/schema", tags=["schema"])
app.include_router(schema_explorer.router, prefix=f"{settings.API_V1_STR}/schema_explorer", tags=["schema_explorer"])
app.include_router(query.router, prefix=f"{settings.API_V1_STR}/query", tags=["query"])
app.include_router(approvals.router, prefix=f"{settings.API_V1_STR}/approvals", tags=["approvals"])
app.include_router(history.router, prefix=f"{settings.API_V1_STR}/history", tags=["history"])
app.include_router(query_requests.router, prefix=f"{settings.API_V1_STR}/query-requests", tags=["query_requests"])

from app.api import admin_users
app.include_router(admin_users.router, prefix=f"{settings.API_V1_STR}/admin/users", tags=["admin_users"])

from app.api import admin_stats
app.include_router(admin_stats.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin_stats"])


