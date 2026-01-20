def textify_schema(schema_json: dict) -> str:
    """
    Converts structured schema JSON into natural language text for embedding.
    """
    docs = []
    metadatas = []
    ids = []
    
    for table, details in schema_json.items():
        col_desc = []
        for col in details["columns"]:
            pk_str = " (Primary Key)" if col["primary_key"] else ""
            col_desc.append(f"{col['name']} ({col['type']}){pk_str}")
            
        fk_desc = []
        for fk in details["foreign_keys"]:
            fk_desc.append(f"Foreign Key from {fk['constrained_columns']} to {fk['referred_table']}.{fk['referred_columns']}")
            
        desc = f"Table '{table}' has columns: {', '.join(col_desc)}."
        if fk_desc:
            desc += " " + " ".join(fk_desc)
            
        docs.append(desc)
        metadatas.append({"table": table})
        ids.append(f"table_{table}")
        
    return docs, metadatas, ids
