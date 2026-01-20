Phase 0: Platform Foundations & System Bootstrapping
 Project Initialization

 Create directory structure (backend/, frontend/)
 Initialize git (already done)
 Backend Setup (FastAPI)

 Set up virtual environment and install dependencies (fastapi, sqlalchemy, alembic, pydantic, python-dotenv, langgraph, langchain, chromadb)
 Create backend folder structure
 Implement Core Configuration (
core/config.py
, core/security.py)
 Implement Database Setup (db/session.py,
db/base.py
)
 Implement Models (
models/user.py
,
models/role.py
,
models/db_connection.py
)
 Setup Alembic and run initial migration
 Implement Auth Skeleton (
api/auth.py
,
auth/jwt.py
,
auth/dependencies.py
)
 Implement RBAC Middleware Stub
 Implement AI Pipeline Stub (LangGraph)
 Create
main.py
 entry point
 Frontend Setup (Next.js)

 Initialize Next.js app (npm create next-app)
 Install dependencies (shadcn/ui, zustand, next-auth, monaco-editor)
 Configure Tailwind and Components
 Implement Auth Pages (
app/login/page.tsx
)
 Implement Dashboard Shell (
app/dashboard/page.tsx
,
components/Navbar.tsx
)
 Implement Editor Shell with Monaco (
app/editor/page.tsx
,
components/Editor.tsx
)
 Wire up API Client (
lib/api.ts
)
 Verification

 Verify Backend starts and exposes OpenAPI docs
 Verify Frontend starts and renders Login/Dashboard
 Verify basic Auth flow (signup/login dummy)
 Verify AI Stub endpoint
Phase 1: Schema Intelligence & Read-Only NL → SQL
 Dependencies & Config

 Update
requirements.txt
 (LLM providers, SQL parsing)
 Update
config.py
 (LLM settings, Vector DB settings)
 Schema Ingestion Engine

 Create
SchemaMetadata
 model (
models/schema.py
)
 Implement introspection service (
schema_ingestion/inspector.py
)
 Implement textifier for RAG (
schema_ingestion/textifier.py
)
 Create /schema/ingest endpoint
 RAG & Vector Storage

 Implement Vector Store service (ChromaDB)
 Implement Embedding service (Switchable: OpenAI/Ollama)
 Index schema metadata endpoint
 AI & NL-to-SQL Pipeline

 Implement LLM Factory (Ollama, OpenAI, Claude, Gemini)
 Update LangGraph (
ai/graph.py
) with real nodes
 Implement
intent_classifier
 node
 Implement
schema_retriever
 node
 Implement
sql_generator
 node (SELECT only)
 Guardrails & Execution

 Implement sql_guardrails (SQLGlot validation)
 Implement query_executor (Read-only execution)
 Create /query/nl endpoint
 Frontend Updates

 Update
api.ts
 for new endpoints
 Create
ResultTable
 component
 Update
Editor
 page with Chat/Run flow
 Update
Editor
 page with Chat/Run flow
Phase 2: Role-Aware Writes & Governance
 Data Models & Database

 Create
ActionAudit
 model (Audit Logs)
 Create
QueryApproval
 model (Approval Workflow)
 Run Alembic migrations (MySQL Verified)
 RBAC & Permissions

 Implement
rbac/permissions.py
 (Rule definitions)
 Implement
rbac/evaluator.py
 (Enforcement logic)
 Update
intent_classifier
 to support WRITE vs READ
 Implement write_intent_classifier node (Granular write types)
 AI Pipeline Enhancements

 Implement
impact_analyzer
 node (Pre-execution analysis)
 Implement
sql_explainer
 node (Explainability)
 Update query_executor for transactional Writes
 Update LangGraph to route READ vs WRITE vs APPROVAL
 Advanced Database Connections

 Update
DBConnection
 model (fields, encryption support)
 Implement credential_encryptor service
 Implement db_connector service (Test Connection)
 Update POST /db_connections API
 Update
AddConnectionModal
 UI
 Approval Workflow API

 Create /approvals/ endpoints (List, Approve, Reject)
 Integrate Approval check in Query Pipeline
 Frontend & UI (Transitional)

 Create
