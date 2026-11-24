---
title: "Jira Integration Configuration"
category: "integration"
tags: ["jira", "integration", "sync", "issues", "workflow"]
summary: "Connect CloudDesk with Jira to sync tickets, automate issue creation, and keep both systems in sync."
---

# Jira Integration Configuration

## Prerequisites

- Jira admin permissions (Cloud or Data Center)
- CloudDesk workspace admin role
- Jira API token (user-specific)

## Installation

### 1. Generate Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**
3. Label: "CloudDesk Integration"
4. Copy token — **shown once only**

### 2. Connect in CloudDesk
1. Settings → Integrations → Jira → **Connect**
2. Enter:
   - **Jira URL**: `https://your-domain.atlassian.net` (Cloud) or your Data Center URL
   - **Email**: Your Jira account email
   - **API Token**: Paste the token from step 1
3. Click **Test Connection** → should verify successfully
4. Click **Save**

## Configuration

### Project Mapping
Map CloudDesk workspaces to Jira projects:
1. Workspace → Settings → Integrations → Jira
2. Click **Add Project Mapping**
3. Select CloudDesk workspace
4. Select Jira project (fetched via API)
5. Choose **Sync Direction**:
   - **Bidirectional** — changes sync both ways
   - **CloudDesk → Jira** — tickets create Jira issues
   - **Jira → CloudDesk** — Jira issues create tickets

### Issue Type Mapping
| CloudDesk Category | Jira Issue Type |
|-------------------|-----------------|
| `login_issue` | Bug |
| `billing` | Task |
| `api_failure` | Bug |
| `storage_quota` | Task |
| `security` | Security Bug |
| `account` | Task |
| `feature_request` | Story |
| `other` | Task |

Customize: Workspace → Jira → Issue Type Mapping

### Status Mapping
Default bidirectional sync:

| CloudDesk Status | Jira Status |
|-----------------|-------------|
| `new` | To Do |
| `in_progress` | In Progress |
| `waiting_on_customer` | Waiting for Customer |
| `waiting_on_approval` | Waiting for Approval |
| `escalated` | Escalated |
| `resolved` | Done |
| `closed` | Closed |

Customize per project in Jira → Status Mapping.

### Field Mapping
Default fields synced:
- **Summary** ←→ Ticket Subject
- **Description** ←→ Ticket Body
- **Assignee** ←→ CloudDesk Assignee
- **Labels** ←→ Ticket Category + Tags
- **Custom Field: CloudDesk Ticket ID** → `customfield_XXXXX`

## Synchronization

### Real-Time Sync
- Ticket created → Jira issue created (within 30s)
- Status change → Jira transition (within 10s)
- Comment added → Jira comment (within 10s)
- Assignment change → Jira assignee update

### Manual Sync
- Workspace → Jira → **Sync Now**
- Forces full reconciliation
- Resolves conflicts (last-write-wins by default)

### Conflict Resolution
| Conflict | Resolution |
|----------|------------|
| Both updated description | CloudDesk wins (source of truth) |
| Both updated status | Jira wins (workflow engine) |
| Both updated assignee | CloudDesk wins |
| Deleted in one, updated in other | Restore in deleted system |

## Advanced Features

### Jira Automation Rules
Create rules in Jira for:
- Auto-assign based on component
- SLA tracking for critical tickets
- Escalation on stale issues
- Notify Slack on priority change

### CloudDesk → Jira Webhooks
For custom Jira workflows:
- `ticket.created` → Create issue with custom fields
- `ticket.escalated` → Transition to "Escalated", add watchers
- `approval.requested` → Add "Needs Approval" label

### Bulk Operations (Enterprise)
- Sync existing tickets to Jira (one-time)
- Migrate from another tool via Jira CSV import

## Troubleshooting

### "Connection test failed"
1. Verify Jira URL (include `https://`)
2. Check email matches API token owner
3. Ensure API token not expired
4. For Data Center: check firewall allows CloudDesk IPs

### "Issues not syncing"
1. Check project mapping exists
2. Verify Jira user has **Browse Projects**, **Create Issues**, **Edit Issues**
3. Check issue type mapping (Jira project must have the issue types)
4. Review sync logs: Workspace → Jira → Sync History

### "Status not transitioning"
1. Verify Jira workflow has the transition
2. Check status mapping matches Jira status names exactly
3. Ensure user has **Transition Issues** permission

### "Custom fields not syncing"
1. Field must be on Jira **Create** and **Edit** screens
2. Field ID must match in CloudDesk mapping
3. Field type must be compatible (text, select, user picker)

## Security

- API tokens encrypted at rest
- Tokens never logged
- Revoke: Settings → Jira → Disconnect
- Audit log tracks all Jira actions

## Related Articles
- [Integration Troubleshooting](integration-troubleshooting.md)
- [Webhook Configuration](webhook-configuration.md)
- [Slack Setup Guide](slack-setup.md)
- [GitHub Integration](github-integration.md)