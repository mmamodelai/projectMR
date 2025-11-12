# Import Budtender Campaign Messages

## Problem
The "First Texts" tab shows "No suggested messages found" because the SQL seed files were never imported into Supabase.

## What's Missing
- **Budtender T-Shirt Campaign**: Welcome messages for budtenders (Abri, Alan, Amia, Ana, Apolinaia, etc.)
- **Status**: 'SUG' (suggested, awaiting human approval)
- **Total Messages**: ~150+ budtenders across 5 SQL files

## Files to Import
Located in `sql_scripts/`:
1. `seed_campaign_messages_bt_20251107_164700_chunk_part1of5.sql`
2. `seed_campaign_messages_bt_20251107_164700_chunk_part2of5.sql`
3. `seed_campaign_messages_bt_20251107_164700_chunk_part3of5.sql`
4. `seed_campaign_messages_bt_20251107_164700_chunk_part4of5.sql`
5. `seed_campaign_messages_bt_20251107_164700_chunk_part5of5.sql`

## How to Import (Supabase Dashboard)

### Step 1: Open Supabase SQL Editor
1. Go to https://supabase.com/dashboard
2. Select your project
3. Click "SQL Editor" in left sidebar
4. Click "New Query"

### Step 2: Import Each SQL File
For each file (part1 through part5):

1. **Open the file** in a text editor (e.g., Notepad, VS Code)
2. **Copy ALL contents** (Ctrl+A, Ctrl+C)
3. **Paste into Supabase SQL Editor**
4. **Click "Run"** (bottom right)
5. **Wait for success message** (should see "Success. X rows returned" or similar)
6. **Repeat for next file**

### Step 3: Verify Import
Run this query in SQL Editor:
```sql
SELECT COUNT(*), status 
FROM campaign_messages 
GROUP BY status;
```

Expected result:
```
count | status
------|-------
~150  | SUG
    1 | draft
```

### Step 4: Test in First Texts Tab
1. Go back to SMS Viewer
2. Click "First Texts" tab
3. Click "🔄 Refresh Suggestions" button
4. Should see: "○ Abri Morales (+1209626...) [welcome]"

## What These Messages Are
Each message is a personalized welcome text for budtenders who signed up for MOTA's program:

**Example**:
```
Hi Abri, it is Luis from MOTA. Thanks for signing up. I am excited 
to welcome you to MOTA's Budtender Program. Please reply to confirm 
your welcome gift details: We have you down for a Large t-shirt with 
a GDP logo on the front and Flavors on the sleeve. Let me know if you 
want any changes. - Luis
```

## What Happens After Import
1. **First Texts tab populates**: Shows all ~150 budtenders
2. **Human approval required**: Click each name to review message
3. **Actions available**:
   - ✅ **Approve & Send**: Queue message to Conductor
   - ✏️ **Edit & Approve**: Modify message before sending
   - ❌ **Reject**: Don't send, log feedback for AI training

## Troubleshooting

### Error: "relation 'campaign_messages' does not exist"
**Solution**: The table needs to be created first. Check if it exists:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'campaign_messages';
```

If empty, you need to create the table first (schema should already exist).

### Error: "duplicate key value violates unique constraint"
**Solution**: The messages were already imported. Check existing data:
```sql
SELECT COUNT(*) FROM campaign_messages WHERE status = 'SUG';
```

If > 0, the import already happened!

### Still Shows "No suggested messages found"
**Solutions**:
1. Click "🔄 Refresh Suggestions" button
2. Restart SMS Viewer: Close and reopen `start_SMSconductor_DB.bat`
3. Check database connection (same Supabase URL/key?)

## Current Workaround
The code was temporarily modified to show 'draft' status messages in addition to 'SUG'. After importing the seed SQL, you should see both types.

## Status
- ❌ **NOT IMPORTED** (as of 2025-11-08)
- ⏳ **Awaiting manual SQL import**
- ✅ **UI ready** (First Texts tab functional)