ImpactSummary
 component
 Create
ApprovalRequest
 dialog/view
 Create QueryHistory / Audit Log page
 Update
Editor
 to handle "Approval Required" state
Phase 3: Advanced Web IDE & Visualization
 Database Schema Explorer

 Backend: Create /schema/{connection_id}/structure endpoint
 Backend: Implement schema introspection for MySQL
 Backend: Implement schema introspection for PostgreSQL
 Frontend: Create
SchemaExplorer
 component
 Frontend: Integrate explorer into Editor sidebar
 Frontend Architecture

 Create
Workspace
 logic (Zustand stores: workspaceStore, queryStore)
 Implement IDE Layout (Sidebar, Editor Zone, Output Zone)
[/] IDE Components

 Create
ChatPanel
 (Conversational UI)
 Upgrade SqlEditor (Diff view, warnings)
 Create
ExplainabilityPanel
 (Collapsible explanation/risk)
 Visualization & Analytics

 Install Recharts
 Implement ChartSuggestionEngine logic
 Create ChartBuilder UI
 Create Chart Components (Bar, Line, Pie, Area)
 Query Lifecycle & Governance

 Implement Query State Machine (Draft -> Approved -> Executed)
 Create QueryStatusTimeline component
 Create AdminApprovalConsole page
 Create QuerySnapshot view
 Schema Exploration

 Create /schema page (Browser)
 Visualize table relationships
Phase 3.5: User Controls
 AI Model Selection
 Backend: Update User model with LLM fields
 Backend: Create User Settings API
 Backend: Update LLM Factory for dynamic config
 Frontend: Create AI Model Selection Page
 Frontend: Integrate into Navigation

Excellent — let’s **lock this down into an implementable, best-practice solution**, not just theory.

Below is a **clear diagnosis → best solution → exact implementation plan** that you can apply directly to your existing codebase **without rewriting everything**.

I’ll keep this practical and structured so you can move straight to coding.

---

## 1. Restating the Core Problem (Precisely)

Your current system does this:

```
User question
 → Embed question
 → Retrieve schema chunks (many tables)
 → LLM guesses tables/joins
 → SQL is valid but semantically wrong
```

This fails when:
• Database has many tables  
• Multiple tables look semantically similar  
• User question is vague (“sales”, “customers”, “revenue”)  

**RAG alone is NOT enough** for NL→SQL on large schemas.

---

## 2. The Best Industry-Grade Solution (Short Answer)

> **Never allow the LLM to directly choose tables from the full schema.**

Instead, enforce a **multi-stage narrowing + validation pipeline**:

```
Question
 → Table candidates (Top-K)
 → Relevance scoring
 → Ambiguity detection
 → (Ask user if needed)
 → Column grounding
 → SQL generation with locked schema
 → Validation + repair
```

This is the **same principle used by**:
• Snowflake Copilot–style systems  
• Enterprise BI copilots  
• Internal tools at scale  

---

## 3. The “Best” Concrete Solution (What You Should Implement)

### ✅ Solution Name (Mental Model)

**Schema-Locked, Disambiguation-First NL→SQL Pipeline**

This has **4 mandatory safeguards**.

---

## 4. Safeguard #1 — Two-Stage Table Selection (MOST IMPORTANT)

### What You Do NOW (Minimal Change)

Instead of this:

```
schema_retriever → sql_generator
```

You change it to:

```
schema_retriever → table_selector → sql_generator
```

---

### Stage 1: Candidate Retrieval (Fast, Embedding-Based)

**Goal**: Narrow 100+ tables → 5–8 tables

Implementation:
• Use your existing ChromaDB
• Retrieve top-K tables only (K=5–8)
• Do NOT include columns yet

Code impact:

```
ai/nodes/table_candidate_retriever.py
```

Output:

```json
[
  {"table": "orders", "score": 0.81},
  {"table": "customer_orders", "score": 0.79},
  {"table": "billing_transactions", "score": 0.63}
]
```

---

### Stage 2: Relevance Scoring (LLM, but constrained)

**Prompt idea (critical)**:
> “From the following tables, choose which are strictly required to answer the question.  
> Return a ranked list and reasoning.”

