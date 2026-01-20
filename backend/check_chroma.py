from app.rag.store import vector_store

try:
    collections = vector_store.client.list_collections()
    print("Collections found:", [c.name for c in collections])
    
    for c in collections:
        print(f"Collection {c.name} has {c.count()} documents.")
        if c.count() > 0:
            print(f"Sample doc: {c.peek(limit=1)}")
except Exception as e:
    print(f"Error: {e}")
