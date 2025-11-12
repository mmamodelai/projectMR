# Questions for Original Conductor SMS System Team

**Date**: October 1, 2025  
**Purpose**: Rebuild system accurately based on production experience  
**Current Status**: Have architecture docs, need implementation details  

---

## 🔧 Core Implementation Details

### 1. Modem Connection & AT Commands

**Q1.1**: What is the exact AT command initialization sequence used in `conductor_system.py`?
- Do you send `AT+CMGF=1` every time you connect, or just once at startup?
- What's the full sequence: `AT` → `AT+CMGF=1` → `AT+CNMI=...` → `AT+CPMS=...`?

**Q1.2**: For the `AT+CNMI` command, what exact parameters did you settle on?
- The docs mention `AT+CNMI=2,1,0,0,0` - is this correct?
- Did you ever experiment with other values?

**Q1.3**: After sending an AT command, how long do you wait before reading the response?
- Is it a fixed `time.sleep(1)` or do you use `ser.read_until(b'OK')`?
- Different timing for different commands?

**Q1.4**: When checking for messages with `AT+CMGL="UNREAD"`, do you:
- Read until timeout?
- Read until you see `OK`?
- Use `ser.read_all()` or `ser.readline()` in a loop?

**Q1.5**: For `AT+CMGS` (sending SMS), what's the exact sequence?
```python
# Is it like this?
ser.write(b'AT+CMGS="+16199773020"\r\n')
# Wait for '>' prompt
ser.write(b'Message content')
ser.write(b'\x1A')  # Ctrl+Z
# Wait for response
```
- How long do you wait for the `>` prompt?
- How do you detect send success vs failure?

---

## 📊 Database Implementation

### 2. Database Schema & Operations

**Q2.1**: Are there any indexes on the `messages` table?
```sql
CREATE INDEX idx_status ON messages(status);
CREATE INDEX idx_timestamp ON messages(timestamp);
```
- If yes, which ones?

**Q2.2**: For the `contacts` table, how do you update it?
- Automatically after each message in/out?
- Separate function that runs periodically?
- Is it even used in the core system?

**Q2.3**: What's your connection timeout for SQLite?
```python
conn = sqlite3.connect(DB_PATH, timeout=10)  # Like this?
```

**Q2.4**: Do you use WAL mode for SQLite?
```python
conn.execute("PRAGMA journal_mode=WAL")
```

**Q2.5**: When you delete messages from the modem with `AT+CMGD`, do you:
- Delete individually: `AT+CMGD=1`, `AT+CMGD=2`, etc.?
- Delete all at once: `AT+CMGD=1,4` (delete all read)?
- Delete in the same connection as reading, or reconnect?

---

## ⏱️ Timing & Performance

### 3. Polling Cycle Details

**Q3.1**: In the main polling loop, what's the exact timing breakdown?
```python
# Is it like this?
while True:
    start = time.time()
    _poll_for_incoming()  # ~2-3 seconds
    _process_outgoing_queue()  # ~2-3 seconds if messages queued
    elapsed = time.time() - start
    time.sleep(max(0, POLL_INTERVAL - elapsed))  # Sleep remainder
```

**Q3.2**: If there are queued outgoing messages, do you:
- Send them ALL in one connection (loop through them)?
- Send one per connection (connect, send, disconnect, connect, send, disconnect)?
- Batch them somehow?

**Q3.3**: What happens if a poll cycle takes longer than 10 seconds?
- Do you skip the sleep?
- Log a warning?
- Adjust the next cycle?

**Q3.4**: When you say "never hold COM port > 3 seconds", is that:
- Per individual operation (read OR send)?
- Per connection session (read AND send)?
- What's the longest you've seen in logs?

---

## 🐛 Error Handling & Edge Cases

### 4. Error Scenarios

**Q4.1**: If the COM port is busy when conductor tries to connect, do you:
- Retry immediately?
- Skip that cycle and wait for next poll?
- Retry with exponential backoff?

**Q4.2**: What happens if the modem returns `ERROR` to an AT command?
- Reconnect and retry?
- Log and continue?
- Raise exception?

**Q4.3**: If a message fails to send, do you:
- Set status to `'failed'` immediately?
- Retry a few times first?
- Move it to a separate failed queue?

**Q4.4**: Have you encountered messages with special characters (emoji, etc.)?
- Do you use GSM7 encoding or UCS2?
- Any encoding issues discovered?

**Q4.5**: What's the longest message you've successfully sent?
- Do you handle message splitting for > 160 chars?
- Or just truncate/reject?

**Q4.6**: What happens if the database is locked when trying to write?
- Built-in SQLite retry logic sufficient?
- Custom retry wrapper?

**Q4.7**: Have you ever had the modem "hang" or stop responding?
- How do you detect this?
- Auto-restart logic?

---

## 🔍 Message Parsing

### 5. SMS Message Parsing

**Q5.1**: When parsing `+CMGL` response, what regex/parsing do you use?
```
+CMGL: 1,"REC UNREAD","+16199773020","","25/09/30,22:45:10-28"
Testing at 1045
OK
```
- Split by lines and use regex on first line?
- Can you share the exact parsing code snippet?

**Q5.2**: Have you encountered multi-line messages?
- How do you know where one message ends and next begins?
- Do you parse until you see the next `+CMGL:` or `OK`?

**Q5.3**: What phone number formats have you seen in real messages?
- Always E.164 format (`+16199773020`)?
- Ever seen without country code?
- Any normalization needed?

