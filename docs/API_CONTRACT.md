# API Contract — CloudDesk Support Platform

Source of truth for every route and type. If an endpoint changes, update this file, `backend/app/schemas/`, and `frontend/lib/types.ts` in the same change.

---

## Conventions

- Base path: `/api/v1`
- Auth: `Authorization: Bearer <JWT>` (Supabase-compatible HS256)
- Request ID: `X-Request-ID` on every response (echoed or generated)
- Errors: `{ "detail": "string" }` with proper HTTP status
- Content-Type: `application/json`
- Pagination: `?page=1&page_size=20` (default 20, max 100)
- Cursor pagination where noted: `?cursor=<opaque>&limit=20`

---

## Health (unprefixed)

### `GET /health`
```json
{ "status": "ok", "service": "clouddesk-support", "version": "0.1.0" }
```

### `GET /health/live`
No I/O. Used by liveness probes.
```json
{ "status": "alive" }
```

### `GET /health/ready`
Checks DB, Redis, vector store, LLM client.
```json
{ "status": "ready", "checks": { "database": true, "redis": true, "vector_store": true, "llm": true } }
```
Returns 503 if any check fails.

---

## Auth

### `POST /api/v1/auth/login`
```json
// Request
{ "email": "sam.agent@clouddesk.demo", "password": "demo" }

// Response (200)
{ "access_token": "eyJ...", "token_type": "bearer", "expires_in": 28800, "user": { "id": "...", "email": "...", "role": "agent" } }
```

### `POST /api/v1/auth/refresh`
```json
// Request (Authorization header required)
{}

// Response (200)
{ "access_token": "eyJ...", "token_type": "bearer", "expires_in": 28800 }
```

### `GET /api/v1/auth/me`
```json
// Response (200)
{ "id": "...", "email": "sam.agent@clouddesk.demo", "role": "agent", "full_name": "Sam Agent" }
```

---

## Tickets

### `POST /api/v1/tickets`
Create a ticket from email, chat, web, or API.
```json
// Request
{
  "subject": "SSO login fails for whole team",
  "body": "Since 09:00 UTC the entire engineering team cannot log in via SSO...",
  "channel": "email",
  "customer_email": "cto@acmecorp.demo"
}

// Response (201)
{
  "id": "cd-1001",
  "subject": "SSO login fails for whole team",
  "body": "...",
  "channel": "email",
  "status": "new",
  "severity": null,
  "category": null,
  "customer_id": "cust-acme-001",
  "assignee_id": null,
  "created_at": "2026-01-15T09:05:00Z",
  "updated_at": "2026-01-15T09:05:00Z"
}
```

### `GET /api/v1/tickets`
List tickets with filters.
```
Query: ?status=new&severity=high&category=login_issue&assignee_id=...&page=1&page_size=20
```

```json
// Response (200)
{
  "items": [ { "id": "...", "subject": "...", "status": "...", "severity": "...", "category": "...", "customer_id": "...", "created_at": "...", "updated_at": "..." } ],
  "page": 1,
  "page_size": 20,
  "total": 13
}
```

### `GET /api/v1/tickets/{id}`
Get ticket by ID (`cd-1001`) or display ID (`CD-1001`).
```json
// Response (200)
{
  "id": "cd-1001",
  "subject": "...",
  "body": "...",
  "channel": "email",
  "status": "in_progress",
  "severity": "critical",
  "category": "login_issue",
  "customer_id": "cust-acme-001",
  "assignee_id": "user-sam-agent",
  "created_at": "2026-01-15T09:05:00Z",
  "updated_at": "2026-01-15T09:45:00Z",
  "customer": { "id": "...", "name": "Acme Corp", "plan": "enterprise", "email": "cto@acmecorp.demo" }
}
```

### `PATCH /api/v1/tickets/{id}`
Update ticket (agent/admin only).
```json
// Request
{ "status": "waiting_on_customer", "assignee_id": "user-sam-agent", "severity": "high", "category": "login_issue" }

// Response (200) — full ticket object
```

### `POST /api/v1/tickets/{id}/run`
Start an AI workflow run. Returns 202 immediately.
```json
// Response (202)
{ "workflow_id": "wf-abc123", "status": "running" }
```
Errors:
- 409 if ticket status is `waiting_on_approval`
- 409 if a run is already `running` for this ticket

