---
title: "Understanding Your Invoice"
category: "billing"
tags: ["invoice", "billing", "charges", "tax", "payment"]
summary: "Breakdown of CloudDesk invoice line items, taxes, prorations, and how to read your bill."
---

# Understanding Your Invoice

## Invoice Structure

### Header
- **Invoice Number**: Unique identifier (e.g., `INV-2026-001234`)
- **Date**: Invoice generation date
- **Period**: Billing period covered
- **Customer**: Your company name and billing address
- **Payment Terms**: Net-30 (Enterprise) or Due on Receipt

### Line Items

#### Subscription Charges
```
CloudDesk Business Plan          10 seats × $35.00 = $350.00
  Period: Jan 1 – Jan 31, 2026
```

#### Seat Adjustments (Prorated)
```
Seat Addition (Pro-rated)        3 seats × $35.00 × 15/30 = $52.50
  Added: Jan 16, 2026
```

#### Storage Overage (if applicable)
```
Storage Overage                  50 GB × $0.10/GB = $5.00
  Limit: 1 TB, Used: 1.05 TB
```

#### Add-ons
```
Advanced Security Add-on         1 × $200.00 = $200.00
  Period: Jan 1 – Jan 31, 2026
```

### Taxes
- Calculated based on **billing address**
- Shown as separate line items
- US: State + local sales tax
- EU/UK: VAT (reverse charge for B2B with valid VAT ID)

### Total
```
Subtotal:          $607.50
Tax (8.5%):        $51.64
Total:             $659.14
```

## Common Line Items Explained

### "Prorated Charge"
You added seats or upgraded mid-cycle. Charge covers only the remaining days.

### "Prorated Credit"
You removed seats or downgraded. Credit applies to **next** invoice.

### "Storage Overage"
Workspace exceeded plan storage limit. $0.10/GB/month over limit.

### "API Overage"
Exceeded plan's API rate limit. Enterprise only (others are blocked).

### "Support Add-on"
Priority support tier (Business/Enterprise).

## Payment Information

### Automatic Payment
- Charged to default payment method on invoice date
- Receipt emailed within 1 hour
- Failed payment → retry schedule (see Payment Methods)

### Manual Payment (Enterprise Net-30)
- Pay within 30 days of invoice date
- Methods: ACH, Wire, Check
- Reference invoice number on payment

## Disputing a Charge

1. Review invoice details in Settings → Billing → Invoices
2. Compare with plan and usage
3. Contact support with:
   - Invoice number
   - Specific line item
   - Reason for dispute
4. Disputed amount held until resolution (max 30 days)

## Invoice History

- All invoices: Settings → Billing → Invoices
- Download PDF
- API: `GET /api/v1/billing/invoices`
- Retention: 7 years (all plans)

## Related Articles
- [Billing and Refund Policy](billing-refunds.md)
- [Payment Methods](payment-methods.md)
- [Subscription Management](subscription-management.md)
- [Tax Settings](payment-methods.md#tax-settings)