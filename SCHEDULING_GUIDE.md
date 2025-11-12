# 📅 Campaign Scheduling System - Complete Guide

## 🎯 **Overview**

Schedule SMS campaigns with **human-like timing** to avoid spam filters and look natural:
- **Random intervals**: 4-7 minutes between messages
- **Random skips**: 15-20% chance of extra 10-15 minute delay (looks like you got distracted)
- **Business hours**: Only sends 9 AM - 8 PM Pacific
- **Auto-resumption**: If time runs past 8 PM, resumes next day at 9 AM

---

## 🚀 **Quick Start**

### Step 1: Create the `scheduled_messages` Table
Run this SQL in Supabase SQL Editor:
```bash
# In Supabase Dashboard:
SQL Editor → New Query → Paste contents of:
sql_scripts/create_scheduled_messages_table.sql
```

### Step 2: Preview the Schedule (Dry Run)
```bash
# Windows:
schedule_campaign_preview.bat

# Or manually:
python schedule_campaign.py --dry-run
```

This shows you the full schedule WITHOUT inserting into the database.

### Step 3: Schedule for Real
```bash
# Windows:
schedule_campaign_now.bat

# Or manually:
python schedule_campaign.py
```

Type `YES` to confirm, and messages will be scheduled!

### Step 4: Let Conductor Run
Conductor automatically checks `scheduled_messages` every 10 seconds and queues messages when their time arrives.

**That's it!** Messages will send at their scheduled times. 🎉

---

## 📊 **How It Works**

### Workflow Diagram

```
┌─────────────────────────────────────┐
│ campaign_messages (status='SUG')    │
│ 346 messages ready for approval     │
└──────────────┬──────────────────────┘
               │
               │ [Run schedule_campaign.py]
               │
               ↓
┌─────────────────────────────────────┐
│ scheduled_messages table             │
│                                      │
│ Row 1: Nalleli | 11:20 AM | scheduled│
│ Row 2: Jeff    | 11:25 AM | scheduled│
│ Row 3: Eugene  | 11:31 AM | scheduled│
│ Row 4: Andres  | 11:46 AM | scheduled│ ← Random skip!
│ ...                                  │
│ Row 346: Melynna | 3 days later     │
└──────────────┬──────────────────────┘
               │
               │ [Conductor polls every 10 sec]
               │
               ↓
       Is scheduled_for <= now?
               │
               ├─ NO → Keep waiting
               │
               └─ YES → Split by [BUBBLE]
                        │
                        ↓
              ┌─────────────────────────┐
              │ messages table (queued)  │
              │                          │
              │ Row 1: Bubble 1 | queued │
              │ Row 2: Bubble 2 | queued │
              │ Row 3: Bubble 3 | queued │
              └──────────┬───────────────┘
                         │
                         │ [Conductor sends via modem]
                         │
                         ↓
                📱 3 SMS bubbles received!
```

---

## 🎲 **Randomization Logic**

### Base Interval
- **4-7 minutes** random delay between each message
- Example: 5 min, 6 min, 4 min, 7 min, 5 min...

### Random Skips
- **15-20% chance** of adding extra delay (10-15 minutes)
- Makes it look like a human got distracted or took a break
- Example sequence:
  ```
  Message 1: 11:20 AM (+5 min)
  Message 2: 11:25 AM (+6 min)
  Message 3: 11:31 AM (+4 min)
  Message 4: 11:46 AM (+15 min SKIP!)  ← Looks human!
  Message 5: 11:51 AM (+5 min)
  ```

### Business Hours
- **Only sends**: 9 AM - 8 PM Pacific
- If schedule runs past 8 PM → **auto-pauses** and resumes next day at 9 AM
- Example:
  ```
  Message 200: 7:55 PM (+5 min)
  Message 201: 9:00 AM next day  ← Auto-pause overnight
  ```

---

## ⚙️ **Scheduler Options**

### Basic Usage
```bash
# Schedule all SUG messages starting now
python schedule_campaign.py
```

### Start at Specific Time
```bash
# Start tomorrow at 10 AM
python schedule_campaign.py --start "2025-11-09 10:00"
```

### Preview Only (No DB Changes)
```bash
# Show schedule without inserting
python schedule_campaign.py --dry-run
```

### Filter by Campaign
```bash
# Only schedule specific campaign
python schedule_campaign.py --campaign "BT_Product_Feedback_v1"
```

---

## 📋 **Database Tables**

### `scheduled_messages` Table Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | bigint | Auto-increment primary key |
| `phone_number` | text | Recipient phone (E.164 format) |
| `customer_name` | text | Recipient name |
| `message_content` | text | Full message (with [BUBBLE] markers) |
| `scheduled_for` | timestamp | When to send (UTC) |
| `status` | text | `scheduled`, `sent`, `cancelled`, `failed` |
| `campaign_message_id` | bigint | Reference to original campaign_messages |
| `campaign_name` | text | Campaign identifier |
| `sent_at` | timestamp | When it was actually sent |
| `error_message` | text | If failed, why? |
| `created_at` | timestamp | When scheduled |
| `updated_at` | timestamp | Last update |

