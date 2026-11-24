---
title: "Webhook Configuration"
category: "integration"
tags: ["webhooks", "events", "integration", "real-time", "notifications"]
summary: "Configure webhooks to receive real-time events from CloudDesk: ticket updates, file changes, user activity, and more."
---

# Webhook Configuration

## Event Types

### Ticket Events
| Event | Trigger | Payload |
|-------|---------|---------|
| `ticket.created` | New ticket created | Full ticket object |
| `ticket.updated` | Any field changed | Changed fields + ticket |
| `ticket.status_changed` | Status transition | Old status, new status |
| `ticket.assigned` | Assignee changed | Old assignee, new assignee |
| `ticket.resolved` | Status → resolved | Resolution summary |
| `ticket.closed` | Status → closed | Close reason |
| `ticket.reopened` | Closed → open | Reopen reason |

### File Events
| Event | Trigger |
|-------|---------|
| `file.created` | New file uploaded |
| `file.updated` | File content/metadata changed |
| `file.deleted` | File moved to trash |
| `file.restored` | File restored from trash |
| `file.shared` | Share link created |
| `file.downloaded` | File downloaded (Enterprise) |

### User Events
| Event | Trigger |
|-------|---------|
| `user.invited` | Member invited to workspace |
| `user.joined` | Invitation accepted |
| `user.removed` | Member removed |
| `user.role_changed` | Role updated |

### Workspace Events
| Event | Trigger |
|-------|---------|
| `workspace.created` | New workspace |
| `workspace.updated` | Settings changed |
| `workspace.deleted` | Workspace deleted |
| `workspace.storage_warning` | 90% capacity reached |

## Creating a Webhook

### Via Dashboard
1. Settings → Integrations → Webhooks → Create
2. Enter **Payload URL** (HTTPS required)
3. Select **Events** to subscribe
4. Enter **Secret** (auto-generated if empty)
5. Click **Create** → test delivery sent

### Via API
```bash
POST /api/v1/webhooks
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks/clouddesk",
  "events": ["ticket.created", "ticket.updated", "file.created"],
  "secret": "your-shared-secret"
}
```

## Payload Format

### Delivery
```json
{
  "id": "evt_abc123",
  "type": "ticket.created",
  "timestamp": "2026-01-15T09:30:00Z",
  "workspace_id": "ws-123",
  "data": { ...ticket object... }
}
```

### Signature Verification
Header: `X-CloudDesk-Signature: sha256=abc123...`

```python
import hmac, hashlib

def verify(payload_bytes, signature_header, secret):
    # signature_header format: "sha256=hexdigest"
    algo, signature = signature_header.split("=", 1)
    assert algo == "sha256"
    expected = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Retry Policy

| Attempt | Delay | Cumulative |
|---------|-------|------------|
| 1 | Immediate | 0s |
| 2 | 1 minute | 1m |
| 3 | 5 minutes | 6m |
| 4 | 15 minutes | 21m |
| 5 | 1 hour | 1h 21m |
| 6 | 6 hours | 7h 21m |
| 7 | 24 hours | 31h 21m |

- Max 7 retries over ~31 hours
- After 7 failures: webhook disabled, admin notified
- Re-enable: Settings → Webhooks → Enable

## Filtering (Enterprise)

### By Workspace
```json
{ "url": "...", "events": ["ticket.*"], "filter": { "workspace_ids": ["ws-1", "ws-2"] } }
```

### By Customer
```json
{ "url": "...", "events": ["ticket.*"], "filter": { "customer_ids": ["cust-123"] } }
```

### By Custom Field
```json
{ "url": "...", "events": ["ticket.*"], "filter": { "custom_fields": { "priority": "high" } } }
```

## Testing Webhooks

### Test Button
- Dashboard: Webhooks → [Webhook] → Send Test
- Sends `webhook.test` event with sample payload

### Local Development
Use ngrok or Cloudflare Tunnel:
```bash
ngrok http 3000
# Use https://abc123.ngrok.io/webhooks as URL
```

### CLI Testing
```bash
curl -X POST https://your-app.com/webhooks \
  -H "Content-Type: application/json" \
  -H "X-CloudDesk-Signature: sha256=..." \
  -d '{"id":"test","type":"webhook.test","timestamp":"...","data":{}}'
```

## Security Best Practices

- **Always verify signatures** — prevents spoofing
- **Use HTTPS only** — CloudDesk rejects HTTP URLs
- **Rotate secrets periodically** — Settings → Webhooks → Rotate Secret
- **Respond 2xx within 10s** — prevents timeout retries
- **Idempotency** — handle duplicate deliveries (same `id`)

## Monitoring

### Delivery Logs
Settings → Webhooks → [Webhook] → Deliveries
- Shows: timestamp, event, status, response code, latency
- Filter by: date, status, event type
- Retry failed deliveries manually

### Metrics (Enterprise)
- Success rate, latency percentiles
- Alert on: failure rate > 5%, p99 latency > 5s
- Dashboard: Admin → Integrations → Webhook Metrics

## Related Articles
- [Integration Troubleshooting](integration-troubleshooting.md)
- [Slack Setup Guide](slack-setup.md)
- [API Authentication](api-authentication.md)
- [Audit Log Guide](audit-log.md)