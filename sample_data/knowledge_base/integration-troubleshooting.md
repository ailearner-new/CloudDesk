---
title: "Integration Troubleshooting Guide"
category: "integration"
tags: ["integrations", "slack", "teams", "jira", "github", "webhooks"]
summary: "Diagnose and fix common integration issues with Slack, Microsoft Teams, Jira, and GitHub."
---

# Integration Troubleshooting Guide

## Slack Integration

### "Notifications stopped working"

**Common causes:**
1. **Bot token revoked** — Reinstall the Slack app
2. **Channel archived/deleted** — Update the notification channel
3. **Rate limited by Slack** — Check Slack API limits
4. **Workspace URL changed** — Reconfigure integration

**Diagnosis steps:**
1. Check Integration Settings → Slack → Connection Status
2. Click "Test Connection" — should return success
3. Verify bot is in the target channel: `/invite @CloudDesk`
4. Check Slack audit log for "app_uninstalled" or "tokens_revoked"

**Resolution:**
1. Disconnect and reconnect the integration
2. Ensure bot has `chat:write`, `channels:read`, `groups:read` scopes
3. Verify the channel still exists and bot is a member

### "Wrong channel receiving notifications"
- Update channel in Integration Settings → Slack → Notification Channel
- Ensure channel is not private (or bot is added to private channel)

## Microsoft Teams Integration

### "No notifications in Teams"
1. Verify the incoming webhook URL is correct
2. Check Teams connector configuration
3. Ensure the channel allows external apps
4. Test with "Send Test Notification" button

### "Adaptive cards not rendering"
- Teams requires specific card schema
- Update to latest CloudDesk version for card fixes

## Jira Integration

### "Issues not syncing"
1. Verify Jira user has **Browse Projects** and **Create Issues** permissions
2. Check Jira API token hasn't expired
3. Ensure project key matches exactly (case-sensitive)
4. Verify issue type mapping in settings

### "Transition errors"
- Jira workflow may not allow the transition
- Check: Jira Settings → Issues → Workflows
- Map CloudDesk statuses to valid Jira transitions

## GitHub Integration

### "PRs not linking to tickets"
1. Ensure GitHub app is installed on the correct organization
2. Check repository permissions (Read/Write for metadata)
3. Verify branch naming convention includes ticket ID (e.g., `CD-1001-fix`)

### "Webhook delivery failing"
1. Check GitHub → Settings → Webhooks → Recent Deliveries
2. Verify payload URL is accessible
3. Ensure secret matches CloudDesk configuration

## General Webhook Troubleshooting

### Webhook Not Firing
1. Verify webhook URL is HTTPS and accessible
2. Check firewall allows inbound from CloudDesk IPs
3. Ensure endpoint returns 2xx within 10 seconds
4. Check CloudDesk webhook delivery logs

### Signature Verification Failing
- Ensure `X-CloudDesk-Signature` header is validated
- Use constant-time comparison
- Clock skew tolerance: 5 minutes

## Reconnecting Integrations

When in doubt, disconnect and reconnect:
1. Integration Settings → [Integration] → Disconnect
2. Wait 30 seconds
3. Reconnect with fresh authentication
4. Run "Test Connection"

## Related Articles
- [Slack Setup Guide](slack-setup.md)
- [Jira Configuration](jira-configuration.md)
- [GitHub Integration](github-integration.md)
- [Webhook Security](webhook-security.md)