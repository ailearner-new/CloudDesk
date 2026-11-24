---
title: "Storage Quota Management"
category: "storage_quota"
tags: ["storage", "quota", "limits", "workspace", "upgrade"]
summary: "Understand storage limits, monitor usage, resolve quota exceeded errors, and plan upgrades."
---

# Storage Quota Management

## Storage Limits by Plan

| Plan | Storage per Workspace | Total Workspaces | Overages |
|------|----------------------|------------------|----------|
| Free | 10 GB | 1 | Read-only at limit |
| Pro | 100 GB | 3 | Read-only at limit |
| Business | 1 TB | 10 | Read-only at limit |
| Enterprise | Unlimited | Unlimited | N/A |

## Quota Exceeded Error

When a workspace hits its storage limit:
- **Uploads fail** with `storage_quota_exceeded`
- **File creation** returns 413 Payload Too Large
- **Existing files** remain accessible (read-only)
- **Dashboard** shows warning banner

## Checking Usage

### Via Dashboard
1. Navigate to Workspace → Settings → Storage
2. View used vs. limit with breakdown by folder

### Via API
```bash
GET /api/v1/workspaces/{workspace_id}/storage
```

Response:
```json
{
  "used_gb": 95.2,
  "limit_gb": 100,
  "percentage": 95.2,
  "breakdown": {
    "files": 80.5,
    "versions": 12.3,
    "trash": 2.4
  }
}
```

## Common Causes of High Usage

### 1. File Versions
Every edit creates a new version. Old versions count toward quota.
- **Fix**: Enable auto-cleanup (Admin → Workspace → Version Retention)
- **Manual**: Delete old versions from file history

### 2. Trash Folder
Deleted files stay in trash for 30 days.
- **Fix**: Empty trash manually or wait for auto-expiry
- **API**: `POST /api/v1/workspaces/{id}/trash/empty`

### 3. Large Files
Single files > 1 GB can accumulate quickly.
- **Fix**: Archive to external storage, use links instead

### 4. Sync Artifacts
Some integrations (e.g., Slack, GitHub) create temporary files.
- **Fix**: Review integration settings, disable file sync if not needed

## Resolving Quota Issues

### Immediate Actions
1. **Empty trash** — Frees space instantly
2. **Delete old versions** — Keep only last 5 versions per file
3. **Remove duplicates** — Use dashboard "Find Duplicates" tool
4. **Archive old projects** — Move to cold storage

### Plan Upgrade
If consistently near limit:
1. Review plan comparison at clouddesk.com/pricing
2. Upgrade takes effect immediately
3. No migration needed — just higher limit

### Enterprise Unlimited
Enterprise plans have no storage limits. Contact sales for upgrade.

## Monitoring and Alerts

### Set Up Alerts
- Dashboard: Workspace → Settings → Notifications → Storage
- Threshold options: 75%, 90%, 95%
- Channels: Email, Slack, Webhook

### API Monitoring
```bash
# Check all workspaces for a customer
GET /api/v1/customers/{customer_id}/workspaces?include_storage=true
```

## Related Articles
- [Workspace Permissions](workspace-permissions.md)
- [File Recovery](file-recovery.md)
- [Subscription Management](subscription-management.md)