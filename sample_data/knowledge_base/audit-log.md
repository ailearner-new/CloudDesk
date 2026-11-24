---
title: "Audit Log Guide"
category: "security"
tags: ["audit", "logging", "compliance", "monitoring", "siem"]
summary: "Understand CloudDesk's audit logging: what's captured, how to access, retention, and SIEM integration."
---

# Audit Log Guide

## What's Logged

### Authentication Events
- User login (success/failure)
- MFA challenges (success/failure)
- SSO assertions (success/failure)
- Token refresh
- Logout (explicit and timeout)

### Authorization Events
- Role grants and revocations
- Workspace membership changes
- Permission changes on files/folders
- API key creation/rotation/revocation

### Data Access Events
- File downloads (bulk and individual)
- Data exports (account, workspace)
- Report generation
- Search queries (Enterprise)

### Configuration Events
- Workspace settings changes
- Integration connect/disconnect
- Webhook create/update/delete
- Billing plan changes
- Security policy updates

### Administrative Events
- User invite/remove
- Workspace create/delete
- Retention policy changes
- DLP rule changes
- Custom domain changes

## Accessing Audit Logs

### Web Dashboard
Admin → Audit Log
- Filter by: date range, user, action, resource type, outcome
- Search: free text across all fields
- Export: CSV (max 10,000 rows), JSON (max 5,000 rows)

### API Access
```bash
GET /api/v1/audit?user_id=...&action=login&start=2026-01-01&end=2026-01-31
```

Response:
```json
{
  "items": [
    {
      "id": "audit-123",
      "timestamp": "2026-01-15T09:30:00Z",
      "actor": { "id": "user-456", "email": "sam@clouddesk.com", "role": "admin" },
      "action": "login",
      "resource": { "type": "session", "id": "sess-789" },
      "outcome": "success",
      "ip": "203.0.113.42",
      "user_agent": "Mozilla/5.0...",
      "details": { "mfa_method": "totp" }
    }
  ],
  "page": 1,
  "page_size": 50,
  "total": 1247
}
```

## Retention by Plan

| Plan | Retention | Export Limit |
|------|-----------|--------------|
| Free | 30 days | 1,000 rows |
| Pro | 90 days | 5,000 rows |
| Business | 1 year | 10,000 rows |
| Enterprise | 7 years | Unlimited |

## SIEM Integration (Enterprise)

### Webhook Delivery
- Endpoint: `POST https://your-siem.com/clouddesk-audit`
- Headers: `X-CloudDesk-Signature`, `Content-Type: application/json`
- Batch: every 5 minutes or 1,000 events (whichever first)
- Retry: exponential backoff (1m, 2m, 4m, 8m, 16m, max 24h)

### Payload Format
```json
{
  "batch_id": "batch-abc123",
  "timestamp": "2026-01-15T09:35:00Z",
  "events": [
    { "id": "...", "timestamp": "...", "actor": {...}, "action": "...", ... }
  ]
}
```

### Signature Verification
```python
import hmac, hashlib

def verify(payload, signature, secret):
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Tested SIEMs
- Splunk (HTTP Event Collector)
- Datadog (Log Intake API)
- Elastic (Fleet/Elastic Agent)
- Microsoft Sentinel (Log Analytics)
- Sumo Logic (HTTP Source)
- Custom (any HTTPS endpoint)

## Common Queries

### "Who accessed sensitive file X?"
```
action:file_download AND resource.id:file-xyz
```

### "Failed logins for user Y"
```
actor.email:user-y AND action:login AND outcome:failure
```

### "Admin actions in last 24h"
```
actor.role:admin AND timestamp:>now-24h
```

### "Bulk exports this month"
```
action:data_export AND timestamp:>start-of-month
```

## Alerting (Enterprise)

### Built-In Alerts
- 10+ failed logins in 5 minutes (brute force)
- Impossible travel (logins from distant locations < 1 hour)
- Mass download (> 100 files in 10 minutes)
- New admin role granted
- DLP rule triggered

### Custom Alerts
Admin → Security → Alert Rules → Create
- Name, description
- Query (same syntax as search)
- Threshold: count/time window
- Channels: email, Slack, webhook, PagerDuty

## Compliance Use

### SOC 2 Evidence
- Audit logs = CC7.2 (system monitoring)
- Retention = CC7.3 (incident response)
- Alerting = CC7.4 (anomalous activity)

### GDPR Article 30
- Data access logs = processing activities record
- Export logs = data portability evidence
- Deletion logs = right to erasure evidence

## Troubleshooting

### "Logs missing"
- Check retention period for plan
- Verify time range (UTC)
- Confirm permissions (admin only)

### "Webhook failing"
- Check endpoint returns 2xx within 10s
- Verify signature secret matches
- Check firewall allows CloudDesk IPs

### "Export truncated"
- Free/Pro/Business have row limits
- Use API with pagination for full dataset
- Enterprise: no limits

## Related Articles
- [Enterprise Security Configuration](enterprise-security.md)
- [Security Best Practices](security-best-practices.md)
- [Account Deletion](account-deletion.md)
- [Data Loss Prevention](enterprise-security.md#data-loss-prevention-dlp)