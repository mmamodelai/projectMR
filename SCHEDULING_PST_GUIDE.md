<!-- maxTokens>100000</max -->
# 📅 Campaign Scheduling System - Database-Native with Pacific Time

## 🎯 **Architecture: Database Handles Scheduling, Conductor Just Sends**

```
┌─────────────────────────────────────────────┐
│ campaign_messages                           │
│ Status: SUG (suggested by AI)               │
└──────────────┬──────────────────────────────┘
               │
               │ [Human approves in SMS Viewer]
               │
               ↓
┌─────────────────────────────────────────────┐
│ campaign_messages                           │
│ Status: APR (approved by human)             │
└──────────────┬──────────────────────────────┘
               │
               │ [Run schedule_campaign.py]
               │ Assigns random send times (PST)
               ↓
┌─────────────────────────────────────────────┐
│ campaign_messages & scheduled_messages      │
│ Status: SCH (scheduled)                     │
│ scheduled_for: 2025-11-08 14:30:00-08 (PST)│
└──────────────┬──────────────────────────────┘
               │
               │ [Supabase pg_cron checks every minute]
               │ Runs: process_scheduled_messages_safe()
               │ Checks: Is it time? (PST)
               │         Are we in business hours? (PST)
               │
               ↓
┌─────────────────────────────────────────────┐
│ messages table                              │
│ status='queued' (split by [BUBBLE])         │
│ Row 1: Bubble 1 | queued                    │
│ Row 2: Bubble 2 | queued                    │
│ Row 3: Bubble 3 | queued                    │
└──────────────┬──────────────────────────────┘
               │
               │ [Conductor polls every 10s]
               │ Just sends queued messages
               │ No scheduling logic!
               ↓
┌─────────────────────────────────────────────┐
│ messages table                              │
│ status='sent'                               │
└─────────────────────────────────────────────┘
               ↓
          📱 Received!
```

---

## 📊 **Status Workflow**

| Status | Meaning | Where | Who Sets It |
|--------|---------|-------|-------------|
| **SUG** | Suggested (AI-generated) | `campaign_messages` | AI / Import Script |
| **APR** | Approved (human reviewed) | `campaign_messages` | Human (SMS Viewer) |
| **SCH** | Scheduled (has send time) | `campaign_messages` + `scheduled_messages` | Scheduler Script |
| **queued** | Ready to send | `messages` | Supabase Function |
| **sent** | Actually sent | `messages` | Conductor |

---

## ⏰ **Pacific Time Handling (CRITICAL!)**

### **The Problem**
- PostgreSQL stores timestamps in **UTC**
- Your business operates in **Pacific Time** (PST/PDT)
- Business hours: **9 AM - 8 PM Pacific**
- Need to ensure messages NEVER send outside these hours

### **The Solution**
```sql
-- ✅ CORRECT: Compare in Pacific Time
scheduled_for AT TIME ZONE 'America/Los_Angeles' <= now() AT TIME ZONE 'America/Los_Angeles'

-- ❌ WRONG: Compare in UTC (ignores time zone!)
scheduled_for <= now()
```

### **Business Hours Check (Pacific Time)**
```sql
CREATE FUNCTION is_business_hours()
RETURNS boolean AS $$
    SELECT 
        EXTRACT(HOUR FROM now() AT TIME ZONE 'America/Los_Angeles')::int >= 9
        AND EXTRACT(HOUR FROM now() AT TIME ZONE 'America/Los_Angeles')::int < 20
        AND EXTRACT(DOW FROM now() AT TIME ZONE 'America/Los_Angeles')::int BETWEEN 1 AND 5;
$$ LANGUAGE sql;
```

### **What This Ensures**
- ✅ Converts "now" to Pacific Time before checking hour
- ✅ Only sends 9 AM - 8 PM Pacific (Monday-Friday)
- ✅ Accounts for Daylight Saving Time automatically
- ✅ No guessing - explicit time zone conversions

---

## 🚀 **Setup Instructions (3 Steps)**

### **Step 1: Create Database Functions**
Run this in Supabase SQL Editor:
```bash
sql_scripts/create_scheduling_system.sql
```

This creates:
- `scheduled_messages` table
- `process_scheduled_messages()` function (splits [BUBBLE], queues messages)
- `process_scheduled_messages_safe()` function (business hours wrapper)
- `is_business_hours()` function (Pacific Time check)
- `scheduled_messages_pst` view (human-readable schedule)
- `business_hours_status` view (current PST time/status)

### **Step 2: Enable pg_cron (If Available)**

**Supabase Pro/Enterprise** (has pg_cron):
```sql
-- Run in SQL Editor:
SELECT cron.schedule(
    'process-scheduled-messages',
    '* * * * *',  -- Every minute
    $$SELECT * FROM process_scheduled_messages_safe()$$
);
```

**Supabase Free** (no pg_cron):
```python
# Uncomment in conductor_system.py line ~1017:
self.check_scheduled_messages()
```
Conductor will check every 10 seconds instead.

