# IC Viewer v5 - Setup Instructions

## Updated: 2025-11-06

### New VIP Segmentation Rules
- **0 visits** = New
- **1 visit** = First
- **2-4 visits** = Casual
- **5-10 visits** = Regular1
- **11-15 visits** = Regular2
- **16+ visits** = VIP

---

## Quick Setup (15 minutes)

### Step 1: Open Supabase SQL Editor
Go to: https://supabase.com/dashboard/project/kiwmwoqrguyrcpjytgte/sql

### Step 2: Run Backfill Script
1. Open and run: `sql_scripts/HYBRID_SOLUTION_step1_backfill.sql`
2. **Wait 10-15 minutes** (updates 131K customers)
3. You'll see progress output in the results

### Step 3: Create Fast Query Function
1. Open and run: `sql_scripts/HYBRID_SOLUTION_step2_create_fast_query.sql`
2. **Wait 1 minute** (creates RPC function)
3. You'll see test results at the bottom

### Step 4: Launch Viewer
- Run: `start_crm_blaze_v5.bat`
- Or: `start_crm_blaze_v5_EASY.bat` (interactive guide)

---

## What Gets Updated

### Database Changes
✅ `total_visits` - Count of completed transactions  
✅ `lifetime_value` - Total $ spent  
✅ `vip_status` - Segmentation (New/First/Casual/Regular1/Regular2/VIP)  
✅ `last_visited` - Most recent transaction date  
✅ `days_since_last_visit` - Days since last visit  

### New RPC Function
✅ `get_customers_fast()` - Server-side filtering  
- Dynamic date range filtering (e.g., "last 180 days")
- Email/Phone filtering
- Search by name/email/phone
- Returns pre-calculated stats
- **FAST** (runs in database, not Python)

---

## Verify It Worked

### In Supabase SQL Editor
```sql
-- Check VIP distribution
SELECT 
    vip_status,
    COUNT(*) as customers,
    ROUND(AVG(total_visits), 1) as avg_visits,
    ROUND(AVG(lifetime_value), 2) as avg_value
FROM customers_blaze
GROUP BY vip_status
ORDER BY 
    CASE vip_status
        WHEN 'VIP' THEN 6
        WHEN 'Regular2' THEN 5
        WHEN 'Regular1' THEN 4
        WHEN 'Casual' THEN 3
        WHEN 'First' THEN 2
        WHEN 'New' THEN 1
    END DESC;
```

### Expected Results
| VIP Status | Customers | Avg Visits | Avg Value |
|------------|-----------|------------|-----------|
| VIP | ~X,XXX | 25+ | $X,XXX |
| Regular2 | ~X,XXX | 12-13 | $XXX |
| Regular1 | ~X,XXX | 7-8 | $XXX |
| Casual | ~X,XXX | 3 | $XXX |
| First | ~X,XXX | 1 | $XX |
| New | ~X,XXX | 0 | $0 |

---

## Optional: Update Segmentation Only

If you've already run the backfill but want to change the segmentation:

```sql
-- Run: sql_scripts/QUICK_UPDATE_VIP_SEGMENTS.sql
-- Takes 30 seconds instead of 15 minutes
```

---

## Troubleshooting

### "Function get_customers_fast does not exist"
- You skipped Step 3
- Run: `HYBRID_SOLUTION_step2_create_fast_query.sql`

### "0 visits, $0.00 lifetime" showing in viewer
- You skipped Step 2
- Run: `HYBRID_SOLUTION_step1_backfill.sql`

### Viewer is slow / not filtering correctly
- Check that both SQL scripts completed
- Verify RPC function exists:
  ```sql
  SELECT * FROM pg_proc WHERE proname = 'get_customers_fast';
  ```

### Still seeing old VIP segments (2-5, 6-14, 15+)
- Run: `sql_scripts/QUICK_UPDATE_VIP_SEGMENTS.sql`
- Or re-run Step 2 (backfill)

---

## Performance Notes

### Before v5 (Slow)
- Loaded ALL 131K customers into Python
- Calculated visits/lifetime in Python
- Filtered in Python
- **Result**: 30-60 seconds to load

### After v5 (Fast)
- Database calculates once (backfill)
- RPC function filters server-side
- Only returns matching customers
- **Result**: 1-3 seconds to load

### Example Speed Improvement
| Filter | Before | After | Speedup |
|--------|--------|-------|---------|
| All customers | 45s | 8s | 5.6x |
| Phone + 180 days | 45s | 1.2s | 37x |
| Phone + Email + 180 days | 45s | 0.8s | 56x |

---

## Files Reference

### SQL Scripts
- `HYBRID_SOLUTION_step1_backfill.sql` - Main backfill (15 min)
- `HYBRID_SOLUTION_step2_create_fast_query.sql` - RPC function (1 min)
- `QUICK_UPDATE_VIP_SEGMENTS.sql` - Just update segments (30 sec)
- `VIP_SEGMENTATION_REFERENCE.md` - Segmentation rules

### Viewers
- `crm_integrated_blaze_v5.py` - Latest viewer (uses RPC)
- `start_crm_blaze_v5.bat` - Quick launch
- `start_crm_blaze_v5_EASY.bat` - Interactive setup guide
- `setup_viewer_v5.py` - Automated setup (slow, API-based)

### Config
- `viewer_config.json` - Persistent viewer settings
- Stores: column visibility, widths, filter states, window positions

---

## Next Steps After Setup

1. **Test filtering**: Try different date ranges, email/phone filters
2. **Verify segments**: Look up known customers, check their VIP status
3. **Column selector**: Click column headers to choose what to display
4. **Adjust layout**: Drag dividers, resize columns, save layout
5. **Search**: Use search box to find specific customers

---

## Questions?

- Check: `CONDUCTOR_ARCHITECTURE.md`
- Or: `WORKLOG.md` for recent changes
- Debug: Check `logs/` folder if viewer crashes