LLM does **ranking**, not free selection.

Output:

```json
{
  "selected_tables": ["orders", "customers"],
  "confidence": 0.87
}
```

---

## 5. Safeguard #2 — Ambiguity Detection (Stops Guessing)

### When to Trigger Ambiguity

If **any** of these are true:
• Top-2 table scores are close  
• More than 2 tables selected  
• Required metric appears in multiple tables  

Then:
❌ Do NOT generate SQL  
✅ Ask the user

---

### What You Ask the User (UI)

Example:

```
I found multiple relevant tables for "revenue":

1) orders – transactional sales
2) billing_transactions – payment records

Which one should I use?
```

Frontend component:

```
<TableDisambiguationDialog />
```

Backend node:

```
ai/nodes/ambiguity_detector.py
```

This **alone** will remove 60–70% wrong queries.

---

## 6. Safeguard #3 — Column-Level Grounding (Precision)

### Why This Matters

Even with correct tables, LLM may:
• Pick wrong column
• Use deprecated field
• Use similar-named metric

---

### Best Practice

Before SQL generation:

1. Extract **columns only from selected tables**
2. Ask LLM:
   > “Which columns are required to answer this question?”

Lock allowed columns.

Implementation:

```
ai/nodes/column_grounder.py
```

Allowed input to SQL generator:

```json
{
  "tables": ["orders"],
  "columns": ["order_date", "amount", "customer_id"]
}
```

LLM **cannot invent anything else**.

---

## 7. Safeguard #4 — Schema-Locked SQL Generation + Repair

### Rule (Non-Negotiable)

> LLM must generate SQL **only using a whitelist** of tables & columns.

Enforce with:
• SQLGlot parse
• Schema validation
• Automatic repair loop

Implementation:

```
ai/nodes/sql_repair_agent.py
```

Flow:

```
Generate SQL
 → Validate
 → If invalid → regenerate with error context
 → Max 2 attempts
```

No silent failures.

---

## 8. The “Best” Prompting Strategy (You Should Use This)

### SQL Generator Prompt (Core)

Key rules to include:
• Use only provided tables and columns
• Do not assume missing fields
• If information is insufficient, say so
• Always include LIMIT
• Never use SELECT *

This dramatically improves correctness.

---

## 9. Confidence Scoring (Simple but Powerful)

### How to Compute Confidence (Practical)

Combine:
• Table relevance score
• Ambiguity resolved or not
• SQL validation passes
• Column match ratio

Return:

```json
{
  "confidence_score": 0.92
}
```

Frontend:
• Green ≥ 0.8  
• Yellow 0.6–0.8  
• Red < 0.6  

This helps users trust or question results.

---

## 10. Minimal Changes You Need to Make (Actionable)

### Backend (Add These Only)

You **do NOT rewrite everything**.

Add:

```
ai/nodes/
├── table_candidate_retriever.py
├── table_relevance_scorer.py
├── ambiguity_detector.py
├── column_grounder.py
├── sql_repair_agent.py
```

Update:

```
ai/graph.py
```

---

### Frontend (Small but Important)

Add:

```
<TableDisambiguationDialog />
<ConfidenceIndicator />
```

Everything else stays.

---

## 11. Why This Is the BEST Solution (Not Just One Solution)

This approach:
• Scales to 500+ tables  
• Avoids hallucination  
• Makes AI ask for help when needed  
• Matches enterprise NL→SQL systems  
• Preserves your existing RAG investment  

You are **not abandoning RAG** —  
you are **controlling it**.

---

## 12. Final Recommendation (Very Important)

Do **not** try to:
❌ Fine-tune first  
❌ Add more embeddings  
❌ Increase context window  

Those **do not solve ambiguity**.

Control > Context.

---

## What I Can Do Next (Very Concrete)

Choose one and I’ll go **code-level deep**:

1️⃣ Exact **LangGraph node wiring code**  
2️⃣ Production-ready **prompt templates**  
3️⃣ SQL validation & repair **implementation**  
4️⃣ Debug your **current failing queries step-by-step**  

Say the number — we move straight to implementation.