### **Step 3: Schedule Your Campaign**
```bash
# Preview schedule (no DB changes):
schedule_campaign_preview.bat

# Actually schedule:
schedule_campaign_now.bat
```

---

## 🎲 **How Scheduling Works**

### **Python Scheduler** (`schedule_campaign.py`)
1. Queries: `SELECT * FROM campaign_messages WHERE status='APR'`
2. Calculates random send times:
   - **4-7 minutes** between messages (random)
   - **15-20% chance** of extra 10-15 min skip (looks human)
   - **Respects Pacific business hours** (9 AM - 8 PM)
   - **Pauses overnight**, resumes next day at 9 AM
3. Inserts into `scheduled_messages` with `status='SCH'`
4. Updates `campaign_messages` to `status='SCH'`

### **Supabase Function** (runs every minute via pg_cron)
1. Checks: `WHERE status='SCH' AND scheduled_for <= now()`
2. Converts times to **Pacific** for comparison
3. Checks: `is_business_hours()` (Pacific Time)
4. If yes:
   - Splits message by `[BUBBLE]`
   - Inserts each bubble into `messages` as `status='queued'`
   - Updates `scheduled_messages` to `status='sent'`

### **Conductor** (polls every 10 seconds)
1. Queries: `SELECT * FROM messages WHERE status='queued'`
2. Sends via modem (AT commands)
3. Updates `messages` to `status='sent'`

**Clean separation!** 🎉

---

## 🔍 **Monitoring & Debugging**

### **View Current Pacific Time**
```sql
SELECT * FROM business_hours_status;
```
Output:
```
is_business_hours | current_pacific_time | current_hour_pst | day_name
------------------+----------------------+------------------+-----------
true              | 2025-11-08 14:30:00  | 14               | Friday
```

### **View Scheduled Messages (in Pacific Time)**
```sql
SELECT * FROM scheduled_messages_pst;
```
Output:
```
customer_name    | phone_number    | scheduled_for_pst   | minutes_until_send
-----------------+-----------------+---------------------+--------------------
Jaquelin Rodriguez| +12097930464   | 2025-11-08 14:31:00 | 1.2
Sandy Evans       | +15598819424   | 2025-11-08 14:37:00 | 7.5
```

### **Manually Trigger Processing (Test)**
```sql
SELECT * FROM process_scheduled_messages_safe();
```
Output:
```
processed_count | error_message | skipped_reason
----------------+---------------+----------------------------------------
5               |               | NULL  (or "Outside business hours..." if after 8 PM)
```

### **View What Will Send Next**
```sql
SELECT 
    customer_name,
    phone_number,
    scheduled_for AT TIME ZONE 'America/Los_Angeles' as send_time_pst,
    EXTRACT(EPOCH FROM (scheduled_for - now())) / 60 as minutes_away
FROM scheduled_messages
WHERE status = 'SCH'
ORDER BY scheduled_for
LIMIT 10;
```

---

## ⚙️ **Management Commands**

### **Cancel a Scheduled Message**
```sql
UPDATE scheduled_messages
SET status = 'cancelled'
WHERE id = 123;
```

### **Reschedule a Message (Push Back 1 Hour)**
```sql
UPDATE scheduled_messages
SET scheduled_for = scheduled_for + INTERVAL '1 hour'
WHERE id = 123;
```

### **Cancel ALL Scheduled Messages (DANGER!)**
```sql
UPDATE scheduled_messages
SET status = 'cancelled'
WHERE status = 'SCH';
```

### **Change a Message's Content**
```sql
UPDATE scheduled_messages
SET message_content = 'New message content here'
WHERE id = 123;
```

### **View Messages Sent Today**
```sql
SELECT 
    customer_name,
    phone_number,
    sent_at AT TIME ZONE 'America/Los_Angeles' as sent_at_pst
FROM scheduled_messages
WHERE status = 'sent'
AND DATE(sent_at AT TIME ZONE 'America/Los_Angeles') = CURRENT_DATE
ORDER BY sent_at;
```

---

## 🧪 **Testing the System**

### **Test 1: Check Current Time & Business Hours**
```sql
SELECT * FROM business_hours_status;
```
Confirm it shows correct Pacific Time.

### **Test 2: Schedule 1 Test Message (2 Minutes from Now)**
```python
from supabase import create_client
from datetime import datetime, timedelta, timezone

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Calculate 2 minutes from now (in UTC)
test_time = datetime.now(timezone.utc) + timedelta(minutes=2)

# Insert test message
supabase.table('scheduled_messages').insert({
    'phone_number': '+16199773020',  # Your phone
    'customer_name': 'Test User',
    'message_content': 'Test bubble 1\n\n[BUBBLE]\n\nTest bubble 2',
    'scheduled_for': test_time.isoformat(),
    'status': 'SCH',
    'campaign_name': 'test'
}).execute()

print(f"Scheduled for: {test_time} UTC")
print("Wait 2 minutes, then check your phone!")
```

