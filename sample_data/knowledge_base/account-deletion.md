---
title: "Account and Workspace Deletion"
category: "account"
tags: ["account", "deletion", "gdpr", "workspace", "data-erasure", "compliance"]
summary: "Process for deleting accounts and workspaces, GDPR data erasure requests, and compliance requirements."
---

# Account and Workspace Deletion

## Workspace Deletion

### Standard Deletion (All Plans)
1. **Owner only** — Only workspace owner can delete
2. **Confirmation required** — Type workspace name to confirm
3. **30-day grace period** — Workspace is "pending deletion", recoverable
4. **Permanent removal** — After 30 days, all data erased

### During Grace Period
- Workspace is inaccessible to members
- Owner can cancel deletion from Settings
- No new data can be added
- Billing stops immediately

### After Grace Period
- All files, messages, settings permanently deleted
- Cannot be recovered
- Audit log entry created

## Account Deletion

### Individual Account (Free/Pro)
1. Settings → Account → Delete Account
2. Enter password to confirm
3. All personal workspaces deleted (if owner)
4. Removed from shared workspaces
5. Data erased per retention policy

### Enterprise Account
- Must be initiated by Enterprise Admin
- Admin → Members → [User] → Delete Account
- Triggers GDPR-compliant erasure workflow
- 30-day grace period for recovery

## GDPR Data Erasure (Right to be Forgotten)

### Request Process
1. Submit request via support@clouddesk.com or GDPR portal
2. Verify identity (government ID for Enterprise)
3. Request logged with timestamp
4. **30-day SLA** for completion

### What Gets Erased
- Personal data: name, email, IP logs, usage analytics
- Generated content: files, comments, messages authored
- Metadata linking to identity
- Backup copies (within 90 days)

### What Is Retained (Legal Basis)
- Transaction records (tax law, 7 years)
- Audit logs (security, anonymized)
- Aggregated analytics (no personal identifiers)

### Verification
- Requester receives completion certificate
- Lists categories of data erased
- Timestamp of completion

## Data Export Before Deletion

### Self-Service Export
- Settings → Account → Export Data
- Includes: files, messages, settings, audit trail
- Format: JSON + original files in ZIP
- Available for 7 days after generation

### Enterprise Bulk Export
- Admin → Compliance → Bulk Export
- Select users/workspaces
- Includes all metadata

## Compliance Notes

### Data Processing Agreement (DPA)
- Available for Business and Enterprise
- Covers GDPR, CCPA, LGPD
- Standard contractual clauses included

### Subprocessors
- Listed at clouddesk.com/subprocessors
- 30-day notice for new subprocessors
- Right to object (Enterprise)

### Data Residency
- Enterprise: Choose region (US, EU, APAC)
- Free/Pro/Business: US primary, EU replication

## Related Articles
- [Workspace Permissions](workspace-permissions.md)
- [Storage Quota Management](storage-quota.md)
- [Enterprise Security Best Practices](enterprise-security.md)
- [Backup and Recovery](backup-recovery.md)