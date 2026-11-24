---
title: "API Authentication"
category: "api_failure"
tags: ["api", "authentication", "tokens", "oauth", "jwt"]
summary: "Authenticate to the CloudDesk API using API keys, OAuth, or JWT tokens."
---

# API Authentication

## Authentication Methods

### 1. API Keys (Recommended for Server-to-Server)
- **Scope**: Workspace-level
- **Format**: `cdsk_live_...` or `cdsk_test_...`
- **Management**: Settings → API Keys
- **Rotation**: Generate new, revoke old (no downtime)

### 2. OAuth 2.0 (For User-Authenticated Apps)
- **Flow**: Authorization Code with PKCE
- **Scopes**: `read`, `write`, `admin`
- **Redirect URI**: Must be pre-registered
- **Token lifetime**: 1 hour (access), 30 days (refresh)

### 3. JWT Bearer Tokens (For SSO-Integrated Apps)
- **Source**: Your IdP after SSO login
- **Validation**: CloudDesk validates signature and claims
- **Required claims**: `sub`, `email`, `exp`, `aud`
- **Audience**: `https://api.clouddesk.com`

## Using API Keys

### Header Format
```
Authorization: Bearer cdsk_live_abc123...
```

### Creating an API Key
1. Settings → API Keys → Create Key
2. Name it (e.g., "Nightly Sync Job")
3. Select scopes
4. Copy immediately — **shown once only**

### Scopes
| Scope | Permissions |
|-------|-------------|
| `read` | GET endpoints only |
| `write` | POST/PATCH/DELETE on tickets, files, comments |
| `admin` | Workspace settings, members, billing |

### Best Practices
- Use separate keys per integration
- Label keys clearly
- Rotate quarterly (Settings → API Keys → Rotate)
- Revoke compromised keys immediately

## Using OAuth

### Authorization URL
```
https://clouddesk.com/oauth/authorize?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=https://yourapp.com/callback&
  response_type=code&
  scope=read write&
  state=RANDOM_STRING&
  code_challenge=BASE64URL_ENCODE(SHA256(code_verifier))&
  code_challenge_method=S256
```

### Token Exchange
```bash
POST https://api.clouddesk.com/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTH_CODE&
redirect_uri=https://yourapp.com/callback&
code_verifier=ORIGINAL_VERIFIER&
client_id=YOUR_CLIENT_ID
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "rt_...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read write"
}
```

### Refreshing Tokens
```bash
POST https://api.clouddesk.com/oauth/token
grant_type=refresh_token&
refresh_token=rt_...&
client_id=YOUR_CLIENT_ID
```

## Using JWT from SSO

### After IdP Login
Your IdP returns an ID token. Send it to CloudDesk:

```bash
POST https://api.clouddesk.com/auth/sso
Content-Type: application/json

{ "id_token": "eyJ...", "workspace_id": "ws-123" }
```

Response:
```json
{
  "access_token": "cdsk_jwt_...",
  "token_type": "Bearer",
  "expires_in": 28800
}
```

### Token Validation
CloudDesk validates:
- Signature (RS256 from IdP JWKS)
- `exp` (not expired)
- `aud` (matches CloudDesk client ID)
- `email` (verified in IdP)

## Error Responses

| Status | Code | Meaning |
|--------|------|---------|
| 401 | `invalid_token` | Expired, malformed, or revoked |
| 401 | `insufficient_scope` | Token lacks required scope |
| 403 | `workspace_access_denied` | Token valid but no access to workspace |
| 429 | `rate_limited` | Too many auth attempts |

## Security Best Practices

- **Never** commit API keys to version control
- **Never** log full tokens
- Use short-lived tokens for user-facing apps
- Store secrets in environment variables or secret managers
- Monitor API key usage in Audit Log

## Related Articles
- [API Rate Limits](api-rate-limits.md)
- [Webhook Configuration](webhook-configuration.md)
- [Enterprise Security](enterprise-security.md)
- [Audit Log Guide](audit-log.md)