# Smart Duplicate Customer Merger - Guide

## What It Does

The `SMART_MERGE_DUPLICATES.sql` script intelligently finds and merges duplicate customer records using multiple matching criteria:

### Matching Logic:
1. **First Name + Last Name** (case-insensitive, trimmed)
2. **Date of Birth** (if available)
3. **Phone Number** (if available)

### Merge Priority:
Records are ranked by completeness:
- Phone exists: +100 points
- Email exists: +50 points
- Total visits: +10 points per visit
- Date joined exists: +5 points

**Highest scoring record = KEEPER**

---

## How to Use

### Step 1: Analyze Duplicates
Run the script in Supabase SQL Editor - it will show:
- How many duplicate groups exist
- Which record will be kept (highest score)
- Which records will be merged

### Step 2: Review the Plan
Look at the output:
```
CUSTOMER NAME         | KEEP THIS ID              | MERGE THESE IDS
stephen clare         | 61394100d18e30747f2b67f7 | [683cea4e022c82ba434de1df]
luis bobadilla        | 5b78a490062bd807d595fb86 | [5be228de062bd807c2323085, ...]
```

### Step 3: Run the Merge
The script automatically:
1. Copies missing data from duplicates to the "keeper"
2. Updates phone, email, address if missing
3. Preserves all opt-in preferences
4. Logs what was merged

### Step 4: Delete Empty Duplicates (Optional)
Uncomment the DELETE section to remove duplicates that are now truly empty (no phone, no email, no visits).

---

## What Gets Merged

From duplicate records, copies to main record if missing:
- ✅ Phone number
- ✅ Email address
- ✅ Street address
- ✅ City, State, ZIP
- ✅ SMS opt-in
- ✅ Email opt-in

**Does NOT merge:**
- ❌ Transactions (stay with original member_id)
- ❌ Visit counts (already calculated)
- ❌ Member ID (each record keeps its own)

---

## Safety Features

1. **Non-destructive merge**: Original records preserved until you run DELETE step
2. **Only merges NULL fields**: Never overwrites existing data
3. **Logs everything**: Shows what was merged in console
4. **Verification query**: Shows remaining duplicates after merge

---

## Example Output

```
MERGE COMPLETE: 47 records merged
===========================================

Merged: stephen clare (683cea4e022c82ba434de1df) into 61394100d18e30747f2b67f7
Merged: luis bobadilla (5be228de062bd807c2323085) into 5b78a490062bd807d595fb86
Merged: clarence white (abc123...) into def456...
...
```

---

## After Running

1. **Refresh Manual Conductor**: Click "📇 Refresh Contacts" to reload
2. **Refresh IC Viewer**: Restart to see merged data
3. **Check results**: Search for customers that were merged

---

## Troubleshooting

### "Still seeing duplicates"
- They might have different DOBs
- Run with DOB matching disabled (remove from PARTITION BY)

### "Wrong record was kept"
- Adjust the scoring logic in ORDER BY clause
- Give more weight to phone vs email vs visits

### "Lost data"
- Merge only copies NULL → value, never overwrites
- Original records still exist until you run DELETE

---

## Advanced: Custom Merge Rules

Edit the ORDER BY section to change priority:

```sql
ORDER BY 
    CASE WHEN c.phone IS NOT NULL THEN 1000 ELSE 0 END +  -- Phone = highest priority
    CASE WHEN c.email IS NOT NULL THEN 50 ELSE 0 END +
    COALESCE(c.total_visits, 0) * 1 +  -- Visits = low priority
    CASE WHEN c.date_joined IS NOT NULL THEN 5 ELSE 0 END
DESC
```

---

## Questions?

Run `find_duplicate_customers.sql` first to just SEE duplicates without merging anything.

