# SMS Manual Reply Feature Guide
**Added**: November 7, 2025  
**Version**: 2.1  
**Status**: ✅ Ready to Use

---

## 🎯 Overview

The SMS Conductor Database Viewer now has **two tabs**:

1. **📋 All Messages** - Original view (all messages, editing, status management)
2. **💬 Reply to Messages** - NEW manual reply interface

---

## 🚀 Quick Start

### Launch the Viewer

```powershell
cd conductor-sms
.\start_SMSconductor_DB.bat
```

### Using the Reply Tab

1. Click the **"💬 Reply to Messages"** tab
2. See list of incoming messages (left side)
3. Click any message to view full conversation
4. Type your reply in the text box
5. Click **"📤 Queue Reply (Send)"**
6. Done! Message will be sent within 5 seconds

---

## 📱 Features

### Left Panel: Incoming Messages
- Shows all incoming SMS messages
- Grouped by phone number (most recent first)
- **Auto-resolves names from CRM database** (Blaze IC)
- Format: `📖 John Doe (+1234567890) | 2025-11-07 10:30 | Message preview...`
- Falls back to phone number if not in CRM
- Click to load full conversation

### Right Panel: Conversation View
**Top Section - Conversation History**:
- Full message thread with timestamps
- Color-coded:
  - 👤 **Blue** = Customer messages (inbound)
  - 🤖 **Green** = Your replies (outbound)
- Shows status for each message: `[sent]`, `[queued]`, `[failed]`
- Auto-scrolls to latest message

**Bottom Section - Reply Composer**:
- Text area for typing reply
- Live character counter: `0 / 160 characters`
- Warnings:
  - Orange at 140 characters
  - Orange + "WILL BE SPLIT" at 160+ (long SMS)
- Clear button to reset
- Queue Reply button to send

---

## 🔄 How It Works

```
You Type Reply
    ↓
Click "Queue Reply"
    ↓
Message inserted into Supabase
(status = 'queued')
    ↓
conductor_system.py polls every 5 seconds
    ↓
Reads queued messages
    ↓
Sends via modem
    ↓
Updates status to 'sent'
```

**Result**: Your reply is sent within 5 seconds (guaranteed)

---

## 💡 Example Workflow

### Scenario: Customer asks about store hours

**Incoming Message** (left panel):
```
💬 +16199773020 | 2025-11-07 03:30 | What are your hours today?...
```

**Click Message** → **Conversation History** shows:
```
2025-11-07 03:30:15 PM PDT
👤 THEM:
What are your hours today?
--------------------------------------------------------------------------------

2025-11-07 03:15:22 PM PDT [sent]
🤖 YOU:
Thanks for your order! Your total is $45.67
--------------------------------------------------------------------------------
```

**Type Reply**:
```
We're open today from 10 AM to 8 PM. See you soon!
```

**Character Counter**: `55 / 160 characters`

**Click** "📤 Queue Reply (Send)"

**Success Message**:
```
Reply queued successfully!

To: +16199773020
Message: We're open today from 10 AM to 8 PM. See you soon!

conductor_system.py will send it within 5 seconds.
```

**Result**: Customer receives SMS in ~5 seconds

---

