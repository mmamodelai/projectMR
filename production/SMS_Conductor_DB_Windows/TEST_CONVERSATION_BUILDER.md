# 💬 Test Conversation Builder - Quick Guide

## Overview
Build realistic back-and-forth SMS conversations to test your AI's context understanding without needing real SMS messages!

## Location
**File**: `conductor-sms/SMSconductor_DB.py`  
**Launch**: `.\conductor-sms\start_SMSconductor_DB.bat`  
**Button**: "💬 Create Test Conversation"

---

## Features

### 🎯 What It Does
- Build multi-message conversations
- Test AI context/memory across messages
- Create training examples
- Debug conversation flow issues
- Verify Leafly data integration

### ⚡ Quick Features
- ✅ Live preview as you build
- ✅ Quick templates for common scenarios
- ✅ Automatic 2-minute spacing
- ✅ Keyboard shortcuts (ENTER/SHIFT+ENTER)
- ✅ One-click save to database
- ✅ Proper UTC timestamps

---

## How to Use

### Basic Workflow

1. **Launch the viewer**:
   ```bash
   .\conductor-sms\start_SMSconductor_DB.bat
   ```

2. **Click button**: "💬 Create Test Conversation"

3. **Set phone number**: Defaults to `+16199773020`

4. **Build conversation**:
   - Type message → Press **ENTER** (adds as Customer)
   - Type reply → Press **SHIFT+ENTER** (adds as Bot)
   - Repeat to build back-and-forth

5. **Save**: Click "💾 Save Conversation to Database"

6. **Test**: Run your n8n workflow to see how AI handles context!

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **ENTER** | Add as Customer message (inbound) |
| **SHIFT+ENTER** | Add as Bot reply (outbound) |

---

## Quick Templates

Click any template to auto-fill the message box:

- "What's my points balance?"
- "Tell me about OG Kush"
- "What are the effects of Blue Dream?"
- "What have I bought before?"
- "Show me relaxing strains"

---

## Example Test Scenarios

### Scenario 1: Context Memory Test

**Build this conversation**:
```
👤 Customer: "What's my points balance?"
🤖 Bot: "You have 150 points, Stephen!"
👤 Customer: "Tell me about OG Kush"
🤖 Bot: "OG Kush (4.28★, 5665 reviews) is a Hybrid strain..."
👤 Customer: "What about effects?"
```

**Then test**: Does AI remember we're talking about OG Kush?

---

### Scenario 2: Leafly Data Integration Test

**Build this conversation**:
```
👤 Customer: "I need something for anxiety"
🤖 Bot: "I can help! Looking for strains that help with anxiety..."
👤 Customer: "Yes, show me options"
```

**Then test**: Does AI use `WHERE 'Anxiety' = ANY(helps_with)` query?

---

### Scenario 3: Multi-Topic Context Test

**Build this conversation**:
```
👤 Customer: "What's my points balance?"
🤖 Bot: "You have 150 points!"
👤 Customer: "Cool. Tell me about Blue Dream"
🤖 Bot: "Blue Dream (4.39★) is a Sativa-dominant Hybrid..."
👤 Customer: "Actually, what was my points again?"
```

**Then test**: Does AI remember the earlier 150 points answer?

---

## Technical Details

### Message Timestamps
- First message: Current time (UTC)
- Each subsequent: 2 minutes earlier
- **Display Order**: Chronological (oldest first, newest last)
- **Right-Click Editing**: Edit any message's timestamp
- Example:
  ```
  Msg 1: 11:24 AM (oldest - top)
  Msg 2: 11:26 AM
  Msg 3: 11:28 AM
  Msg 4: 11:30 AM (newest - bottom)
  ```

### Message Status
- **Inbound** (customer): Marked as `unread`
- **Outbound** (bot): Marked as `read`

### Database Fields
```json
{
  "phone_number": "+16199773020",
  "content": "Tell me about OG Kush",
  "direction": "inbound",
  "status": "unread",
  "timestamp": "2025-10-14T18:30:00.000000+00:00",
  "message_hash": null
}
```

---

## Advanced Features

### Right-Click Message Editing

**How to Edit Timestamps**:
1. Right-click any message in the preview
2. Select "✏️ Edit Timestamp"
3. Enter new date (YYYY-MM-DD format)
4. Enter new time (HH:MM AM/PM format)
5. Click Save

**How to Delete Messages**:
1. Right-click any message in the preview
2. Select "🗑️ Delete Message"
3. Confirm deletion

**Use Cases for Timestamp Editing**:
- Create gaps between messages (e.g., hours apart)
- Set specific conversation times
- Fix timestamp order manually
- Create realistic conversation timing

---

## Troubleshooting

### Messages not appearing in n8n?
- Check workflow is polling every 30s
- Verify phone number matches workflow filter
- Check "status" = "unread" for inbound messages

### Timestamps look wrong?
- Database stores UTC (proper)
- Viewer displays Pacific Time (your local)
- n8n will see UTC timestamps (correct!)
- **NEW**: Right-click any message to edit timestamp

### Conversation history not loading?
- Verify "Get Conversation History" node URL: `/rest/v1/messages` (plural!)
- Check Accept header is set: `application/json`
- Ensure `alwaysOutputData: true`

### Messages in wrong order?
- **FIXED**: Messages now display in chronological order (oldest first)
- If still wrong, right-click to edit timestamps manually

---

## Best Practices

### 1. Start Simple
Build 2-3 message conversations first to understand the flow.

### 2. Use Real Scenarios
Base your test conversations on actual customer questions.

### 3. Test Context
Always include a follow-up question that requires remembering earlier context.

### 4. Vary Topics
Test if AI can switch between points balance, products, and general info.

### 5. Use Templates
Start with templates, then customize for specific tests.

---

## Integration with n8n

### Workflow Compatibility
Works with any workflow that:
- Polls `messages` table
- Filters by `status = 'unread'`
- Includes conversation history

### Testing Steps
1. Build conversation in viewer
2. Save to database (marks last customer message as `unread`)
3. Wait for n8n to poll (30s default)
4. Watch workflow process the message
5. Verify AI response uses conversation context

### Recommended Workflows
- ✅ `supabaseimport_LEAFLY_ENHANCED.json` (has conversation history)
- ✅ `supabaseimport.json` (updated with Products tool)
- ❌ Workflows without "Get Conversation History" node

---

## Timestamp Fix (Bonus!)

### Problem
Incoming SMS messages from modem were showing 7 hours slow.

### Solution
The viewer now auto-detects naive timestamps (no timezone) and adds +7 hours to fix SMS modem timestamps.

### Code
```python
# If timestamp is naive (no timezone), fix it
if dt.tzinfo is None:
    dt = dt.replace(tzinfo=tz.tzutc()) + timedelta(hours=7)
```

### Result
✅ All timestamps now display correctly in Pacific Time!

---

## Summary

**What You Get**:
- 💬 Rapid conversation creation (seconds, not minutes)
- 🧪 Perfect for testing AI context understanding
- 🎯 Quick templates for common scenarios
- ⚡ Keyboard shortcuts for speed
- 💾 One-click save to database
- ⏱️ Proper timestamps (UTC + local display)

**Perfect For**:
- Testing if AI remembers previous messages ✅
- Verifying Leafly data in responses ✅
- Creating training examples ✅
- Debugging context issues ✅
- Rapid iteration without real SMS ✅

---

## Questions?

See `WORKLOG.md` section `[2025-10-14 Evening] - SMS Database Viewer Enhancements` for full implementation details.

**Happy Testing! 🎉**