### **Test 3: Manually Trigger Processing**
```sql
-- Wait 2 minutes, then:
SELECT * FROM process_scheduled_messages_safe();
```
Should return: `processed_count: 1`

Check your phone - you should get 2 separate SMS bubbles!

### **Test 4: Test Business Hours Logic**
```sql
-- Check if outside hours:
SELECT is_business_hours();

-- Try to process when outside hours:
SELECT * FROM process_scheduled_messages_safe();
-- Should return: skipped_reason: "Outside business hours..."
```

---

## ⚠️ **Important Notes**

### **pg_cron Availability**
- **Supabase Pro/Enterprise**: pg_cron included ✅
- **Supabase Free**: No pg_cron ❌
- **Fallback**: Conductor can check `scheduled_messages` (uncomment line ~1017 in `conductor_system.py`)

### **Time Zone Changes (Daylight Saving)**
- PostgreSQL's `America/Los_Angeles` **automatically** handles DST
- No manual adjustments needed!
- PST (winter): UTC-8
- PDT (summer): UTC-7

### **Database Performance**
- `process_scheduled_messages()` processes **50 messages at a time**
- If you have 1000+ messages due at once, it will take ~20 minutes (50 per minute)
- Increase batch size if needed (change `LIMIT 50` in SQL function)

### **Error Handling**
- If a message fails to process, it's marked `status='failed'`
- Check `error_message` column for details
- Manually fix and reset to `status='SCH'` to retry

---

## 📊 **Campaign Rollout Example**

### **Scenario**: 346 Budtender Messages

**Step 1**: Approve messages in SMS Viewer
```
campaign_messages: 346 rows with status='SUG'
↓ (Human approves in SMS Viewer)
campaign_messages: 346 rows with status='APR'
```

**Step 2**: Run scheduler
```bash
python schedule_campaign.py
```
Output:
```
[1/346]   Jaquelin Rodriguez  | +12097930464   | 11/08 02:31 PM | + 1m | 8 bubbles
[2/346]   Sandy Evans         | +15598819424   | 11/08 02:37 PM | + 6m | 8 bubbles
    [SKIP] Adding extra 12 min delay (looks human)
[3/346]   Aubrey Mann          | +12094880885   | 11/08 02:54 PM | +17m | 8 bubbles
...
[346/346] Melynna Ramirez     | +15594930003   | 11/11 07:45 PM | + 5m | 3 bubbles

Campaign Duration: 62.3 hours (3 days with nights paused)
```

**Step 3**: Database automatically processes every minute
```
[Minute 1] 11/08 2:31 PM - Jaquelin's message → messages (queued)
[Minute 7] 11/08 2:37 PM - Sandy's message → messages (queued)
[Minute 24] 11/08 2:54 PM - Aubrey's message → messages (queued)
...continues for 3 days...
```

**Step 4**: Conductor sends queued messages
```
11/08 2:31:05 PM - Sends Jaquelin's 8 bubbles
11/08 2:37:10 PM - Sends Sandy's 8 bubbles
11/08 2:54:15 PM - Sends Aubrey's 8 bubbles
```

**Total**: 346 messages sent over ~3 days with human-like timing! 🎉

---

## 🎉 **Summary**

### **What Changed from Original Design**
- ❌ **Before**: Conductor checked `scheduled_messages` table
- ✅ **Now**: Supabase pg_cron handles scheduling (or Conductor as fallback)

### **Benefits**
- ✅ **Decoupled**: Conductor just sends, doesn't schedule
- ✅ **More reliable**: Database won't crash like Python might
- ✅ **Pacific Time safe**: All comparisons explicitly use PST
- ✅ **Business hours enforced**: No guessing, SQL function checks
- ✅ **Easier debugging**: Clear separation of concerns

### **Status Flow** (Final)
```
SUG (AI suggests)
  ↓
APR (Human approves in SMS Viewer)
  ↓
SCH (Scheduler assigns time)
  ↓
queued (Database moves at scheduled time)
  ↓
sent (Conductor sends via modem)
```

---

## 📁 **Files Created/Modified**

| File | Purpose |
|------|---------|
| `sql_scripts/create_scheduling_system.sql` | Database schema + functions |
| `schedule_campaign.py` | Updated to use APR/SCH statuses |
| `conductor-sms/conductor_system.py` | Commented out scheduled check (Supabase handles it) |
| `SCHEDULING_PST_GUIDE.md` | This guide |

---

## 🚀 **Ready to Roll!**

1. ✅ Run SQL script to create functions
2. ✅ Enable pg_cron (if Pro plan) or use Conductor fallback
3. ✅ Schedule campaign: `schedule_campaign_now.bat`
4. ✅ Watch messages send automatically with Pacific Time safety!

**All 346 budtender messages ready to send with proper time zone handling!** 🎉

