---
title: "Microsoft Teams Integration Setup"
category: "integration"
tags: ["teams", "microsoft", "integration", "notifications", "setup"]
summary: "Connect CloudDesk with Microsoft Teams for real-time notifications and collaboration."
---

# Microsoft Teams Integration Setup

## Prerequisites

- Microsoft Teams admin or owner permissions
- CloudDesk workspace admin role
- Target Teams channel identified

## Installation

### 1. From CloudDesk
1. Settings → Integrations → Microsoft Teams → **Add to Teams**
2. Sign in with Microsoft account
3. Select Teams workspace
4. Review permissions:
   - `ChannelMessage.Send` — post messages
   - `Channel.ReadBasic.All` — list channels
   - `Team.ReadBasic.All` — list teams
5. Click **Accept**

### 2. From Teams App Store
1. Search "CloudDesk" in Teams Apps
2. Click **Add** → select team
3. Follow same permission review

## Configuration

### Default Notification Channel
1. Settings → Integrations → Microsoft Teams → Configure
2. Select **Team** and **Channel** for notifications
3. Bot automatically added to channel

### Per-Workspace Override
Each CloudDesk workspace can have its own Teams channel:
1. Workspace → Settings → Integrations → Teams
2. Set notification channel for this workspace

### Event Subscriptions
Choose which events send to Teams:
- [ ] Ticket created
- [ ] Ticket assigned
- [ ] Ticket status changed
- [ ] Ticket resolved
- [ ] Comment added
- [ ] File shared
- [ ] Storage warning
- [ ] Mention (@user in comment)

## Message Format

### Ticket Notification (Adaptive Card)
```json
{
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    { "type": "TextBlock", "text": "New Ticket: CD-1001", "weight": "Bolder", "size": "Medium" },
    { "type": "FactSet", "facts": [
      { "title": "Subject:", "value": "SSO login fails for whole team" },
      { "title": "Customer:", "value": "Acme Corp (Enterprise)" },
      { "title": "Severity:", "value": "Critical" },
      { "title": "Assignee:", "value": "Sam Agent" }
    ]},
    { "type": "ActionSet", "actions": [
      { "type": "Action.OpenUrl", "title": "View in CloudDesk", "url": "https://clouddesk.com/tickets/CD-1001" }
    ]}
  ]
}
```

## Troubleshooting

### "Not receiving notifications"
1. Check Integration Status → **Connected**
2. Click **Test Connection** → should post test card
3. Verify bot in channel (check channel members)
4. Check channel permissions

### "Wrong channel/team"
1. Settings → Teams → Notification Channel
2. Select correct team and channel
3. Bot auto-added on save

### "Adaptive cards not rendering"
- Update Teams to latest version
- Some older Teams clients don't support Adaptive Cards 1.4
- Fallback to plain text available in settings

### "App removed"
- Reinstall from Settings → Integrations → Teams
- Historical messages not restored

## Teams Commands

### `@CloudDesk ticket CD-1001`
Show ticket details in Teams

### `@CloudDesk create "Subject" "Body"`
Create ticket from Teams (Enterprise)

### `@CloudDesk assign CD-1001 @user`
Assign ticket (Enterprise)

## Security

- Tokens encrypted at rest (Microsoft Graph)
- OAuth tokens auto-refreshed via Microsoft Identity
- Revoke: Settings → Teams → Disconnect
- Audit log tracks all Teams actions

## Related Articles
- [Integration Troubleshooting](integration-troubleshooting.md)
- [Webhook Configuration](webhook-configuration.md)
- [Slack Setup Guide](slack-setup.md)
- [Jira Configuration](jira-configuration.md)