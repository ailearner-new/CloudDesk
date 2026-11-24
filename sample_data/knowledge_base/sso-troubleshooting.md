---
title: "SSO Troubleshooting Guide"
category: "login_issue"
tags: ["sso", "saml", "oidc", "okta", "enterprise"]
summary: "Diagnose and fix SSO login failures including SAML response validation errors, certificate issues, and clock skew."
---

# SSO Troubleshooting Guide

## Diagnosis

### SAML Response Validation Failed

This error typically indicates one of the following issues:

1. **IdP Certificate Expired or Rotated** — The Identity Provider's signing certificate has expired or was rotated without updating CloudDesk.
2. **Clock Skew** — The time difference between the IdP and CloudDesk servers exceeds 5 minutes.
3. **Audience/Entity ID Mismatch** — The SAML response's AudienceRestriction doesn't match CloudDesk's configured Entity ID.
4. **Assertion Consumer Service URL Mismatch** — The ACS URL in the SAML request doesn't match what's configured in the IdP.

### Verification Steps

1. **Check IdP Certificate Expiry**
   - Download the current certificate from your IdP (Okta, Azure AD, etc.)
   - Verify the `NotAfter` date hasn't passed
   - If rotated, update the certificate in CloudDesk Admin → SSO Settings

2. **Verify Clock Synchronization**
   - Ensure both IdP and CloudDesk servers use NTP
   - Maximum allowed skew: 5 minutes
   - Check with `ntpdate -q pool.ntp.org` on both systems

3. **Validate SAML Response**
   - Use a SAML tracer browser extension to capture the response
   - Verify `AudienceRestriction` contains `https://clouddesk.com/sso/saml/metadata`
   - Verify `Recipient` and `Destination` match your ACS URL

4. **Check IdP Configuration**
   - Ensure NameID format is `urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress`
   - Verify required attributes: `email`, `firstName`, `lastName`
   - Confirm the IdP sends `SessionNotOnOrAfter` with reasonable lifetime

## Resolution

### For Certificate Issues
1. Obtain the new certificate from your IdP administrator
2. Navigate to CloudDesk Admin → Security → SSO Configuration
3. Paste the new certificate (X.509 PEM format)
4. Save and test with a single user before rolling out

### For Clock Skew
1. Ensure NTP is running on all servers
2. Consider using a shared NTP pool
3. If skew persists, contact CloudDesk support to adjust tolerance (Enterprise only)

### For Configuration Mismatches
1. Compare IdP and CloudDesk configurations side-by-side
2. Ensure Entity ID, ACS URL, and SLO URL match exactly
3. Re-import metadata if using dynamic metadata exchange

## Prevention

- Set calendar reminders for certificate expiry (30 days before)
- Enable automated certificate rotation where supported (Okta, Azure AD)
- Monitor SSO health via `/health/ready` endpoint
- Configure alerts for authentication failure rate spikes

## Related Articles
- [MFA Recovery Guide](mfa-recovery.md)
- [API Rate Limits](api-rate-limits.md)
- [Enterprise Security Best Practices](enterprise-security.md)