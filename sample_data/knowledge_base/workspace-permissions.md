---
title: "Workspace Permissions and Sharing"
category: "workspace_permissions"
tags: ["workspace", "permissions", "sharing", "external", "roles"]
summary: "Configure workspace roles, share folders externally, and manage member access."
---

# Workspace Permissions and Sharing

## Workspace Roles

| Role | Permissions |
|------|-------------|
| Owner | Full control, delete workspace, manage billing |
| Admin | Manage members, settings, integrations |
| Member | Create/edit files, share internally |
| Viewer | Read-only access |

## External Sharing

### Availability by Plan

| Plan | External Sharing |
|------|------------------|
| Free | No |
| Pro | Yes (read-only) |
| Business | Yes (read/write) |
| Enterprise | Yes (read/write + expiration) |

### Sharing a Folder

1. Navigate to the folder
2. Click **Share** → **Create Link**
3. Choose access level: **View** or **Edit**
4. (Enterprise) Set expiration date
5. Copy link and send to recipient

### Troubleshooting "Share Button Greyed Out"

**Cause 1: Plan doesn't support external sharing**
- Free plan: Upgrade to Pro or higher
- Check: Settings → Plan → External Sharing

**Cause 2: Admin disabled sharing**
- Workspace Admin → Settings → Security → External Sharing
- Must be enabled by workspace owner/admin

**Cause 3: Folder permissions**
- You need **Admin** or **Member** role on the folder
- Viewers cannot create share links

**Cause 4: Domain restrictions**
- Enterprise: Admin may restrict to approved domains
- Check: Admin → Security → Allowed Domains

## Internal Sharing

### Adding Members
1. Workspace → Members → Add Member
2. Enter email, select role
3. Member receives invitation email

### Changing Roles
- Owners/Admins can change any member's role
- Cannot demote the last Owner

### Removing Members
- Removes access immediately
- Files remain owned by workspace

## Permission Inheritance

- Folder permissions inherit from parent
- Explicit permissions override inherited
- "Restricted" folders break inheritance

## Audit Log

Track all permission changes:
- Workspace → Settings → Audit Log
- Filter by: member, action, date range

## Related Articles
- [Storage Quota Management](storage-quota.md)
- [File Recovery](file-recovery.md)
- [Enterprise Security Best Practices](enterprise-security.md)