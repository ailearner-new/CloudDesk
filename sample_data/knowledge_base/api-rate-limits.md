---
title: "API Rate Limits and Best Practices"
category: "api_failure"
tags: ["api", "rate-limit", "429", "throttling", "best-practices"]
summary: "Understand CloudDesk API rate limits, handle 429 responses, and implement exponential backoff."
---

# API Rate Limits and Best Practices

## Rate Limit Tiers

| Plan | Requests/Minute | Burst Allowance |
|------|-----------------|-----------------|
| Free | 30 | 10 |
| Pro | 100 | 50 |
| Business | 300 | 100 |
| Enterprise | 1000 | 500 |

Limits apply per workspace, aggregated across all API keys.

## Response Headers

Every API response includes rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1705320000
Retry-After: 45  (only on 429)
```

## Handling 429 Responses

When you receive HTTP 429 Too Many Requests:

1. **Read `Retry-After` header** — seconds to wait before retrying
2. **Implement exponential backoff** — start with `Retry-After`, then 2x, 4x, 8x...
3. **Add jitter** — ±10% to prevent thundering herd
4. **Respect the limit** — don't retry immediately

### Example Backoff Algorithm (Python)

```python
import time
import random
import httpx

async def api_call_with_backoff(client, method, url, max_retries=5):
    for attempt in range(max_retries):
        resp = await client.request(method, url)
        if resp.status_code != 429:
            return resp
        
        retry_after = int(resp.headers.get("Retry-After", 60))
        wait_time = retry_after * (2 ** attempt) + random.uniform(0, 0.1 * retry_after)
        print(f"Rate limited. Waiting {wait_time:.1f}s (attempt {attempt + 1})")
        await asyncio.sleep(wait_time)
    
    raise Exception("Max retries exceeded")
```

## Best Practices

### 1. Batch Requests
Use batch endpoints where available (e.g., `/api/v1/tickets/batch`) to reduce call count.

### 2. Cache Responses
Cache GET responses for at least 60 seconds. Use `ETag` and `If-None-Match` headers.

### 3. Use Webhooks
Subscribe to webhook events instead of polling:
- `ticket.created`
- `ticket.updated`
- `ticket.resolved`

### 4. Monitor Your Usage
Check `/api/v1/workspaces/{id}/api-usage` for current consumption.

### 5. Distribute Load
For high-volume integrations:
- Spread requests evenly over time
- Use multiple API keys if needed (Enterprise)
- Implement client-side queuing

## Common Issues

### "We're under the limit but getting 429"
- **Burst limit exceeded** — short bursts can exceed per-minute average
- **Shared workspace limit** — other integrations count toward the same limit
- **Clock skew** — ensure your system clock is synchronized

### Nightly Sync Jobs
For batch jobs running at specific times:
- Request a temporary limit increase (Enterprise)
- Spread the job over a longer window
- Use the `bulk` endpoint if available

## Rate Limit Exemptions

Enterprise customers can request:
- Higher base limits
- Dedicated rate limit pool
- Custom burst allowances

Contact your account manager or support@clouddesk.com.

## Related Articles
- [API Authentication](api-authentication.md)
- [Webhook Configuration](webhook-configuration.md)
- [Bulk Operations](bulk-operations.md)