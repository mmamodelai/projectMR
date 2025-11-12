# Safe Duplicate Customer Merge Process

**Created**: 2025-11-06  
**Purpose**: Complete guide to safely merging duplicate customer records  
**Estimated Time**: 10-20 minutes

---

## ⚠️ CRITICAL: Follow These Steps IN ORDER

### **Step 1: Backup Your Data (2 minutes)**

**File**: `sql_scripts/BACKUP_customers_before_merge.sql`

**What it does:**
- Creates `customers_blaze_backup_20251106` table
- Copies ALL customer data (every field, every record)
- Adds indexes to backup for fast restore
- Reports backup statistics

**How to run:**
1. Open Supabase SQL Editor
2. Paste the entire `BACKUP_customers_before_merge.sql` file
3. Click "Run"
4. Wait for completion (~30 seconds)

**Expected output:**
```
status: BACKUP COMPLETE!
original_count: 10,847
backup_count: 10,847
original_size: 2.1 MB
backup_size: 2.1 MB
```

**✅ If counts match**: Continue to Step 2  
**❌ If counts DON'T match**: STOP! Something's wrong. Contact support.

---

### **Step 2: Check What Will Be Merged (1 minute)**

**File**: `sql_scripts/FAST_FIND_DUPLICATES.sql`

**What it does:**
- Counts how many duplicate groups exist
- Shows total records that will be merged
- No changes made (read-only)

**Expected output:**
```
total_customers: 10,847
unique_customers: 10,104
duplicate_records: 743
duplicate_groups: 328
```

**Example**: If you have 328 duplicate groups with 743 total records:
- You'll end up with 10,104 clean records
- 328 "keeper" records will absorb data from 743 duplicates
- 743 duplicate records will be deleted

---

### **Step 3: Merge Duplicates (5-15 minutes)**

**File**: `sql_scripts/FULL_MERGE_DUPLICATES.sql`

**What it does** (for each duplicate group):
1. **Picks best record** (most complete data) as KEEPER
2. **Copies missing data** from duplicates to keeper:
   - Phone, email, address
   - Birthday, opt-in preferences
3. **MOVES ALL TRANSACTIONS** from duplicates to keeper
4. **Recalculates keeper stats**:
   - Total visits (now includes ALL transactions!)
   - Lifetime value (sum of everything)
   - VIP status (based on new visit count)
5. **DELETES empty duplicate records**

**How to run:**
1. Open Supabase SQL Editor
2. Paste `FULL_MERGE_DUPLICATES.sql`
3. Click "Run"
4. **Wait for output** (~5-10 seconds)
5. Check output:
   - Shows how many groups processed
   - Shows how many duplicates deleted
6. **Run again** if output says records were processed
7. **Keep running** until output shows "0 customer groups processed"

**Expected output (first run):**
```
Processing group 1/20: medgo artea drots
  Keeper ID: 12345 (has phone + email)
  Moved 147 transactions from customer 12346
  Deleted duplicate customer 12346
  Moved 52 transactions from customer 12347
  Deleted duplicate customer 12347
  ... (repeats for all 30 duplicates)
  Updated keeper: 199 total visits, $4,521.00 lifetime value
  
Processed 20 customer groups
Deleted 67 duplicate records
```

**Keep running until you see:**
```
No duplicate customer groups found.
Processed 0 customer groups.
```

---

### **Step 4: Verify Everything Worked (2 minutes)**

**File**: `sql_scripts/COUNT_ALL_DUPLICATES.sql`

**What it does:**
- Counts remaining duplicates (should be 0!)
- Shows before/after comparison

**Expected output:**
```
before_backup: 10,847 customers (743 duplicates)
after_merge: 10,104 customers (0 duplicates)
records_removed: 743
duplicate_groups_remaining: 0
```

**✅ If duplicates = 0**: SUCCESS! Continue to Step 5  
**❌ If duplicates > 0**: Run `FULL_MERGE_DUPLICATES.sql` again (you might have missed some)

---

### **Step 5: Test Your Viewers (3 minutes)**

**Test Manual Conductor:**
1. Run `mota-crm/viewers/start_manual_conductor.bat`
2. Search for "Stephen Clare" (was a known duplicate)
3. Verify his phone number shows up
4. Check conversation loads correctly
5. Verify customer details panel shows correct data

**Test IC Viewer:**
1. Run `mota-crm/viewers/start_crm_blaze_v5.bat`
2. Search for customers that were duplicates
3. Verify transaction counts are correct
4. Check lifetime value makes sense
5. Verify VIP status is accurate

**✅ If everything looks good**: You're done! 🎉  
**❌ If something looks wrong**: Continue to Step 6 (restore from backup)

---

