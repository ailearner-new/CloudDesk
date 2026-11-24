---
title: "Enterprise Security Configuration"
category: "security"
tags: ["enterprise", "security", "sso", "scim", "compliance", "audit"]
summary: "Advanced security features for Enterprise: SSO, SCIM, audit logs, DLP, and compliance reporting."
---

# Enterprise Security Configuration

## Single Sign-On (SSO)

### Supported Protocols
- **SAML 2.0** — Okta, Azure AD, AD FS, PingIdentity, custom
- **OIDC** — Google, Microsoft, Auth0, Keycloak, custom

### Configuration
1. Admin → Security → SSO Configuration
2. Choose protocol
3. Enter IdP metadata (URL or XML)
4. Configure attribute mapping:
   - `email` (required)
   - `firstName`, `lastName`
   - `groups` (for role mapping)
5. Test with one user
6. Enable for all users

### Just-in-Time (JIT) Provisioning
- Auto-create users on first SSO login
- Map IdP groups → CloudDesk roles
- Deprovision on IdP removal (configurable)

### IdP-Initiated vs SP-Initiated
| Flow | Use Case |
|------|----------|
| SP-Initiated | User clicks "Login with SSO" on clouddesk.com |
| IdP-Initiated | User clicks CloudDesk tile in Okta/Azure portal |

Both supported. Configure ACS URL and Entity ID in IdP.

## SCIM Provisioning (Enterprise)

### Supported Operations
- `GET /scim/v2/Users` — list users
- `POST /scim/v2/Users` — create user
- `PATCH /scim/v2/Users/{id}` — update user
- `DELETE /scim/v2/Users/{id}` — deactivate user
- `GET /scim/v2/Groups` — list groups
- `POST /scim/v2/Groups` — create group

### Setup
1. Admin → Security → SCIM → Generate Token
2. Configure in IdP (Okta: "SCIM Provisioning")
3. Map attributes: `userName`=email, `displayName`=full name
4. Enable group push for role sync

### Role Mapping
| IdP Group | CloudDesk Role |
|-----------|----------------|
| `CloudDesk_Admins` | Admin |
| `CloudDesk_Members` | Member |
| `CloudDesk_Viewers` | Viewer |

Custom mapping available.

## Audit Log Enhancements (Enterprise)

### Extended Retention
- 7 years (vs 1 year Business)
- Immutable write-once storage
- Tamper-evident with hash chaining

### Real-Time Streaming
- Webhook: `POST /api/v1/webhooks/audit`
- Batch every 5 minutes or 1000 events
- Includes: actor, action, resource, outcome, IP, user-agent
- Signature: `X-CloudDesk-Signature` (HMAC-SHA256)

### SIEM Integration
Tested with: Splunk, Datadog, Sumo Logic, Elastic, Sentinel
Custom format available on request.

## Data Loss Prevention (DLP)

### Built-In Detectors
- Credit card numbers (Luhn validated)
- US SSN (format + checksum)
- API keys (AWS, GitHub, Stripe, generic)
- JWT tokens
- Custom regex patterns

### Rule Actions
| Action | Behavior |
|--------|----------|
| Block | Prevent upload/send, notify user |
| Quarantine | Allow but flag for admin review |
| Alert | Log only, notify admin |

### Scope
- File uploads and content
- Chat messages and comments
- Email notifications
- API payloads (optional)

### Configuration
Admin → Security → DLP Rules → Create Rule
- Name, description
- Detectors (built-in + custom)
- Actions per detector
- Scope: workspaces, users, file types

## Compliance Reporting

### Available Reports
| Report | Frequency | Format |
|--------|-----------|--------|
| SOC 2 Control Matrix | On demand | PDF, CSV |
| ISO 27001 Evidence | On demand | ZIP |
| GDPR Article 30 Record | Quarterly | PDF |
| Access Review Report | Monthly | CSV |
| DLP Incident Report | Weekly | CSV |

### Generation
Admin → Compliance → Reports → Generate
- Select report type, date range
- Ready within 24 hours
- Download from same page

### Data Processing Agreement
- Standard: clouddesk.com/dpa
- Custom: Enterprise only, contact legal@clouddesk.com
- Includes: SCCs, subprocessors, breach notification terms

## Data Residency (Enterprise)

### Available Regions
| Region | Data Center | Compliance |
|--------|-------------|------------|
| US East | Virginia | SOC 2, ISO |
| EU West | Frankfurt | GDPR, ISO |
| APAC | Singapore | ISO, PDPA |

### Configuration
- Selected at provisioning (cannot change later)
- All data: primary + backups in region
- Cross-region replication optional (extra cost)

## Related Articles
- [Security Best Practices](security-best-practices.md)
- [SSO Troubleshooting](sso-troubleshooting.md)
- [Account Deletion](account-deletion.md)
- [Audit Log Guide](audit-log.md)