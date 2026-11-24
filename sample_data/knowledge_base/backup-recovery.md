---
title: "Backup and Disaster Recovery"
category: "account"
tags: ["backup", "disaster-recovery", "rpo", "rto", "business-continuity"]
summary: "CloudDesk's backup strategy, recovery point objectives, recovery time objectives, and disaster recovery procedures."
---

# Backup and Disaster Recovery

## Backup Strategy

### Automated Backups
- **Frequency**: Daily at 02:00 UTC
- **Scope**: All customer data (files, databases, configurations)
- **Method**: Incremental snapshots with weekly full
- **Retention**: 30 days (configurable for Enterprise)

### What's Backed Up
- File content and metadata
- Database: tickets, customers, users, settings
- Workspace configurations
- Integration tokens (encrypted)
- Audit logs

### What's NOT Backed Up
- Temporary files (.tmp, cache)
- Trash folder contents
- Session tokens
- Rate limit counters

## Recovery Objectives

### By Plan

| Plan | RPO (Data Loss) | RTO (Downtime) | Recovery Type |
|------|-----------------|----------------|---------------|
| Free | 24 hours | 24 hours | Best effort |
| Pro | 24 hours | 12 hours | Standard |
| Business | 4 hours | 4 hours | Priority |
| Enterprise | 1 hour | 1 hour | Dedicated |

### Definitions
- **RPO (Recovery Point Objective)**: Maximum data loss measured in time
- **RTO (Recovery Time Objective)**: Maximum downtime before service restored

## Recovery Procedures

### Standard Recovery (All Plans)
1. Support receives recovery request
2. Identify affected workspace/time range
3. Restore from latest snapshot before incident
4. Validate data integrity
5. Notify customer when complete

### Point-in-Time Recovery (Business, Enterprise)
- Restore to any minute within retention window
- Creates new workspace with restored state
- Original workspace preserved for comparison
- Requires support ticket with timestamp

### Cross-Region Failover (Enterprise)
- Automatic failover to secondary region
- DNS updates within 5 minutes
- Data replication: synchronous (RPO < 1 min)
- Manual failback after primary restored

## Disaster Scenarios

### Regional Outage
- **Detection**: Automated health checks (30s interval)
- **Failover**: Automatic (Enterprise) / Manual (others)
- **Communication**: Status page, email, in-app banner
- **Post-mortem**: Published within 5 business days

### Data Corruption
- **Detection**: Checksum validation on read
- **Isolation**: Affected workspace set to read-only
- **Recovery**: Restore from last clean snapshot
- **Investigation**: Root cause analysis

### Ransomware/Encryption
- **Detection**: Anomalous encryption patterns
- **Response**: Immediate snapshot, isolate workspace
- **Recovery**: Restore from pre-encryption snapshot
- **Reporting**: Legal/security team notification

## Testing and Validation

### Backup Validation
- **Daily**: Automated restore test (1% of workspaces)
- **Weekly**: Full restore drill (staging environment)
- **Monthly**: Cross-region failover test (Enterprise)
- **Annually**: Full disaster simulation

### Customer Validation
- Enterprise: Quarterly restore test available
- Business: Annual restore test available
- Results shared with designated contacts

## Customer Responsibilities

### Data Export
- Regular exports recommended (monthly)
- Settings → Account → Export Data
- Store exports in independent location

### Configuration Documentation
- Document custom integrations
- Record webhook URLs and secrets
- Maintain API key inventory

### Access Management
- Ensure at least 2 admins per workspace
- Document admin contact information
- Test admin recovery procedures

## Related Articles
- [Account Deletion](account-deletion.md)
- [File Recovery](file-recovery.md)
- [Enterprise Security](enterprise-security.md)
- [Audit Log Guide](audit-log.md)