### `GET /api/v1/tickets/{id}/workflow`
Poll for workflow progress (every 2s).
```json
// Response (200)
{
  "workflow_id": "wf-abc123",
  "status": "running",
  "current_node": "troubleshooting",
  "completed_nodes": ["understand_ticket", "classify_severity", "customer_context", "knowledge_retrieval"],
  "classification": { "category": "login_issue", "summary": "Enterprise SSO outage affecting all engineers", "confidence": 0.94 },
  "severity": { "level": "critical", "reason": "Enterprise customer, all users blocked, active incident" },
  "customer_context": { "customer": {...}, "subscription": {...}, "workspace": {...}, "previous_tickets": [...], "memory_notes": [...] },
  "evidence": [ { "id": "...", "title": "SSO Troubleshooting Guide", "source": "kb://sso-troubleshooting#diagnosis", "snippet": "...", "score": 0.87, "url": "/knowledge/art-001", "article_id": "art-001" } ],
  "similar_cases": [ { "ticket_id": "cd-0987", "title": "SAML cert rotation", "resolution_summary": "Rotated IdP certificate", "similarity": 0.82 } ],
  "diagnosis": { "probable_causes": ["IdP certificate expired", "Clock skew > 5 min"], "steps": ["Verify IdP cert expiry", "Check clock sync", "Test with SP-initiated flow"] },
  "resolution_plan": { "summary": "Rotate IdP certificate and verify clock sync", "customer_reply": "We've identified the root cause...", "internal_notes": "Cert expires 2026-01-16. Coordinate with Acme infra team.", "actions": [ { "tool": "update_ticket", "args": { "status": "waiting_on_customer" } } ], "grounding_score": 0.91 },
  "risk_level": "low",
  "approval_request_id": null,
  "escalation": null,
  "summary": null,
  "memory_updated": false,
  "error": null
}
```

### `GET /api/v1/tickets/{id}/events`
Inspectable event trace for the run.
```
Query: ?workflow_id=wf-abc123
```

```json
// Response (200)
{
  "items": [
    { "id": "evt-1", "workflow_id": "wf-abc123", "event_type": "node_started", "node": "understand_ticket", "timestamp": "2026-01-15T09:05:01Z", "duration_ms": null, "data": {} },
    { "id": "evt-2", "workflow_id": "wf-abc123", "event_type": "node_completed", "node": "understand_ticket", "timestamp": "2026-01-15T09:05:03Z", "duration_ms": 2100, "data": { "output": { "category": "login_issue", "summary": "..." } } },
    { "id": "evt-3", "workflow_id": "wf-abc123", "event_type": "llm_called", "node": "understand_ticket", "timestamp": "2026-01-15T09:05:02Z", "duration_ms": 1800, "data": { "model": "fake", "input_tokens": 1200, "output_tokens": 200, "cost_usd": 0.0 } }
  ]
}
```

### `POST /api/v1/tickets/{id}/reply`
Send a customer reply (agent/admin only).
```json
// Request
{ "body": "We've identified the root cause...", "internal": false }

// Response (201)
{ "id": "msg-xyz", "ticket_id": "cd-1001", "body": "...", "author_id": "user-sam-agent", "internal": false, "created_at": "2026-01-15T10:00:00Z" }
```

### `POST /api/v1/tickets/{id}/request-info`
Ask customer for more information (agent/admin only).
```json
// Request
{ "body": "Could you share the IdP metadata URL?", "internal": false }

// Response (201) — same as reply, sets ticket status to waiting_on_customer
```

### `POST /api/v1/tickets/{id}/escalate`
Manually escalate (agent/admin only).
```json
// Request
{ "reason": "Requires security team investigation", "team": "security" }

// Response (201)
{ "id": "esc-123", "ticket_id": "cd-1001", "reason": "...", "team": "security", "status": "open", "created_at": "..." }
```

---

## Approvals

### `GET /api/v1/approvals`
List approval requests (paginated).
```
Query: ?status=pending&page=1&page_size=20
```

```json
// Response (200)
{
  "items": [
    {
      "id": "appr-123",
      "workflow_id": "wf-abc123",
      "ticket_id": "cd-1002",
      "tool_name": "create_refund_request",
      "tool_args": { "amount_cents": 15000, "reason": "Overcharge for 3 unused seats" },
      "status": "pending",
      "requested_at": "2026-01-15T09:30:00Z",
      "decided_at": null,
      "decided_by": null
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

### `GET /api/v1/approvals/{id}`
```json
// Response (200) — single approval request
```

### `POST /api/v1/approvals/{id}/approve`
```json
// Request
{}

// Response (200)
{ "id": "appr-123", "status": "approved", "decided_at": "2026-01-15T09:35:00Z", "decided_by": "user-sam-agent" }
```
Errors:
- 409 if already decided
- 403 if viewer

### `POST /api/v1/approvals/{id}/reject`
```json
// Request
{ "reason": "Amount exceeds policy limit" }

