---
title: "Enterprise Security Best Practices"
category: "security"
tags: ["security", "enterprise", "compliance", "audit", "access-control"]
summary: "Security configuration, audit logging, access controls, and compliance for Enterprise customers."
---

# Enterprise Security Best Practices

## Access Control

### Principle of Least Privilege
- Grant minimum roles needed for job function
- Regular access reviews (quarterly recommended)
- Automate deprovisioning on role change/termination

### Role Configuration
| Role | Use Case |
|------|----------|
| Owner | Business owner, 1-2 max |
| Admin | IT admins, team leads |
| Member | Regular contributors |
| Viewer | Auditors, stakeholders |

### Domain Restrictions (Enterprise)
- Admin → Security → Allowed Email Domains
- Only users from approved domains can join
- Blocks personal email addresses

## Authentication

### Enforce MFA
- Admin → Security → Require MFA
- Grace period: 7 days for existing users
- All methods supported (TOTP, WebAuthn, SMS)

### SSO Integration
- SAML 2.0 or OIDC
- IdP-initiated and SP-initiated flows
- Just-in-Time (JIT) provisioning supported
- SCIM for automated user lifecycle (Enterprise)

### Session Management
- Idle timeout: 30 min (configurable)
- Max session: 8 hours (configurable)
- Concurrent sessions: 5 per user (configurable)
- Force re-auth on sensitive actions

## Audit Logging

### What's Logged
- Authentication events (login, logout, MFA, SSO)
- Permission changes (role grants, revokes)
- Data access (exports, bulk downloads)
- Configuration changes (settings, integrations)
- File operations (create, delete, share, download)
- Admin actions (user management, billing)

### Accessing Logs
- Admin → Audit Log
- Filter by: user, action, resource, date range
- Export: CSV, JSON (max 10,000 rows)

### Retention
| Plan | Retention |
|------|-----------|
| Free | 30 days |
| Pro | 90 days |
| Business | 1 year |
| Enterprise | 7 years |

### SIEM Integration
- Webhook: `POST /api/v1/webhooks/audit`
- Batch delivery every 5 minutes
- Includes full event payload
- Signature verification with shared secret

## Data Protection

### Encryption
- **At rest**: AES-256 (all plans)
- **In transit**: TLS 1.3 (all plans)
- **Key management**: CloudDesk managed (standard), BYOK (Enterprise)

### Data Loss Prevention (Enterprise)
- Admin → Security → DLP Rules
- Detect: credit cards, SSN, API keys, custom regex
- Actions: block, quarantine, alert
- Applies to: files, messages, comments

### Backup and Recovery
- Automated daily snapshots
- Point-in-time recovery (Enterprise: 30 days)
- Cross-region replication (Enterprise)
- RPO: 24 hours, RTO: 4 hours

## Compliance

### Certifications
- SOC 2 Type II (all plans)
- ISO 27001 (Business, Enterprise)
- GDPR DPA (Business, Enterprise)
- HIPAA BAA (Enterprise only)

### Compliance Reports
- Admin → Compliance → Reports
- Generate: SOC 2, ISO, GDPR artifact
- Available within 24 hours of request

### Data Processing Agreement
- Standard DPA at clouddesk.com/dpa
- Custom DPA for Enterprise
- Subprocessor list: clouddesk.com/subprocessors

## Incident Response

### Security Events
- Automated alerts for: brute force, impossible travel, mass download
- Admin notified via email + in-app
- Enterprise: dedicated security contact

### Breach Notification
- CloudDesk notifies affected customers within 72 hours
- Includes: scope, impact, remediation steps
- Enterprise: direct phone contact for critical

## Related Articles
- [SSO Troubleshooting](sso-troubleshooting.md)
- [MFA Recovery](mfa-recovery.md)
- [Account Deletion](account-deletion.md)
- [Audit Log Guide](audit-log.md)