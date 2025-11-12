# VIP Status Segmentation Rules

## Current Segmentation (Updated 2025-11-06)

| Visits | Status | Description |
|--------|--------|-------------|
| 0 | New | No completed transactions |
| 1 | First | First-time customer |
| 2-4 | Casual | Casual visitor |
| 5-10 | Regular1 | Regular customer (Tier 1) |
| 11-15 | Regular2 | Regular customer (Tier 2) |
| 16+ | VIP | VIP customer |

## Implementation Locations

1. **Database Backfill**: `sql_scripts/HYBRID_SOLUTION_step1_backfill.sql`
   - Lines 63-69: CASE statement for vip_status calculation
   - Re-run this to update existing customer statuses

2. **Viewer Fallback**: `mota-crm/viewers/crm_integrated_blaze_v5.py`
   - Used only by `setup_viewer_v5.py` API method (slow fallback)
   - Lines in the API-based backfill section

## To Update All Customers

Run this in Supabase SQL Editor:

```sql
UPDATE customers_blaze c
SET vip_status = CASE 
    WHEN c.total_visits >= 16 THEN 'VIP'
    WHEN c.total_visits BETWEEN 11 AND 15 THEN 'Regular2'
    WHEN c.total_visits BETWEEN 5 AND 10 THEN 'Regular1'
    WHEN c.total_visits BETWEEN 2 AND 4 THEN 'Casual'
    WHEN c.total_visits = 1 THEN 'First'
    ELSE 'New'
END;
```

## Marketing Strategy by Segment

- **New (0)**: Welcome campaigns, first-visit incentives
- **First (1)**: Come back campaigns, loyalty program signup
- **Casual (2-4)**: Engagement campaigns, product recommendations
- **Regular1 (5-10)**: Appreciation rewards, referral incentives
- **Regular2 (11-15)**: Premium perks, early access to new products
- **VIP (16+)**: Exclusive events, personalized service, highest rewards

