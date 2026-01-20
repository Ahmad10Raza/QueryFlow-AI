from app.core.config import settings

# This is a factory to return the appropriate embedding function
# For now, we will rely on Chroma's default or simple sentence transformers if available,
# or we can plug in OpenAIEmbeddings/OllamaEmbeddings
# Phase 1 simplified: Use Chroma default (all-MiniLM-L6-v2) for local dev
# or switch based on config.

def get_embedding_function():
    if settings.LLM_PROVIDER == "openai":
        from chromadb.utils import embedding_functions
        if settings.OPENAI_API_KEY:
             return embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name="text-embedding-3-small"
            )
    
    # Default to generic sentence transformer (built-in to chroma)
    from chromadb.utils import embedding_functions
    return embedding_functions.DefaultEmbeddingFunction()