**Q5.4**: Timestamp parsing - do you convert to UTC or keep local?
- The format `25/09/30,22:45:10-28` - the `-28` is timezone, right?
- Do you parse it or just store as-is?

---

## 🚀 Startup & Shutdown

### 6. System Lifecycle

**Q6.1**: When `conductor_system.py` starts, do you:
- Test modem connection first before entering loop?
- Initialize database tables if they don't exist?
- Clear any old `status='queued'` messages from previous crashes?

**Q6.2**: For graceful shutdown, do you use signal handlers?
```python
import signal
signal.signal(signal.SIGINT, shutdown_handler)
```

**Q6.3**: If conductor crashes, do queued messages get resent on restart?
- Or do you clear them?
- Any duplicate prevention logic?

**Q6.4**: Do you have any modem initialization at startup?
- Clear stored messages?
- Check signal strength?
- Verify SIM card is ready?

---

## 📝 Logging

### 7. Logging Configuration

**Q7.1**: What's your logging configuration?
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/conductor_system.log'),
        logging.StreamHandler()  # Also to console?
    ]
)
```

**Q7.2**: Do you use log rotation?
- `RotatingFileHandler` with max size?
- Or just let logs grow?

**Q7.3**: What level of detail for AT command logging?
- Log every AT command at DEBUG level?
- Only errors?
- Full request/response?

---

## 🧪 Testing

### 8. Testing & Validation

**Q8.1**: For `test_conductor.bat`, how does it queue messages?
- Direct database INSERT?
- Call a function in `conductor_system.py`?
- Can you share the exact code?

**Q8.2**: The `status` command that shows message counts - is that:
- A separate CLI argument (`python conductor_system.py status`)?
- Just queries the database?
- Code snippet?

**Q8.3**: How do you test the system without sending real SMS?
- Mock serial port?
- Test mode in the code?
- Or always test with real modem?

---

## 🔗 Integration

### 9. n8n & External Integration

**Q9.1**: For n8n integration, which approach is currently used?
- Direct database INSERT for outgoing?
- Direct database SELECT for incoming?
- Or through Python script calls?

**Q9.2**: If using database approach, any locking issues with n8n and conductor both accessing DB?

**Q9.3**: Are there any webhook/API endpoints, or is it all database-driven?

---

## 🛠️ Configuration

### 10. Configuration & Deployment

**Q10.1**: Is COM port hardcoded or configurable?
- Config file?
- Environment variable?
- Command-line argument?

**Q10.2**: Same for poll interval, database path, etc. - configurable how?

**Q10.3**: Do you run conductor as a Windows service?
- If yes, using NSSM as mentioned in docs?
- Any special configuration?

**Q10.4**: How do you handle updates/restarts without losing messages?
- Stop conductor → update → restart?
- Any queue persistence concerns?

---

## 📊 Production Experience

### 11. Real-World Insights

**Q11.1**: Of the 95 messages processed successfully:
- How many inbound vs outbound?
- Any patterns in failures?
- Average processing time per message?

**Q11.2**: Longest uptime without restart?
- Any memory leaks observed?
- Performance degradation over time?

**Q11.3**: Biggest issues encountered in production?
- What almost broke?
- What required emergency fixes?

**Q11.4**: If you could redesign one thing, what would it be?

**Q11.5**: Any modem-specific quirks with SIM7600G-H that aren't obvious?
- Specific firmware version?
- Settings in modem config?

---

## 🎯 Specific Code Requests

### 12. Can You Share Snippets?

If possible, can you share specific code snippets for:

**Q12.1**: Complete `_poll_for_incoming()` method
**Q12.2**: Complete `_send_sms()` method  
**Q12.3**: Message parsing logic (regex/parsing code)
**Q12.4**: Database connection setup
**Q12.5**: Main loop structure
**Q12.6**: The exact AT command initialization sequence

Even pseudocode or simplified versions would be incredibly helpful!

---

## 📦 Dependencies

### 13. Environment

**Q13.1**: Python version? (3.8, 3.9, 3.10, 3.11, 3.12?)

**Q13.2**: `pyserial` version? (`pip list | grep pyserial`)

**Q13.3**: Any other dependencies?
- colorama for db_viewer?
- Any others?

**Q13.4**: Windows version? (10, 11?)

**Q13.5**: Any known compatibility issues?

---

## 🎨 db_viewer.py

### 14. Database Viewer Details

**Q14.1**: Does `db_viewer.py` use any special libraries?
- `curses` (doesn't work well on Windows)?
- `rich` library?
- Just clear screen and print?

**Q14.2**: How does auto-refresh work?
- Thread that refreshes?
- Simple loop with `time.sleep(2)`?

**Q14.3**: Can you share the basic structure/approach?

---

## Priority Questions

If you can only answer a few, these are the most critical:

1. **Q1.1** - Exact AT command sequence
2. **Q1.4** - How to reliably read messages
3. **Q1.5** - How to reliably send messages  
4. **Q3.2** - How to handle multiple queued outgoing messages
5. **Q5.1** - Message parsing code
6. **Q12.1-12.6** - Any actual code snippets!

---

## Thank You!

Any details you can provide will help ensure the rebuild is as robust and battle-tested as your production system. Even partial answers or "we learned X the hard way" notes are incredibly valuable!

**Contact**: Ready to receive answers and rebuild the system accordingly.

