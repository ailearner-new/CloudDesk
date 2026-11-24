---
title: "Subscription Management"
category: "billing"
tags: ["subscription", "plan", "upgrade", "downgrade", "renewal", "cancellation"]
summary: "Manage your CloudDesk subscription: upgrades, downgrades, renewals, cancellations, and payment methods."
---

# Subscription Management

## Plan Changes

### Upgrades
- **Effective immediately** — new features available right away
- **Prorated charge** — difference for remaining days in period
- **New limits apply** — storage, seats, API rate limits increase instantly

### Downgrades
- **Effective next billing cycle** — current period unchanged
- **No refund** for unused portion of current period
- **Limits reduce** at cycle boundary
- **Data preserved** — no deletion on downgrade

### Changing Plans
1. Settings → Billing → Change Plan
2. Select new plan, review changes
3. Confirm — immediate for upgrades, next cycle for downgrades
4. Receive confirmation email with new invoice

## Seat Management

### Adding Seats
- Available anytime
- Prorated from activation date
- New user can be invited immediately

### Removing Seats
- Takes effect next billing cycle
- User loses access at cycle boundary
- No credit for current period

### Seat Count vs. Active Users
- **Seats** = licensed capacity (what you pay for)
- **Active users** = logged in at least once this period
- You can have more seats than active users (buffer)
- Cannot have more active users than seats

## Billing Cycle

### Monthly vs. Annual
| Billing | Discount | Commitment |
|---------|----------|------------|
| Monthly | None | Month-to-month |
| Annual | 15% off | 12 months |

### Renewal
- Automatic on cycle date
- Payment method charged 24 hours before
- Invoice emailed on renewal
- 7-day grace period for failed payments

### Cancellation
1. Settings → Billing → Cancel Subscription
2. Choose: **End of period** (recommended) or **Immediate**
3. **End of period**: Access continues until cycle ends, no refund
4. **Immediate**: Access revoked, prorated refund for unused days (Enterprise only)

## Payment Methods

### Supported
- Credit/Debit cards (Visa, Mastercard, Amex)
- ACH/Bank transfer (Business, Enterprise)
- Invoice/Net-30 (Enterprise only)

### Updating Payment Method
1. Settings → Billing → Payment Method
2. Add new card/bank account
3. Set as default
4. Remove old method (optional)

### Failed Payments
- Retry: 24h, 48h, 72h after initial failure
- After 72h: account suspended (read-only)
- Reactivate: update payment method, auto-retries
- After 30 days suspended: data archived

## Invoices

### Accessing Invoices
- Settings → Billing → Invoices
- Download PDF
- Email copy sent on each charge

### Invoice Details
- Plan, seats, period
- Prorated adjustments
- Taxes (based on billing address)
- Payment status

### Tax Exemption
- Enterprise: upload exemption certificate
- Settings → Billing → Tax Exemption
- Applied to future invoices

## Enterprise: Volume Discounts

| Seats | Discount |
|-------|----------|
| 100-249 | 5% |
| 250-499 | 10% |
| 500-999 | 15% |
| 1000+ | Custom |

Contact sales for custom Enterprise agreements.

## Related Articles
- [Billing and Refund Policy](billing-refunds.md)
- [Payment Methods](payment-methods.md)
- [Invoice Understanding](invoice-understanding.md)
- [API Rate Limits](api-rate-limits.md)