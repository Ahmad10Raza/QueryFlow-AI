from langchain_community.vectorstores import Chroma
from app.core.config import settings
from app.ai.utils.llm_factory import get_embeddings
from typing import List, Any

class VectorStore:
    def get_store(self, collection_name: str):
        embeddings = get_embeddings()
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        )
        
    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[dict], ids: List[str]):
        store = self.get_store(collection_name)
        store.add_texts(
            texts=documents,
            metadatas=metadatas,
            ids=ids
        )
        
    def query(self, collection_name: str, query_text: str, n_results: int = 5):
        store = self.get_store(collection_name)
        return store.similarity_search(query_text, k=n_results)
        
    # Expose client for maintenance scripts if needed, but LangChain wraps it.
    @property
    def client(self):
        # This is a hack if we really need raw client, but strict usage suggests avoiding it.
        # But check_chroma.py uses it.
        # LangChain Chroma has a .client attribute? Yes.
        # We can just return a raw client using same settings.
        import chromadb
        return chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)

vector_store = VectorStore()
