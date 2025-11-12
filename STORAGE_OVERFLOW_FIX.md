# 🚨 CRITICAL: STORAGE OVERFLOW PREVENTION

## The New Problem

### Storage Limits
```
SIM Storage (SM):  0/30 messages  ← 30 max!
Phone Storage (ME): 0/23 messages  ← 23 max!
```

**When storage fills up → Modem STOPS receiving new messages!**

### Current Risk
With `AT+CNMI=1,1` (keep messages in storage):
- ✅ Messages persist (not auto-deleted)
- ❌ **Storage fills up after 23 messages**
- ❌ **New messages are REJECTED by modem!**

---

## The Complete Solution

### 1. Auto-Delete After Successful Save
**After** saving to database → **IMMEDIATELY delete from modem**

```python
# In check_incoming_messages():
if success:
    # Delete from modem to free storage
    self._send_at_command(f"AT+CMGD={msg['index']}")
    logger.info(f"Message {msg['index']} deleted from modem storage")
```

### 2. Add Storage Monitoring
Check storage before each poll:

```python
def _check_storage_health(self):
    """Check if modem storage is near capacity"""
    response = self._send_at_command('AT+CPMS?')
    # Response: +CPMS: "ME",5,23,"ME",5,23,"ME",5,23
    #                      ↑used ↑total
    
    if response and '+CPMS:' in response:
        # Parse used/total
        match = re.search(r'"ME",(\d+),(\d+)', response)
        if match:
            used = int(match.group(1))
            total = int(match.group(2))
            percent = (used / total) * 100
            
            if percent > 80:
                logger.warning(f"Modem storage {percent:.0f}% full ({used}/{total})!")
            
            if percent >= 90:
                logger.error(f"CRITICAL: Modem storage {percent:.0f}% full! Cleaning...")
                self._emergency_storage_cleanup()
```

### 3. Emergency Storage Cleanup
If storage gets too full → delete ALL messages:

```python
def _emergency_storage_cleanup(self):
    """Emergency cleanup if storage is full"""
    logger.warning("Performing emergency storage cleanup!")
    
    # Delete ALL messages from modem
    self._send_at_command('AT+CMGD=1,4')  # Delete all read+unread
    
    # Verify cleanup
    response = self._send_at_command('AT+CPMS?')
    logger.info(f"Storage after cleanup: {response}")
```

### 4. Crash Recovery: Re-read Messages on Startup
When Conductor starts → check for **unsynced** messages:

```python
def _startup_recovery(self):
    """On startup: check modem for messages that weren't synced to DB"""
    logger.info("Checking for unsynced messages from modem...")
    
    response = self._send_at_command('AT+CMGL="ALL"')
    
    if response and '+CMGL:' in response:
        messages = self._parse_messages(response)
        logger.warning(f"Found {len(messages)} unsynced messages on modem!")
        
        for msg in messages:
            # Try to save to database
            msg_hash = self._calculate_message_hash(msg['phone'], msg['content'])
            
            if not self._is_duplicate(msg_hash):
                success = self._save_message_to_database(...)
                if success:
                    logger.info(f"Recovered message from {msg['phone']}")
                    self._send_at_command(f"AT+CMGD={msg['index']}")
```

---

## Timestamps Fix

### Current Issue
Database viewer doesn't show timestamps in the list!

### Fix: Update SMSconductor_DB.py

```python
# In create_widgets():
self.tree = ttk.Treeview(
    self.messages_frame,
    columns=("ID", "Phone", "Direction", "Status", "Timestamp", "Content"),  # ← Add Timestamp
    show="headings",
    selectmode="browse"
)

# Add timestamp column
self.tree.heading("Timestamp", text="Timestamp", command=lambda: self.sort_by_column("Timestamp"))
self.tree.column("Timestamp", width=150)

# In load_messages():
for msg in messages:
    self.tree.insert('', 'end', values=(
        msg['id'],
        msg['phone_number'],
        msg['direction'],
        msg['status'],
        msg['timestamp'],  # ← Add timestamp
        msg['content'][:100]
    ))
```

### Add Sort by Timestamp
```python
def sort_by_column(self, col):
    """Sort treeview by column"""
    items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
    
    if col == "Timestamp":
        # Sort by timestamp (ISO format sorts naturally)
        items.sort(reverse=True)  # Newest first
    else:
        items.sort()
    
    for index, (val, item) in enumerate(items):
        self.tree.move(item, '', index)
```

---

## Implementation Plan

### Phase 1: Prevent Storage Overflow (CRITICAL)
1. ✅ Delete messages from modem after successful DB save
2. ✅ Monitor storage usage
3. ✅ Emergency cleanup if >90% full

### Phase 2: Crash Recovery
1. ✅ Check modem on startup for unsynced messages
2. ✅ Sync them to database
3. ✅ Delete from modem after sync

### Phase 3: UI Improvements
1. ✅ Add timestamp column to viewer
2. ✅ Sort by timestamp (newest first)
3. ✅ Better timestamp formatting

---

## Risk Assessment

### Without This Fix:
- ❌ Storage fills after 23 messages
- ❌ New messages rejected
- ❌ System appears "dead"
- ❌ No error indication

### With This Fix:
- ✅ Messages deleted after save (storage stays under 5%)
- ✅ Emergency cleanup if needed
- ✅ Startup recovery for crash scenarios
- ✅ Better monitoring and logging

---

**Implement this NOW?** 🚀

