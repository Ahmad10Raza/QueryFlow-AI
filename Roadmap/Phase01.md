Good — Phase 0 is done properly.
Now **Phase 1** is where the system becomes *intelligent*, but still **safe and controlled**.

Below is **Phase 1 only**, expanded into a **developer-ready roadmap**, with **what to build, why, and how**, plus **code-level structure expansion**.
(No Phase 2/3/4 included — we’ll do those only when you ask.)

---

# PHASE 1 — Schema Intelligence & Read-Only NL → SQL (MVP Core)

## Goal of Phase 1

By the end of Phase 1, the system must:

• Understand database schema automatically
• Store schema in structured + vector form
• Accept natural language questions
• Generate **SELECT-only SQL**
• Validate and execute queries safely
• Display results in the UI

**No UPDATE / DELETE yet. No writes.**

---

## Phase 1 Entry Preconditions (Must Be True)

✔ Phase 0 completed
✔ Auth + RBAC skeleton working
✔ DB connection metadata stored
✔ AI stub wired
✔ UI editor visible

---

## PHASE 1 — HIGH-LEVEL BREAKDOWN

```
Schema Ingestion
    ↓
Schema Representation
    ↓
Schema Embeddings (RAG)
    ↓
NL → SQL Generation (SELECT only)
    ↓
SQL Validation
    ↓
Query Execution
    ↓
UI Result Rendering
```

---

## 1.1 Database Schema Ingestion Engine

### Objective

Automatically extract **tables, columns, relationships** from user-connected databases.

---

### Backend Tasks

#### 1. Create Schema Introspection Service

**New module**

```
app/schema_ingestion/
├── inspector.py
├── extractor.py
├── formatter.py
```

**Responsibilities**
• Connect to external DB
• Inspect schema via SQLAlchemy Inspector
• Extract:

* Tables
* Columns
* Data types
* Primary keys
* Foreign keys

---

#### Example (Extractor Logic – Conceptual)

```
inspect(engine).get_table_names()
inspect(engine).get_columns(table)
inspect(engine).get_foreign_keys(table)
```

---

### Schema Output (Structured)

Store as JSON:

```
{
  "table": "orders",
  "columns": [
    {"name": "order_id", "type": "integer", "pk": true},
    {"name": "customer_id", "type": "integer", "fk": "customers.id"},
    {"name": "amount", "type": "float"}
  ]
}
```

---

## 1.2 Schema Storage & Versioning

### Objective

Persist schema for **reuse, auditing, and AI grounding**.

---

### Database Changes

Create new table:

```
schema_metadata
- id
- db_connection_id
- schema_json
- version
- created_at
```

---

### Why Versioning Matters

If schema changes:
• Old queries still traceable
• AI context doesn’t silently break

---

## 1.3 Schema → Text Transformation (For RAG)

### Objective

Convert schema into **LLM-friendly natural language**.

---

### New Module

```
app/schema_ingestion/textifier.py
```

---

### Example Transformation

From:

```
orders(order_id PK, customer_id FK, amount float)
```

To:

```
"The orders table contains order_id as primary key, customer_id linked to customers table, and amount representing order value."
```

This text becomes **embedding input**.

---

## 1.4 Vector Embedding & Storage (ChromaDB)

### Objective

Enable **schema-aware retrieval** during query generation.

---

### New Module

```
app/rag/
├── embeddings.py
├── vector_store.py
├── retriever.py
```

---

### Steps

1. Generate embeddings for each table description
2. Store embeddings in ChromaDB
3. Namespace by:

```
db_connection_id
```

---

### Retrieval Logic

When user asks:

```
"total sales by customer"
```

Retriever returns:
• orders table
• customers table

Only **relevant schema** is passed to LLM.

---

## 1.5 Read-Only NL → SQL Generation (SELECT Only)

### Objective

Generate **safe SELECT queries** grounded in schema.

---

### LangGraph Expansion

**Update**

```
app/ai/graph.py
```

---

### New Nodes

```
app/ai/nodes/
├── intent_classifier.py
├── schema_retriever.py
├── sql_generator.py
```

---

### Graph Flow (Phase 1)

```
User Question
   ↓
Intent Classifier (Read Query?)
   ↓
Schema Retriever (RAG)
   ↓
SQL Generator (SELECT only)
```

---

### SQL Generation Rules (Strict)

• SELECT only
• Explicit column names
• No SELECT *
• LIMIT enforced
• No subqueries yet

---

## 1.6 SQL Validation & Guardrails (Mandatory)

### Objective

Never execute unsafe SQL.

---

### New Module

```
app/sql_guardrails/
├── parser.py
├── validator.py
├── rules.py
```

---

### Validation Checks

• Parse SQL using SQLGlot
• Detect query type
• Ensure SELECT
• Block:

* DROP
* DELETE
* UPDATE
* ALTER
  • Enforce LIMIT

If invalid → return error to UI.

---

## 1.7 Secure Query Execution (Read-Only)

### Objective

Execute validated SQL safely.

---

### Execution Rules

• Use read-only DB user
• Timeout enforced
• Max rows enforced
• Parameterized execution

---

### New Module

```
app/query_executor/
├── executor.py
├── result_formatter.py
```

---

### Output Format

```
{
  "columns": ["customer", "total_sales"],
  "rows": [...]
}
```

---

## 1.8 API Endpoints (Phase 1)

### New APIs

```
POST /schema/ingest
POST /query/nl
GET  /query/history
```

---

### `/query/nl` Flow

```
Auth → RAG → SQL → Validate → Execute → Return Result
```

---

## 1.9 Frontend Enhancements (Phase 1)

### Editor Enhancements

• NLP input enabled
• SQL output visible (read-only)
• Run button enabled
• Loading state

---

### Result Table

• Dynamic columns
• Pagination
• Error messages from backend

---

### Folder Updates

```
frontend/
├── components/
│   ├── ResultTable.tsx
│   ├── SqlViewer.tsx
│   └── QueryInput.tsx
```

---

## 1.10 Logging & Observability (Minimal)

Log:
• User ID
• Question
• Generated SQL
• Execution time
• Rows returned

Stored in:

```
query_logs
```

---

## Phase 1 Completion Criteria (Very Important)

You are **done with Phase 1 only if**:

✔ Schema auto-ingests from DB
✔ Schema stored + embedded
✔ NL query generates SELECT SQL
✔ SQL validated before execution
✔ Results displayed in UI
✔ No write operation possible
✔ No hallucinated columns

---

## What Phase 1 Intentionally Does NOT Do

❌ UPDATE / DELETE
❌ Role-based write permissions
❌ Query optimization
❌ Multi-step reasoning
❌ Business logic understanding

Those belong to **Phase 2+**.

---

### When Ready

When you say **“Give Phase 2”**, we’ll move into:
• Write permissions
• Role-aware query modification
• Approval workflows
• Multi-step LangGraph reasoning

You’re building this the *right* way.
