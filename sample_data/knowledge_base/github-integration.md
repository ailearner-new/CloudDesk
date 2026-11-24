---
title: "GitHub Integration Setup"
category: "integration"
tags: ["github", "integration", "pull-requests", "commits", "repositories"]
summary: "Connect CloudDesk with GitHub to link pull requests, commits, and branches to tickets."
---

# GitHub Integration Setup

## Prerequisites

- GitHub organization admin permissions
- CloudDesk workspace admin role
- Target repositories identified

## Installation

### 1. Install GitHub App
1. Settings → Integrations → GitHub → **Install GitHub App**
2. Select GitHub organization
3. Choose repositories: **All repositories** or **Select repositories**
4. Review permissions:
   - **Metadata** — read repo info (required)
   - **Pull requests** — read/write PRs
   - **Issues** — read/write issues
   - **Contents** — read file contents
   - **Commit statuses** — read/write status checks
   - **Webhooks** — manage webhooks
5. Click **Install**

### 2. Configure in CloudDesk
1. Settings → Integrations → GitHub → Configure
2. Select installed app
3. Choose default repository for new links
4. Save

## Configuration

### Repository Mapping
Map CloudDesk workspaces to GitHub repositories:
1. Workspace → Settings → Integrations → GitHub
2. Click **Add Repository**
3. Select workspace
4. Select repository (from installed app)
5. Choose **Link Behavior**:
   - **Auto-link** — PRs with ticket ID in title/branch auto-link
   - **Manual** — link via UI or comment command

### Branch Naming Convention
Default pattern: `CD-1001-short-description`
- Ticket ID prefix: `CD-` (configurable)
- Auto-detects ticket ID from branch name
- Links PR to ticket when opened

### Commit Message Convention
Include ticket ID in commits:
```
git commit -m "CD-1001: Fix SAML certificate validation"
```
- Links commit to ticket
- Shows in ticket timeline

## Features

### Pull Request Linking
- PR opened with ticket ID → auto-linked
- PR status shown on ticket: Open, Merged, Closed
- Merge → ticket comment with PR link
- Close without merge → ticket comment

### Commit Tracking
- Commits with ticket ID → appear in ticket timeline
- View diff from ticket
- Filter by author, date

### Deployment Tracking (Enterprise)
- Connect GitHub Environments
- Deployment status on ticket
- Rollback detection

### GitHub Actions Integration
```yaml
# .github/workflows/clouddesk.yml
on:
  pull_request:
    types: [opened, synchronize, closed]
jobs:
  clouddesk:
    runs-on: ubuntu-latest
    steps:
      - uses: clouddesk/github-action@v1
        with:
          ticket-id: ${{ github.event.pull_request.title }}
          action: update-status
```

## Troubleshooting

### "App not installing"
1. Must be organization admin
2. Check organization settings → Third-party access → Allow
3. For Enterprise Cloud: check SAML restrictions

### "PRs not linking"
1. Verify repository mapped to workspace
2. Check branch name contains ticket ID (e.g., `CD-1001-fix`)
3. Check PR title contains ticket ID
4. Review auto-link setting (Auto-link vs Manual)

### "Commits not showing"
1. Commit message must contain ticket ID: `CD-1001: message`
2. Push commits after linking (historical commits not retroactively linked)
3. Check repository permissions (Contents: read)

### "Webhook delivery failing"
1. Check GitHub → Settings → Webhooks → Recent Deliveries
2. Verify payload URL accessible
3. Ensure secret matches

## Security

- GitHub App tokens (not personal access tokens)
- Tokens auto-rotated by GitHub
- Minimal permissions (principle of least privilege)
- Revoke: Settings → GitHub → Uninstall App
- Audit log tracks all GitHub actions

## Related Articles
- [Integration Troubleshooting](integration-troubleshooting.md)
- [Webhook Configuration](webhook-configuration.md)
- [Jira Configuration](jira-configuration.md)
- [API Authentication](api-authentication.md)