---

## 🔍 **Monitoring & Management**

### View Scheduled Messages
```sql
-- All scheduled messages (not yet sent)
SELECT 
    id,
    customer_name,
    phone_number,
    scheduled_for,
    status
FROM scheduled_messages
WHERE status = 'scheduled'
ORDER BY scheduled_for;
```

### Count Scheduled Messages
```sql
SELECT 
    status,
    COUNT(*) as count
FROM scheduled_messages
GROUP BY status;
```

### Next 10 Messages
```sql
SELECT 
    customer_name,
    phone_number,
    scheduled_for,
    EXTRACT(EPOCH FROM (scheduled_for - NOW())) / 60 as minutes_until_send
FROM scheduled_messages
WHERE status = 'scheduled'
ORDER BY scheduled_for
LIMIT 10;
```

### Cancel a Message
```sql
-- Cancel specific message
UPDATE scheduled_messages
SET status = 'cancelled'
WHERE id = 123;

-- Cancel all scheduled messages (DANGER!)
UPDATE scheduled_messages
SET status = 'cancelled'
WHERE status = 'scheduled';
```

### Reschedule a Message
```sql
-- Push back 30 minutes
UPDATE scheduled_messages
SET scheduled_for = scheduled_for + INTERVAL '30 minutes'
WHERE id = 123;
```

---

## 🎯 **Example Schedule Output**

```
======================================================================
CAMPAIGN SCHEDULER - HUMAN-LIKE RANDOM TIMING
======================================================================
Start Time: 2025-11-08 02:30 PM
Intervals: 4-7 minutes (random)
Human Skips: 15-20% chance of extra 10-15 min delay
Business Hours: 9 AM - 8 PM
Dry Run: NO (will schedule)
======================================================================

Found 346 messages to schedule

[1/346]   Jaquelin Rodriguez  | +12097930464   | 11/08 02:31 PM | + 1m | 8 bubbles
[2/346]   Sandy Evans         | +15598819424   | 11/08 02:37 PM | + 6m | 8 bubbles
[3/346]   Aubrey Mann          | +12094880885   | 11/08 02:42 PM | + 5m | 8 bubbles
    [SKIP] Adding extra 12 min delay (looks human)
[4/346]   Andrew Torres        | +14084069711   | 11/08 02:59 PM | +17m | 8 bubbles
[5/346]   Denise Mendez        | +12093989722   | 11/08 03:05 PM | + 6m | 8 bubbles
...
[346/346] Melynna Ramirez     | +15594930003   | 11/11 07:45 PM | + 5m | 3 bubbles

======================================================================
SCHEDULING COMPLETE: 346/346 messages scheduled
======================================================================

Campaign Duration: 62.3 hours
First Message: 2025-11-08 02:31 PM
Last Message: 2025-11-11 07:45 PM
```

---

## ⚠️ **Important Notes**

### Conductor Must Be Running
- Conductor checks for scheduled messages every **10 seconds**
- If Conductor is stopped, messages won't send!
- Start Conductor: `cd conductor-sms && python conductor_system.py`

### Time Zone
- All times stored in **UTC** in database
- Scheduler converts to **Pacific Time** for business hours
- Make sure your system clock is accurate!

### Cancelling vs. Deleting
- **Cancel**: Sets `status='cancelled'` (keeps record)
- **Delete**: Removes from table (no record)
- **Recommendation**: Always cancel, don't delete (for audit trail)

### Failed Messages
- If Conductor can't send, marks as `failed` in `scheduled_messages`
- Check `error_message` column for reason
- Can manually retry by updating `status='scheduled'` and `scheduled_for`

---

## 🧪 **Testing the System**

### Test 1: Schedule 1 Message
```python
from supabase import create_client
from datetime import datetime, timedelta

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Schedule test message for 2 minutes from now
test_time = datetime.utcnow() + timedelta(minutes=2)

supabase.table('scheduled_messages').insert({
    'phone_number': '+16199773020',  # Your phone
    'customer_name': 'Test User',
    'message_content': 'Test bubble 1\n\n[BUBBLE]\n\nTest bubble 2',
    'scheduled_for': test_time.isoformat(),
    'status': 'scheduled',
    'campaign_name': 'test'
}).execute()

print(f"Scheduled for: {test_time}")
print("Wait 2 minutes and check your phone!")
```

### Test 2: Preview Schedule
```bash
python schedule_campaign.py --dry-run
```
Review the output, confirm timing looks good.

### Test 3: Schedule 5 Messages
Edit `schedule_campaign.py` temporarily:
```python
# Line ~125 (in schedule_campaign_messages)
messages = messages[:5]  # Only first 5
```
Then run normally.

---

## 🎉 **You're Ready!**

1. ✅ Create `scheduled_messages` table (run SQL script)
2. ✅ Preview schedule: `schedule_campaign_preview.bat`
3. ✅ Confirm timing looks good
4. ✅ Run scheduler: `schedule_campaign_now.bat`
5. ✅ Ensure Conductor is running
6. ✅ Messages will auto-send at scheduled times!

**346 budtender messages ready to roll out with human-like timing!** 🚀

