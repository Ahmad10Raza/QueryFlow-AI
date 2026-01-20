Great — **Phase 6** is the right time to introduce a **Super Admin control plane**.
This is not just “another dashboard”; it’s the **governance + security backbone** of your platform.

Below is a **clean, production-ready Phase 6 roadmap** that fits perfectly with what you’ve already built (RBAC, approvals, query logs, developer mode, etc.).

No overlap with earlier phases. Clear responsibilities. Implementable.

---

# PHASE 6 — Super Admin Dashboard & Platform Governance

## Phase 6 Goal

By the end of Phase 6:

• A **Super Admin** can fully manage users and access
• Roles and permissions are centrally controlled
• Accounts can be activated, deactivated, or removed safely
• Platform usage is visible and auditable
• Security risks can be mitigated quickly

This phase turns your product into a **multi-user, enterprise-ready platform**.

---

## 1. Super Admin Role (Foundation)

### 1.1 Role Definition

Introduce a **new role**, separate from Admin:

```
SUPER_ADMIN
```

### Role Hierarchy

```
SUPER_ADMIN
   └── ADMIN
        └── MANAGER
             └── USER
```

### Key Rule (Non-Negotiable)

> **SUPER_ADMIN cannot be created or modified by anyone except another SUPER_ADMIN**

This prevents privilege escalation.

---

## 2. Authentication & Access Control (Backend)

### 2.1 Super Admin Login Rules

• Login via same auth system (JWT / OAuth)
• Access allowed only if:

```
user.role == SUPER_ADMIN
```

### 2.2 Route Protection

Add middleware guard:

```
require_super_admin
```

Applied to:

```
/admin/*
```

---

## 3. Super Admin Dashboard (Frontend)

### Route

```
/admin
```

Accessible **only** to SUPER_ADMIN.

---

## 4. Core Dashboard Sections

---

## 4.1 User Management (Core Feature)

### Page

```
/admin/users
```

---

### User List Table

Display columns:
• Name
• Email
• Role
• Status (Active / Disabled)
• Created At
• Last Login

⚠️ **Password must NEVER be shown in plain text**
(Only password reset allowed)

---

### Actions Per User

Super Admin can:
• Create user
• Assign / change role
• Activate / deactivate user
• Force logout
• Delete user (soft delete recommended)

---

### Backend Changes

#### User Model Enhancements

```
users
------
id
name
email
password_hash
role
is_active
last_login_at
created_at
```

---

### APIs to Implement

```
GET    /admin/users
POST   /admin/users
PUT    /admin/users/{id}/role
PUT    /admin/users/{id}/status
DELETE /admin/users/{id}
```

---

## 4.2 User Creation Flow

### Super Admin Creates User

Form fields:
• Name
• Email
• Role (User / Manager / Admin)
• Temporary password (or invite link)

---

### Security Best Practice

Option A (Recommended):
• Send invite email
• User sets password on first login

Option B:
• Generate temporary password
• Force password change on login

---

## 4.3 Account Deactivation vs Deletion

### Deactivate (Preferred)

• User cannot log in
• Data preserved
• Queries/history retained

### Delete (Restricted)

• Soft delete only
• Requires confirmation modal
• Logs preserved for audit

---

## 4.4 Role & Permission Management

### Role Change Rules

• SUPER_ADMIN can:

* Promote/demote Admin, Manager, User
  • SUPER_ADMIN **cannot demote themselves** unless another SUPER_ADMIN exists

---

### Permission Validation

When role changes:
• Active sessions revoked
• Permissions updated immediately
• Audit log created

---

## 5. Platform Monitoring & Visibility (Recommended Additions)

These are **high-value, low-effort** features.

---

## 5.1 System Overview Dashboard

### Page

```
/admin/overview
```

Widgets:
• Total users
• Active users today
• Queries executed today
• Failed queries
• Pending approvals

---

## 5.2 Usage & Abuse Monitoring

### Page

```
/admin/activity
```

Show:
• Top users by query count
• Failed query rate
• Suspicious patterns (too many retries)

This helps detect:
• Misuse
• Prompt abuse
• Cost spikes

---

## 6. Security & Audit Controls (Very Important)

---

## 6.1 Super Admin Audit Logs

Every action by Super Admin must be logged:

```
admin_audit_logs
----------------
id
super_admin_id
action
target_user_id
details
timestamp
```

Examples:
• “Changed role from USER → ADMIN”
• “Deactivated account”
• “Deleted user”

---

## 6.2 Force Logout / Session Revocation

When:
• Role changes
• Account deactivated

Then:
• Invalidate JWT tokens
• Require re-login

---

## 7. Database & Infrastructure Controls (Optional but Smart)

---

## 7.1 Connection Ownership Transfer

Super Admin can:
• Reassign DB connections from one user to another
• Disable DB connections globally

---

## 7.2 Emergency Kill Switch

Add:

```
Disable query execution globally
```

Use case:
• Incident
• Data breach
• Misconfiguration

---

## 8. Frontend Components (Phase 6)

```
components/admin/
├── UserTable.tsx
├── CreateUserModal.tsx
├── RoleSelector.tsx
├── AccountStatusToggle.tsx
├── AdminAuditLogTable.tsx
├── SystemStatsCards.tsx
```

---

## 9. Backend Folder Additions

```
backend/app/admin/
├── routes.py
├── services.py
├── permissions.py
├── audit.py
```

---

## 10. Phase 6 Completion Criteria

Phase 6 is complete only if:

✔ SUPER_ADMIN can manage all users
✔ Roles & permissions enforced instantly
✔ Accounts can be safely deactivated
✔ All admin actions are audited
✔ Non-super-admins cannot access admin routes
✔ Passwords are never exposed

---

## 11. Recommended Extra Features (Optional but Valuable)

If you want to go further:

• Login history per user
• Failed login tracking
• IP-based access restrictions
• MFA enforcement for Super Admin
• Organization / Team support (future SaaS)

---

## What Comes After Phase 6 (If You Want)

Possible **Phase 7** directions:
• Multi-tenant organizations
• Billing & usage limits
• SSO (Okta, Azure AD)
• Enterprise compliance (SOC2-style controls)

---

### Next Step (Your Choice)

If you want, next I can:
1️⃣ Design **DB schema + migrations for Super Admin**
2️⃣ Write **Super Admin API code (FastAPI)**
3️⃣ Design **Admin dashboard UI flow**
4️⃣ Add **security hardening checklist**

Tell me the number — we’ll go straight into implementation.