// Response (200)
{ "id": "appr-123", "status": "rejected", "decided_at": "...", "decided_by": "...", "reason": "..." }
```

---

## Customers

### `GET /api/v1/customers`
```json
// Response (200)
{
  "items": [ { "id": "cust-acme-001", "name": "Acme Corp", "email": "cto@acmecorp.demo", "plan": "enterprise", "created_at": "..." } ],
  "page": 1,
  "page_size": 20,
  "total": 8
}
```

### `GET /api/v1/customers/{id}`
```json
// Response (200)
{
  "id": "cust-acme-001",
  "name": "Acme Corp",
  "email": "cto@acmecorp.demo",
  "plan": "enterprise",
  "subscription": { "id": "sub-001", "plan": "enterprise", "seats": 50, "status": "active", "renewal_at": "2026-12-01T00:00:00Z" },
  "workspaces": [ { "id": "ws-001", "name": "Engineering", "storage_gb_used": 450, "storage_gb_limit": 1000 } ],
  "memory_notes": [ { "id": "mem-1", "type": "past_issue", "content": "SSO cert rotated 2025-11", "created_at": "..." } ],
  "tickets": [ { "id": "cd-1001", "subject": "...", "status": "in_progress", "severity": "critical", "created_at": "..." } ]
}
```

---

## Knowledge

### `GET /api/v1/knowledge/articles`
```json
// Response (200)
{
  "items": [ { "id": "art-001", "title": "SSO Troubleshooting Guide", "category": "login_issue", "tags": ["sso", "saml"], "summary": "Diagnose and fix SSO login failures", "updated_at": "..." } ],
  "page": 1,
  "page_size": 20,
  "total": 15
}
```

### `GET /api/v1/knowledge/articles/{id}`
```json
// Response (200)
{
  "id": "art-001",
  "title": "SSO Troubleshooting Guide",
  "category": "login_issue",
  "tags": ["sso", "saml"],
  "summary": "...",
  "content": "# SSO Troubleshooting Guide\n\n## Diagnosis\n...",
  "updated_at": "..."
}
```

### `GET /api/v1/knowledge/search`
Hybrid retrieval (semantic + keyword, reranked).
```
Query: ?q=SSO certificate expired&category=login_issue&mode=hybrid&top_k=5
```

```json
// Response (200)
{
  "query": "SSO certificate expired",
  "mode": "hybrid",
  "results": [
    { "id": "chunk-001", "title": "SSO Troubleshooting Guide", "source": "kb://sso-troubleshooting#diagnosis", "snippet": "Check IdP certificate expiry...", "score": 0.91, "url": "/knowledge/articles/art-001", "article_id": "art-001" }
  ]
}
```

### `POST /api/v1/knowledge/reindex` (admin only)
```json
// Response (200)
{ "indexed": { "chunks": 46, "articles": 15 } }
```

---

## Escalations

### `GET /api/v1/escalations`
```json
// Response (200)
{
  "items": [
    { "id": "esc-123", "ticket_id": "cd-1005", "reason": "Suspicious logins", "team": "security", "status": "open", "created_at": "..." }
  ],
  "page": 1,
  "page_size": 20,
  "total": 3
}
```

### `GET /api/v1/escalations/{id}`
```json
// Response (200)
{ "id": "esc-123", "ticket_id": "cd-1005", "reason": "...", "team": "security", "status": "open", "created_at": "...", "updates": [] }
```

### `PATCH /api/v1/escalations/{id}`
```json
// Request
{ "status": "resolved", "resolution": "False positive, legitimate travel" }

