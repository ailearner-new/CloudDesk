---
title: "Payment Methods and Billing"
category: "billing"
tags: ["payment", "billing", "cards", "ach", "invoices", "tax"]
summary: "Supported payment methods, updating billing information, handling failed payments, and tax settings."
---

# Payment Methods and Billing

## Supported Payment Methods

### Credit/Debit Cards
- **Accepted**: Visa, Mastercard, American Express, Discover
- **Processing**: Secure tokenization via Stripe
- **Currency**: USD (other currencies on Enterprise)
- **Receipts**: Automatic email on each charge

### ACH/Bank Transfer
- **Plans**: Business, Enterprise
- **Setup**: Settings → Billing → Add Bank Account
- **Verification**: Micro-deposits (1-2 business days)
- **Preferred for**: Annual invoices > $5,000

### Invoice/Net-30 Terms
- **Plan**: Enterprise only
- **Requirements**: Approved credit application
- **Payment**: Within 30 days of invoice date
- **Late fees**: 1.5%/month after 30 days

## Managing Payment Methods

### Adding a Payment Method
1. Settings → Billing → Payment Methods
2. Click **Add Payment Method**
3. Choose type: Card or Bank Account
4. Enter details securely (hosted fields)
5. Set as default (optional)

### Updating Default Payment Method
- New method automatically becomes default
- Previous default remains as backup
- Remove old methods anytime (keep at least one)

### Removing Payment Methods
- Cannot remove last payment method
- Must add replacement first
- Removed methods cannot be recovered

## Failed Payment Handling

### Retry Schedule
| Attempt | Timing | Action |
|---------|--------|--------|
| 1 | 24 hours | Retry same method |
| 2 | 48 hours | Retry, notify admin |
| 3 | 72 hours | Retry, suspend if fails |

### Account Suspension
- After 3 failed retries: **read-only mode**
- Users can view/export data, cannot create/edit
- Billing admin receives daily reminders
- Reactivation: update payment method → auto-retry

### Data Archival
- After 30 days suspended: data archived to cold storage
- Recovery: contact support, $500 fee, 5 business days
- After 90 days archived: permanent deletion

## Tax Settings

### Tax Calculation
- Based on **billing address** (not workspace location)
- Automatic via Stripe Tax
- Updated monthly for rate changes

### Tax Exemption
- **Enterprise only**: Upload exemption certificate
- Settings → Billing → Tax Exemption → Upload
- Validated within 2 business days
- Applied to future invoices only

### VAT (EU/UK Customers)
- Reverse charge for B2B (valid VAT ID required)
- Consumer VAT applied based on country
- VAT ID validation via VIES

## Invoices

### Invoice Schedule
- **Monthly**: 1st of each month
- **Annual**: Anniversary of signup
- **Prorated**: Mid-cycle changes

### Invoice Contents
- Plan name and seat count
- Period covered
- Prorated adjustments (upgrades/add-ons)
- Taxes and fees
- Payment status

### Accessing Invoices
- Settings → Billing → Invoices
- Download PDF
- Email copy sent automatically
- API: `GET /api/v1/billing/invoices`

## Billing Address

### Updating Billing Address
1. Settings → Billing → Billing Address
2. Enter complete address
3. Save — affects next invoice's tax calculation

### Multiple Billing Entities (Enterprise)
- Separate invoices per entity
- Configure: Admin → Billing → Entities
- Each has own payment method, address, tax settings

## Related Articles
- [Billing and Refund Policy](billing-refunds.md)
- [Subscription Management](subscription-management.md)
- [Invoice Understanding](invoice-understanding.md)
- [Enterprise Security Best Practices](security-best-practices.md)