## 🎨 Interface Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  📱 SMS Conductor - Message Database                                │
├─────────────────────────────────────────────────────────────────────┤
│  [📋 All Messages]  [💬 Reply to Messages]  ← TABS                 │
├───────────────────┬─────────────────────────────────────────────────┤
│                   │                                                 │
│  📥 INCOMING      │  📜 CONVERSATION HISTORY                       │
│                   │  ┌─────────────────────────────────────────┐   │
│  📖 +1619977...   │  │ 2025-11-07 03:30 PM PDT                │   │
│  | 2025-11-07     │  │ 👤 THEM:                                │   │
│  | Message...     │  │ What are your hours?                    │   │
│                   │  │ ----------------------------------      │   │
│  💬 +1858555...   │  │                                         │   │
│  | 2025-11-06     │  │ 2025-11-07 03:15 PM PDT [sent]         │   │
│  | Hello...       │  │ 🤖 YOU:                                 │   │
│                   │  │ Thanks for your order!                  │   │
│  [🔄 Refresh]     │  └─────────────────────────────────────────┘   │
│                   │                                                 │
│                   │  ✍️ YOUR REPLY                                  │
│                   │  ┌─────────────────────────────────────────┐   │
│                   │  │ 💬 Replying to: +16199773020           │   │
│                   │  │                                         │   │
│                   │  │ [Type your reply here...]              │   │
│                   │  │                                         │   │
│                   │  └─────────────────────────────────────────┘   │
│                   │  55 / 160 characters          [🗑️ Clear]       │
│                   │                    [📤 Queue Reply (Send)]      │
└───────────────────┴─────────────────────────────────────────────────┘
```

---

## ⚙️ Technical Details

### Database Integration
- **Reads**: `messages` table where `direction='inbound'`
- **Writes**: Inserts with:
  ```json
  {
    "phone_number": "+1234567890",
    "content": "Your reply text",
    "direction": "outbound",
    "status": "queued",
    "timestamp": "2025-11-07T22:30:00Z"
  }
  ```

### Message Status Flow
1. **queued** → Inserted by viewer, waiting for conductor
2. **sent** → Successfully sent by conductor
3. **failed** → Send attempt failed (will retry)

### Character Counting
- **0-140**: Gray text (safe)
- **140-160**: Orange text (near limit)
- **160+**: Orange + "WILL BE SPLIT" warning (long SMS splits into multiple)

---

## 👤 Contact Name Resolution

### How It Works

The SMS Viewer automatically looks up customer names when displaying phone numbers:

1. **Cache Check** - Checks in-memory cache first (fast)
2. **CRM Lookup** - Queries `customers` table in Blaze IC database
3. **Fallback** - Shows phone number if no match found

### Database Search Order

**Priority 1: IC Database (Blaze Customers)**
- Table: `customers`
- Searches by: `phone` field
- Example: `+16199773020` → "John Doe"

**Priority 2: XB Database (SMS Contacts)**
- Table: `contacts` (future feature)
- Local SMS contact names
- Example: Custom nicknames

### Display Formats

**Customer Found**:
```
📖 John Doe (+16199773020) | 2025-11-07 03:30 | What are your hours...
```

**Customer Not Found**:
```
📖 +16199773020 | 2025-11-07 03:30 | What are your hours...
```

### Benefits

✅ **Instant Recognition** - See who's texting immediately  
✅ **No Manual Entry** - Pulls from existing CRM data  
✅ **Cached for Speed** - Second lookup is instant  
✅ **VIP Identification** - Know your high-value customers  
✅ **Context Awareness** - See purchase history in CRM

### Example: Customer Journey

1. **Customer texts**: "Do you have Blue Dream in stock?"
2. **SMS Viewer shows**: 
   - Left panel: `💬 Sarah Johnson (+18585551234) | 2025-11-07 03:30 | Do you have Blue...`
   - Reply label: `💬 Replying to: Sarah Johnson (+18585551234)`
3. **You know**: This is Sarah, you can check her purchase history in IC Viewer
4. **Personal reply**: "Hi Sarah! Yes we have Blue Dream. Based on your last visit, you might also like our new Gelato strain!"

### Troubleshooting

**Phone number not resolving to name**:
- Check if customer exists in CRM: Open IC Viewer, search by phone
- Ensure phone format matches (E.164: `+1234567890`)
- Try refreshing: Close and reopen SMS Viewer

**Wrong name showing**:
- Check for duplicate phone numbers in CRM
- Verify phone number format is consistent
- Clear cache by restarting viewer

---

## 🔍 Troubleshooting

### "No incoming messages found"
**Cause**: No inbound messages in database yet  
**Fix**: Send a test SMS to your modem number first

### Reply not sending
**Cause**: `conductor_system.py` not running  
**Fix**: Start conductor with `.\start_conductor.bat`

### Can't see conversation history
**Cause**: Invalid phone number format  
**Fix**: Ensure phone is in E.164 format (`+1234567890`)

### Message shows as "queued" forever
**Cause**: Conductor not polling or modem offline  
**Fix**: 
1. Check logs: `Get-Content logs\conductor_system.log -Tail 50`
2. Check modem: `python modem_probe.py`
3. Restart conductor

---

## 📊 Comparison with AI Bot

| Feature | Manual Reply Tab | MotaBot AI (n8n) |
|---------|------------------|------------------|
| **Speed** | Instant (manual) | Automatic (15-30s) |
| **Use Case** | Quick responses, overrides | Standard customer queries |
| **Control** | Full manual control | AI-generated responses |
| **Integration** | Direct to database | Via n8n workflow |
| **Best For** | Urgent replies, testing | High-volume automation |

**Tip**: Use manual replies for:
- Testing conversations
- VIP customers needing immediate attention
- Complex queries AI can't handle
- System debugging

---

## 🎯 Best Practices

### 1. Keep Messages Concise
- Under 160 characters = single SMS
- Over 160 = splits into multiple (costs more)
- Aim for 140-150 characters max

### 2. Use Professional Tone
- Customer sees this as official business communication
- Proofread before sending
- Use proper grammar and punctuation

### 3. Monitor Conversation History
- Check previous messages before replying
- Ensure context makes sense
- Note message status (sent vs failed)

### 4. Refresh Often
- Click "🔄 Refresh Incoming" for latest messages
- Conversation auto-refreshes after sending
- Check "All Messages" tab for delivery status

### 5. Handle Failed Messages
- If status shows `[failed]`, message didn't send
- Copy message content
- Delete failed message
- Queue fresh copy

---

## 🆕 What's New (v2.1)

**Added**:
- ✅ Two-tab interface (All Messages + Reply to Messages)
- ✅ Incoming message list with phone grouping
- ✅ Full conversation threading
- ✅ Manual reply composer
- ✅ Live character counter with warnings
- ✅ Color-coded chat history
- ✅ Auto-refresh after sending
- ✅ Status tracking in conversation view

**Unchanged**:
- ✅ All existing features in "All Messages" tab
- ✅ Database editing, status changes, deletion
- ✅ Test conversation builder
- ✅ Message search and sorting

---

## 📝 Summary

**The SMS Manual Reply Tab lets you**:
1. See all incoming messages at a glance
2. Click any message to view full conversation
3. Type a reply with character counting
4. Queue reply for instant sending (within 5 seconds)
5. Track delivery status in real-time

**Perfect for**:
- Quick manual responses
- Testing SMS conversations
- VIP customer support
- Debugging message flow

**Launch**:
```powershell
.\start_SMSconductor_DB.bat
```

**Click**: `💬 Reply to Messages` tab

**Start replying!** 🚀

---

## 🔗 Related Documentation

- `README.md` - SMS Conductor system overview
- `CONDUCTOR_ARCHITECTURE.md` - Technical architecture
- `WORKLOG.md` - Development history
- `DATABASE_VIEWERS_GUIDE.md` - All viewer tools

---

**Questions or issues?** Check logs: `Get-Content logs\conductor_system.log -Tail 50`

