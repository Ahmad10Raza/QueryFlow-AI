from app.core.config import settings
from app.services.credential_encryptor import encryptor
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from typing import Optional

def get_llm(user=None):
    # Default to system settings
    provider = settings.LLM_PROVIDER.lower()
    model = None
    api_key = None
    
    # Overwrite if user has valid config
    if user and user.llm_provider:
        provider = user.llm_provider.lower()
        model = user.llm_model
        if user.llm_api_key_encrypted:
            try:
                api_key = encryptor.decrypt(user.llm_api_key_encrypted)
            except:
                pass # Fallback or error? For now fallback or fail naturally.

    print(f"DEBUG: Initializing LLM Provider={provider}, Model={model}, HasKey={bool(api_key)}")

    if provider == "ollama":
        return ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=model or settings.OLLAMA_MODEL
        )
    elif provider == "openai":
        return ChatOpenAI(
            api_key=api_key or settings.OPENAI_API_KEY,
            model=model or settings.OPENAI_MODEL
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            api_key=api_key or settings.ANTHROPIC_API_KEY,
            model_name=model or settings.ANTHROPIC_MODEL
        )
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            google_api_key=api_key or settings.GOOGLE_API_KEY,
            model=model or settings.GEMINI_MODEL
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings

def get_embeddings():
    # Use config for embedding provider, default to openai or ollama
    # For now, let's look at LLM_PROVIDER or a separate EMBEDDING_PROVIDER
    # Assuming we use same provider for embeddings if possible
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "ollama":
        return OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model="nomic-embed-text" # Common default, or add to config
        )
    else:
        # Default to OpenAI if not ollama (or explicit openai)
        return OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY
        )
