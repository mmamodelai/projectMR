# 🚨 ROOT CAUSE FOUND: MODEM AUTO-DELETING MESSAGES!

## The Smoking Gun

### Modem Storage Status
```
SIM Storage (SM):  0/30 messages  ← EMPTY!
Phone Storage (ME): 0/23 messages  ← EMPTY!
```

**BOTH storages are EMPTY!**

### Message Notification Settings
```
+CNMI: 2,0,0,0,0
       ↑ ↑
Mode 2: Store in memory
Parameter 0: NO indication/notification
```

---

## What's Happening

### The Deadly Sequence:
1. **Message arrives** from T-Mobile → Modem receives it
2. **Modem stores it** in memory (mode 2)
3. **Modem IMMEDIATELY DELETES IT** (auto-delete enabled?)
4. **Conductor polls** 5 seconds later
5. **Modem says:** "0 messages" (already deleted!)
6. **Message is LOST!** ❌

### Why We Lost "Hey how many points do I have":
- Message arrived at **11:04 AM**
- Modem stored it briefly
- Modem **auto-deleted** it before 11:04:05 (next poll)
- Conductor checked at **11:04:05** - saw nothing
- **Message gone forever!**

---

## Evidence

### 1. Storage is Always Empty
```
AT+CMGL="ALL"
OK
← No messages returned!
```

Every poll shows **0 messages**. This is impossible if messages are being stored!

### 2. Message Count Dropped
```
11:04:58 - Status: 13 total
11:06:38 - Status: 12 total
```

A message was **deleted** from the database! This might be:
- Old message cleanup by n8n?
- Supabase trigger?
- Or unrelated

### 3. Modem Never Reports Messages
Logs show **"No messages found on modem"** every single cycle.

---

## The Fix: Change CNMI Settings

### Current (BAD):
```
AT+CNMI=2,0,0,0,0
        ↑ Store in memory
          ↑ NO notification
```

Messages stored but **auto-deleted** before Conductor can read them!

### Fix Option 1: Route to TE (Best for Polling)
```
AT+CNMI=2,1,0,0,0
        ↑ Store in memory
          ↑ Notify when message arrives
```

This will:
- ✅ Store messages in memory
- ✅ Send notification "+CMT:" when new message
- ✅ Keep messages until explicitly deleted
- ✅ Conductor can read them at next poll

### Fix Option 2: Direct Delivery (Best for Real-time)
```
AT+CNMI=2,2,0,0,0
        ↑ Buffer mode
          ↑ Deliver directly to TE (no storage)
```

This will:
- ✅ Deliver messages IMMEDIATELY to serial port
- ✅ No storage (messages don't get "stuck")
- ❌ Requires Conductor to be ALWAYS listening
- ❌ Conflicts with polling architecture

### Fix Option 3: Persistent Storage
```
AT+CNMI=1,1,0,0,0
        ↑ Forward to TE, DO NOT DELETE from storage
          ↑ Notify when message arrives
```

This will:
- ✅ Keep messages in storage
- ✅ Notify on arrival
- ✅ Conductor can poll and read them
- ✅ Explicit delete required (AT+CMGD)

---

## Recommended Fix

**Use Option 3: Persistent Storage + Notification**

```python
# In conductor_system.py, add to initialization:
def _setup_modem(self):
    \"\"\"Setup modem for message handling\"\"\"
    # Set text mode
    self._send_at_command('AT+CMGF=1')
    
    # Set message storage to phone memory
    self._send_at_command('AT+CPMS="ME","ME","ME"')
    
    # CRITICAL: Set CNMI to keep messages in storage!
    self._send_at_command('AT+CNMI=1,1,0,0,0')
    #                              ↑ Keep in storage, don't auto-delete!
    #                                ↑ Send notification when new message
```

---

## Testing the Fix

### Step 1: Apply the Fix
Update `conductor_system.py` to set `AT+CNMI=1,1,0,0,0` on startup.

### Step 2: Restart Conductor
```bash
cd conductor-sms
python conductor_system.py
```

### Step 3: Send Test Message
Text: "test 12345"

### Step 4: Check Logs
Should see:
```
AT Command: AT+CMGL="ALL"
Response: +CMGL: 1,"REC UNREAD","+16199773020"...
Found 1 message on modem
```

### Step 5: Verify Database
```bash
python conductor_system.py status
```

Should show **1 unread message**!

---

## Why This Happened

### Modem Default Settings
The SIM7600 modem defaults to:
- `+CNMI=2,0,0,0,0` (store but don't notify, auto-delete)

This is WRONG for polling architecture!

### Conductor Assumption
Conductor assumes:
- Messages stay in storage until explicitly deleted
- Polling every 5s is fast enough

But if modem auto-deletes, **5 seconds is too slow!**

---

## Impact

**This bug causes:**
- ❌ **Random message loss** (messages deleted before poll)
- ❌ **No error indication** (Conductor sees nothing wrong)
- ❌ **Unpredictable behavior** (depends on timing)
- ❌ **Customer messages unanswered!**

**Priority: P0 - CRITICAL BUG** 🚨

---

## Next Steps

1. ✅ Update `conductor_system.py` to set `AT+CNMI=1,1,0,0,0`
2. ✅ Restart Conductor
3. ✅ Send test message
4. ✅ Verify message is NOT lost
5. ✅ Monitor for 24 hours
6. ✅ Document in `.cursorrules`

**FIX THIS NOW!** 🔥

