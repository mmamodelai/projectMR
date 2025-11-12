# DELETE BACKUP TABLES NOW

## Quick Steps (30 seconds):

1. **Open Supabase SQL Editor**
   - Go to: https://supabase.com/dashboard/project/kiwmwoqrguyrcpjytgte/sql/new

2. **Copy this SQL:**

```sql
DROP TABLE IF EXISTS public.blaze_api_samples CASCADE;
DROP TABLE IF EXISTS public.blaze_sync_state CASCADE;
VACUUM ANALYZE;
```

3. **Paste into SQL Editor**

4. **Click RUN**

5. **Done!** Tables deleted, space freed.

---

**That's it. Takes 30 seconds.**

