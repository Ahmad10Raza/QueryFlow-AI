try:
    from app.ai.graph import app
    print("Graph compiled successfully.")
    
    # Optional: Print graph structure
    for node in app.get_graph().nodes:
        print(f"Node: {node}")
except Exception as e:
    print(f"Graph verification failed: {e}")
    import traceback
    traceback.print_exc()