// Response (200) — updated escalation
```

---

## Agents (Workflow Graph Metadata)

### `GET /api/v1/agents`
```json
// Response (200)
{
  "nodes": [
    { "id": "understand_ticket", "label": "Understand Ticket", "description": "Classify and summarize the ticket" },
    { "id": "classify_severity", "label": "Classify Severity", "description": "Assign severity with reason" },
    { "id": "customer_context", "label": "Customer Context", "description": "Load customer, subscription, history, memory" },
    { "id": "knowledge_retrieval", "label": "Knowledge Retrieval", "description": "Find cited evidence and similar cases" },
    { "id": "troubleshooting", "label": "Troubleshooting", "description": "Probable causes and numbered steps" },
    { "id": "resolution_planning", "label": "Resolution Planning", "description": "Summary, reply, notes, and actions" },
    { "id": "risk_check", "label": "Risk Check", "description": "Assess if approval or escalation needed" },
    { "id": "human_approval", "label": "Human Approval", "description": "Pause for approval on consequential actions" },
    { "id": "escalation", "label": "Escalation", "description": "File escalation to named team" },
    { "id": "execute_resolution", "label": "Execute Resolution", "description": "Run approved actions" },
    { "id": "ticket_summary", "label": "Ticket Summary", "description": "Write final summary" },
    { "id": "memory_update", "label": "Memory Update", "description": "Record resolution in customer memory" }
  ],
  "edges": [
    { "from": "understand_ticket", "to": "classify_severity" },
    { "from": "classify_severity", "to": "customer_context" },
    { "from": "customer_context", "to": "knowledge_retrieval" },
    { "from": "knowledge_retrieval", "to": "troubleshooting" },
    { "from": "troubleshooting", "to": "resolution_planning" },
    { "from": "resolution_planning", "to": "risk_check" },
    { "from": "risk_check", "to": "human_approval", "condition": "approval_required" },
    { "from": "risk_check", "to": "escalation", "condition": "escalation_required" },
    { "from": "risk_check", "to": "execute_resolution", "condition": "low_risk" },
    { "from": "human_approval", "to": "execute_resolution", "condition": "approved" },
    { "from": "human_approval", "to": "escalation", "condition": "rejected" },
    { "from": "escalation", "to": "ticket_summary" },
    { "from": "execute_resolution", "to": "ticket_summary" },
    { "from": "ticket_summary", "to": "memory_update" },
    { "from": "memory_update", "to": "END" }
  ]
}
```

---

## Audit

### `GET /api/v1/audit`
```json
// Response (200)
{
  "items": [
    { "id": "audit-1", "user_id": "user-sam-agent", "action": "ticket.run", "resource_type": "ticket", "resource_id": "cd-1001", "details": { "workflow_id": "wf-abc123" }, "ip": "127.0.0.1", "created_at": "2026-01-15T09:05:00Z" }
  ],
  "page": 1,
  "page_size": 50,
  "total": 42
}
```

---

## Settings (admin only)

### `GET /api/v1/settings`
```json
// Response (200)
{
  "approval_required_for_refunds": true,
  "max_refund_without_approval": 0,
  "rate_limit_per_minute": 120,
  "tool_timeout_seconds": 30,
  "vector_store": "memory",
  "embedding_provider": "fake",
  "llm_provider": "fake"
}
```

### `PATCH /api/v1/settings`
```json
// Request
{ "approval_required_for_refunds": false, "rate_limit_per_minute": 60 }

// Response (200) — updated settings
```

---

## MCP Tools (read-only)

### `GET /api/v1/mcp/tools`
```json
// Response (200)
{
  "tools": [
    { "name": "get_customer", "description": "Get customer by ID", "parameters": { "type": "object", "properties": { "customer_id": { "type": "string" } }, "required": ["customer_id"] } },
    { "name": "get_subscription", "description": "Get subscription by customer ID", "parameters": { ... } },
    { "name": "search_docs", "description": "Search knowledge base", "parameters": { ... } }
  ]
}
```

---

## Webhooks (future)

### `POST /api/v1/webhooks/tickets`
Receive ticket events from external systems (not implemented in v1).

---

## Error Responses

| Status | When |
|--------|------|
| 400 | Validation error (Pydantic detail) |
| 401 | Missing or invalid token |
| 403 | Role insufficient (viewer on mutating route) |
| 404 | Resource not found |
| 409 | Conflict (run while waiting_on_approval, double-approve, resume non-paused) |
| 422 | Unprocessable (business rule violation) |
| 429 | Rate limited |
| 500 | Internal error (logged with request_id) |
| 503 | `/health/ready` dependency down |

All error bodies: `{ "detail": "human-readable message" }`

---

## Type Definitions (mirrored in `backend/app/schemas/` and `frontend/lib/types.ts`)

```typescript
// Ticket
type TicketStatus = "new" | "in_progress" | "waiting_on_customer" | "waiting_on_approval" | "escalated" | "resolved" | "closed";
type TicketSeverity = "low" | "medium" | "high" | "critical";
type TicketChannel = "email" | "chat" | "web" | "api";
type TicketCategory = "login_issue" | "billing" | "api_failure" | "workspace_permissions" | "storage_quota" | "integration" | "feature_request" | "account" | "security" | "other";

// Workflow
type WorkflowStatus = "running" | "paused" | "completed" | "failed" | "cancelled";
type RiskLevel = "low" | "medium" | "high";
type ApprovalStatus = "pending" | "approved" | "rejected";

// Customer
type PlanTier = "free" | "pro" | "business" | "enterprise";

// User
type UserRole = "viewer" | "agent" | "admin";

// Escalation
type EscalationStatus = "open" | "in_progress" | "resolved" | "closed";
```