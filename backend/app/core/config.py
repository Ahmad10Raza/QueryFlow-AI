from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "QueryFlow AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours for development
    
    DATABASE_URL: str
    MONGO_DATABASE_URL: Optional[str] = None  # For audit logs
    USER_MONGODB_DATABASE_URL: Optional[str] = None  # For user management
    
    # AI / LLM Configuration
    LLM_PROVIDER: str = "ollama" # ollama, openai, anthropic, gemini
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3" # or mistral, etc
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    
    # Gemini
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"
    
    # Vector DB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