## 🚨 Emergency: Something Went Wrong

### **Step 6: Restore From Backup**

**File**: `sql_scripts/RESTORE_customers_from_backup.sql`

**What it does:**
- Deletes current (messed up) `customers_blaze` table
- Restores from `customers_blaze_backup_20251106`
- Recreates all indexes
- Verifies restoration

**How to run:**
1. Open Supabase SQL Editor
2. Paste `RESTORE_customers_from_backup.sql`
3. Click "Run"
4. Wait for completion (~1 minute)

**Expected output:**
```
status: RESTORATION COMPLETE!
total_customers: 10,847
unique_members: 10,104
total_visits: 45,239
```

**After restore:**
- Your data is exactly as it was before
- No changes were made
- You can investigate what went wrong
- Try again when ready

---

## 📊 What This Process Achieves

### **Before Merge:**
- 10,847 total customer records
- 743 duplicate records (same person, multiple records)
- 328 people with 2+ records each
- Example: "Stephen Clare" has 2 records (one with phone, one without)

### **After Merge:**
- 10,104 clean customer records
- 0 duplicates
- Every person has 1 record with ALL their data
- Example: "Stephen Clare" has 1 record with phone, email, all transactions

### **Data Preservation:**
- ✅ All transactions moved to keeper
- ✅ All phone/email data preserved
- ✅ All opt-in preferences preserved
- ✅ All purchase history intact
- ✅ Lifetime value recalculated accurately
- ✅ VIP status updated correctly

---

## 🔍 Example: "medgo artea drots" (30 Records → 1 Record)

### **Before Merge:**
```
Record 1: medgo artea drots | Phone: +1234567890 | Email: none | 12 visits
Record 2: medgo artea drots | Phone: none | Email: m@example.com | 8 visits
Record 3: medgo artea drots | Phone: none | Email: none | 5 visits
... (27 more records)
Total: 30 records, 199 visits, $4,521 lifetime value (split across 30 records)
```

### **After Merge:**
```
Record 1: medgo artea drots | Phone: +1234567890 | Email: m@example.com | 199 visits | $4,521 LTV | VIP
```

**What happened:**
1. Script picked Record 1 as keeper (had phone)
2. Copied email from Record 2
3. Moved all 199 transactions to Record 1
4. Recalculated: 199 visits → VIP status
5. Deleted Records 2-30 (now empty)

---

## 🎯 Success Criteria

### **You know it worked if:**
1. ✅ `COUNT_ALL_DUPLICATES.sql` shows 0 duplicates
2. ✅ Manual Conductor finds all customers by phone
3. ✅ IC Viewer shows accurate transaction counts
4. ✅ Customer lifetime values look reasonable
5. ✅ VIP statuses match visit counts
6. ✅ No customers "disappeared" from viewers
7. ✅ All conversation histories load correctly

### **Red flags (restore from backup):**
1. ❌ Customers missing from viewers
2. ❌ Transaction counts look way off
3. ❌ Lifetime values are $0 or incorrect
4. ❌ Conversations not loading
5. ❌ Error messages in SQL output

---

## 📞 Need Help?

**If you see any of these:**
- SQL errors during merge
- Duplicate count not decreasing
- Customers disappearing
- Transaction data looks wrong
- Viewers not loading customers

**STOP and restore from backup first!**

Then investigate:
1. Check `customers_blaze_backup_20251106` still exists
2. Check Supabase logs for errors
3. Run diagnostic scripts to see what changed
4. Contact support with error details

---

## 🗑️ Cleanup (After Successful Merge)

**Once you've verified everything works for 1-2 days:**

```sql
-- Delete the backup table (frees up space)
DROP TABLE customers_blaze_backup_20251106;
```

**Don't rush this!** Keep the backup for at least a week to be safe.

---

## 📝 Post-Merge Checklist

- [ ] Ran `BACKUP_customers_before_merge.sql` successfully
- [ ] Backup count matches original count
- [ ] Ran `FAST_FIND_DUPLICATES.sql` to see what will change
- [ ] Ran `FULL_MERGE_DUPLICATES.sql` until 0 groups remaining
- [ ] Ran `COUNT_ALL_DUPLICATES.sql` - shows 0 duplicates
- [ ] Tested Manual Conductor - customers load correctly
- [ ] Tested IC Viewer - transaction counts accurate
- [ ] All conversation histories load properly
- [ ] VIP statuses look correct
- [ ] Lifetime values make sense
- [ ] No customers missing from search
- [ ] Backup table still exists (don't delete yet!)
- [ ] Update `WORKLOG.md` with results

---

**Last Updated**: 2025-11-06  
**Status**: Production Ready  
**Risk Level**: Medium (destructive operation, but fully reversible with backup)

