---
title: "Slack Integration Setup"
category: "integration"
tags: ["slack", "integration", "notifications", "setup", "configuration"]
summary: "Step-by-step guide to connect CloudDesk with Slack for real-time notifications."
---

# Slack Integration Setup

## Prerequisites

- Slack workspace admin permissions
- CloudDesk workspace admin role
- Target Slack channel(s) identified

## Installation

### 1. From CloudDesk
1. Settings → Integrations → Slack → **Add to Slack**
2. Choose Slack workspace
3. Review permissions:
   - `chat:write` — post messages
   - `channels:read` — list public channels
   - `groups:read` — list private channels
   - `incoming-webhook` — post to specific channel
4. Click **Allow**

### 2. From Slack App Directory
1. Search "CloudDesk" in Slack App Directory
2. Click **Add to Slack**
3. Follow same permission review

## Configuration

### Default Notification Channel
1. Settings → Integrations → Slack → Configure
2. Select **Default Channel** for notifications
3. Bot must be in channel: `/invite @CloudDesk`

### Per-Workspace Override
Each CloudDesk workspace can have its own Slack channel:
1. Workspace → Settings → Integrations → Slack
2. Set notification channel for this workspace

### Event Subscriptions
Choose which events send to Slack:
- [ ] Ticket created
- [ ] Ticket assigned
- [ ] Ticket status changed
- [ ] Ticket resolved
- [ ] Comment added
- [ ] File shared
- [ ] Storage warning
- [ ] Mention (@user in comment)

## Message Format

### Ticket Notification
```
🎫 *New Ticket: CD-1001*
*Subject:* SSO login fails for whole team
*Customer:* Acme Corp (Enterprise)
*Severity:* Critical
*Assignee:* @sam.agent
*Channel:* #support-tickets
<https://clouddesk.com/tickets/CD-1001|View in CloudDesk>
```

### Customization (Enterprise)
Admin → Integrations → Slack → Message Templates
- Customize per event type
- Use variables: `{{ticket.id}}`, `{{ticket.subject}}`, `{{customer.name}}`
- Add buttons: "Assign to me", "View ticket", "Reply"

## Troubleshooting

### "Not receiving notifications"
1. Check Integration Status → **Connected**
2. Click **Test Connection** → should post test message
3. Verify bot in channel: `/invite @CloudDesk`
4. Check channel permissions (bot can post)

### "Wrong channel"
1. Settings → Slack → Notification Channel
2. Select correct channel
3. Ensure bot is member

### "Duplicate notifications"
- Check for multiple webhook URLs
- Disable duplicate integrations
- Each workspace should have one Slack connection

### "App uninstalled"
- Reinstall from Settings → Integrations → Slack
- Historical messages not restored

## Slack Commands

### `/clouddesk ticket CD-1001`
Show ticket details in Slack

### `/clouddesk create "Subject" "Body"`
Create ticket from Slack (Enterprise)

### `/clouddesk assign CD-1001 @user`
Assign ticket (Enterprise)

## Security

- Tokens encrypted at rest
- OAuth tokens auto-refreshed
- Revoke: Settings → Slack → Disconnect
- Audit log tracks all Slack actions

## Related Articles
- [Integration Troubleshooting](integration-troubleshooting.md)
- [Webhook Configuration](webhook-configuration.md)
- [Microsoft Teams Setup](teams-setup.md)
- [Jira Configuration](jira-configuration.md)