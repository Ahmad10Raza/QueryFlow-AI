Alright — **Phase 2** is where your system stops being “just a smart reader” and becomes a **controlled, enterprise-grade decision-maker**.

Phase 2 builds **role-aware intelligence, write operations, approvals, and explainability** on top of the solid Phase 1 foundation.

I’ll keep the same engineering depth and structure.

---

# PHASE 2 — Role-Aware Writes, Permissions & Governance

## Goal of Phase 2

By the end of Phase 2, the system must:

• Support **UPDATE / DELETE** queries
• Enforce **role-based permissions at SQL level**
• Prevent destructive or unsafe operations
• Introduce **approval workflows** (Manager/Admin)
• Explain **what the query will do before execution**
• Maintain full **auditability and traceability**

This is where your app becomes **enterprise-safe AI**, not a chatbot.

---

## Phase 2 Entry Preconditions

✔ Phase 1 fully complete
✔ NL → SELECT pipeline stable
✔ Schema RAG working
✔ SQL validation enforced
✔ Query execution safe

If SELECT queries are not rock-solid, **do not start Phase 2**.

---

## PHASE 2 — HIGH-LEVEL EXPANSION

```
User Intent
   ↓
Role Detection
   ↓
Write Intent Detection
   ↓
Impact Analysis
   ↓
Permission Enforcement
   ↓
Approval (if needed)
   ↓
Safe Execution
   ↓
Audit & Explainability
```

---

## 2.1 Write-Intent Detection (Critical)

### Objective

Detect **what kind of operation** the user is requesting *before* generating SQL.

---

### New LangGraph Node

```
app/ai/nodes/write_intent_classifier.py
```

---

### Intent Categories

```
READ_ONLY
UPDATE_SINGLE_TABLE
UPDATE_MULTI_TABLE
DELETE_RESTRICTED
DELETE_HIGH_RISK
```

---

### Example

User asks:

```
"Update the salary of employees in sales department by 10%"
```

System classifies:

```
Intent = UPDATE_MULTI_TABLE
Risk = MEDIUM
```

This classification happens **before SQL generation**.

---

## 2.2 Role-Based Permission Matrix (Hard Enforcement)

### Objective

Prevent AI from executing what the **user role is not allowed to do**.

---

### Permission Rules

| Role    | SELECT | UPDATE          | DELETE |
| ------- | ------ | --------------- | ------ |
| User    | ✅      | ❌               | ❌      |
| Manager | ✅      | ⚠️ (restricted) | ❌      |
| Admin   | ✅      | ✅               | ✅      |

---

### New Module

```
app/rbac/
├── permissions.py
├── evaluator.py
├── policies.py
```

---

### Enforcement Happens In Two Places

1. **Before SQL generation**
2. **After SQL parsing (final gate)**

Even if LLM hallucinates, execution is blocked.

---

## 2.3 Write-SQL Generation (Controlled)

### Objective

Allow AI to generate **UPDATE / DELETE**, but under strict constraints.

---

### LangGraph Expansion

```
READ → existing path
WRITE → new guarded path
```

---

### SQL Generation Rules (Phase 2)

• Single-table UPDATE preferred
• Explicit WHERE clause required
• LIMIT required where supported
• No subqueries (yet)
• No cascading deletes

---

### Example Allowed SQL

```
UPDATE employees
SET salary = salary * 1.1
WHERE department = 'Sales'
LIMIT 50;
```

---

## 2.4 Impact Analysis Node (Enterprise Feature)

### Objective

Show **what will change** before execution.

---

### New Node

```
app/ai/nodes/impact_analyzer.py
```

---

### What It Does

• Converts UPDATE/DELETE into a SELECT preview
• Estimates affected rows
• Lists affected tables & columns

---

### Example Output

```
Impact Summary:
- Table: employees
- Rows affected: ~42
- Columns modified: salary
```

This is sent to UI **before execution**.

---

## 2.5 Approval Workflow (Manager → Admin)

### Objective

Introduce **human-in-the-loop** safety.

---

### Approval Rules

• Manager UPDATE → Admin approval
• DELETE → Always Admin approval
• Bulk UPDATE → Approval required

---

### New Database Tables

```
query_approvals
- id
- query_id
- requested_by
- approved_by
- status (PENDING / APPROVED / REJECTED)
- created_at
```

---

### Flow

```
Manager submits write query
   ↓
Stored as PENDING
   ↓
Admin reviews
   ↓
Approve / Reject
```

AI **cannot bypass** this.

---

## 2.6 Write Query Execution Engine

### Objective

Safely execute approved write queries.

---

### Enhancements to Executor

```
app/query_executor/
├── write_executor.py
├── transaction_manager.py
```

---

### Execution Safeguards

• Transaction-based execution
• Auto rollback on error
• Timeout enforced
• Affected-row limit enforced

---

## 2.7 Explainability Layer (Mandatory for Trust)

### Objective

Explain **why this SQL was generated**.

---

### New Module

```
app/ai/explanations/
├── sql_explainer.py
```

---

### UI Output Example

```
"This query updates employee salaries by 10% for the Sales department as requested. 
It modifies the salary column in the employees table for records matching department='Sales'."
```

This builds **user trust**.

---

## 2.8 Frontend Enhancements (Phase 2)

### New UI Components

```
frontend/components/
├── ImpactSummary.tsx
├── ApprovalDialog.tsx
├── QueryHistory.tsx
```

---

### UI Flow (Write Query)

1. User enters NLP query
2. AI generates SQL
3. Impact summary shown
4. Approval requested (if needed)
5. Execution button enabled only after approval

---

## 2.9 Audit & Compliance Logging (Expanded)

### Objective

Full traceability for every write.

---

### Log Everything

• Original NLP prompt
• Generated SQL
• User role
• Approval chain
• Execution result
• Rows affected

Stored in:

```
audit_logs
```

---

## Phase 2 Completion Criteria

You are **done with Phase 2 only if**:

✔ UPDATE / DELETE supported
✔ Role-based enforcement cannot be bypassed
✔ Approval workflow works end-to-end
✔ Impact analysis shown before execution
✔ Full audit trail exists
✔ Accidental destructive queries are impossible

---

## What Phase 2 Still Does NOT Do

❌ Multi-step reasoning
❌ Complex joins across DBs
❌ Query optimization
❌ Auto rollback suggestions
❌ Business KPI reasoning

Those belong to **Phase 3**.

---

### When You’re Ready

When you say **“Give Phase 3”**, we’ll move into:

• Multi-step LangGraph reasoning
• Complex analytical queries
• Query optimization & rewriting
• Caching & performance intelligence

You’re now building something **very few teams get right**.
