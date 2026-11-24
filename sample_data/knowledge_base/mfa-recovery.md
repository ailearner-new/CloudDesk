---
title: "MFA Recovery Guide"
category: "login_issue"
tags: ["mfa", "recovery", "totp", "webauthn", "backup-codes"]
summary: "Recover access to your account when you lose your authenticator app or hardware key."
---

# MFA Recovery Guide

## Recovery Options (in order of preference)

### 1. Backup Codes (Recommended)
Every user receives 10 backup codes when enabling MFA.
- **Use once** — each code works only once
- **Store securely** — password manager or printed in safe place
- **Regenerate** — Admin → Security → MFA → Regenerate Backup Codes

### 2. Secondary MFA Method
If you configured multiple methods (e.g., TOTP + WebAuthn):
- Use the alternate method at login
- WebAuthn (security key, Touch ID, Windows Hello) works without phone

### 3. Admin-Assisted Recovery (Enterprise Only)
Enterprise admins can initiate recovery for team members:
1. Admin → Members → [User] → Reset MFA
2. User receives email with one-time recovery link
3. Link expires in 1 hour
4. User sets up new MFA method

### 4. Support-Assisted Recovery
If no backup codes, no secondary method, and not on Enterprise:
1. Contact support from registered email
2. Verify identity (may require video call for Enterprise)
3. Support resets MFA — **all existing sessions revoked**
4. User sets up new MFA on next login

## Step-by-Step: Using Backup Codes

1. Go to login.clouddesk.com
2. Enter email and password
3. On MFA screen, click **"Use backup code"**
4. Enter one 8-digit code
5. **Immediately** set up new MFA method (Settings → Security)

## Step-by-Step: WebAuthn Recovery

If you have a registered security key:
1. Insert security key (USB/NFC/Bluetooth)
2. Touch/activate when prompted
3. No authenticator app needed

## Preventing Lockout

### Do:
- ✅ Save backup codes in password manager
- ✅ Register multiple MFA methods (TOTP + WebAuthn)
- ✅ Use cloud-synced authenticator (1Password, Bitwarden, Google Authenticator sync)
- ✅ Register a hardware security key (YubiKey, Titan)

### Don't:
- ❌ Rely on single phone with no backup
- ❌ Store backup codes only on the same device
- ❌ Ignore "regenerate codes" prompts after using several

## For Admins (Enterprise)

### View Member MFA Status
- Admin → Members → MFA column shows: **Enabled**, **Not Enabled**, **Recovery Needed**

### Enforce MFA
- Admin → Security → Require MFA for all members
- Grace period: 7 days for existing members

### Bulk MFA Reset
- Select multiple members → Actions → Reset MFA
- Each receives individual recovery email

## Troubleshooting

### "Backup code says invalid"
- Codes are single-use — check if already used
- Ensure no typos (8 digits, no spaces)
- Try next code in sequence

### "Security key not working"
- Ensure key is registered to this account
- Try different USB port / NFC position
- Update key firmware (YubiKey Manager)

### "Recovery email not arriving"
- Check spam/junk folder
- Verify email address in profile
- Contact support if email changed recently

## Related Articles
- [SSO Troubleshooting Guide](sso-troubleshooting.md)
- [Enterprise Security Best Practices](enterprise-security.md)
- [Account Security Settings](account-security.md)