# MotaBot AI - Intelligent SMS Chatbot for n8n
**Version**: 5.100 COMPATIBLE  
**Status**: Production  
**Last Updated**: October 11, 2025

---

## 🎯 Overview

**MotaBot AI** is an intelligent AI-powered chatbot that automatically responds to incoming SMS messages. It integrates with **Conductor SMS** (for messaging) and **MoTa CRM** (for customer data) to provide personalized, context-aware responses.

### Key Features:
- ✅ **Automatic SMS Response** - Reads unread SMS, generates AI replies
- ✅ **CRM Integration** - Queries customer data (name, VIP status, visits, lifetime value)
- ✅ **Conversation History** - Maintains context across multiple messages
- ✅ **Email Integration** - Can send emails in addition to SMS
- ✅ **Gmail Tool** - AI can look up customer email and send via Gmail
- ✅ **Personalized AI** - Uses customer data to tailor responses
- ✅ **n8n Compatible** - Pure workflow, no custom nodes required

---

## 🚀 Quick Start

### 1. Prerequisites

**Software Required**:
- **n8n** (self-hosted or cloud) - https://n8n.io
- **Supabase account** - https://supabase.com
- **OpenAI API key** (or other AI provider)
- **Conductor SMS** running (for sending responses)

### 2. Import Workflow

1. Open n8n
2. Go to **Workflows** → **Import from File**
3. Select: `workflows/active/MotaBot wDB v5.100 COMPATIBLE.json`
4. Workflow imports successfully ✅

### 3. Configure Credentials

**Supabase Credentials**:
1. In n8n, go to **Credentials**
2. Create new **Supabase** credential
3. Enter:
   - Project URL: `https://your-project.supabase.co`
   - API Key: `your-anon-key`

**OpenAI Credentials** (or your AI provider):
1. Create **OpenAI** credential
2. Enter API key

**Gmail Credentials** (optional, for email integration):
1. Create **Gmail OAuth2** credential
2. Follow n8n's Gmail setup guide

### 4. Activate Workflow

1. Click **Active** toggle in top-right
2. Workflow starts polling Supabase for unread messages
3. Done! ✅

---

## 🔄 How It Works

### Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                      MOTABOT WORKFLOW                         │
│                                                               │
│  1. Poll Supabase (every 5 seconds)                          │
│     ↓                                                         │
│  2. Find unread inbound messages                             │
│     ↓                                                         │
│  3. Get conversation history (same phone number)             │
│     ↓                                                         │
│  4. Query CRM data for this customer                         │
│     ↓                                                         │
│  5. Prepare AI context (history + CRM data)                  │
│     ↓                                                         │
│  6. Send to AI agent (OpenAI)                                │
│     ↓                                                         │
│  7. Receive AI response                                      │
│     ↓                                                         │
│  8. Split into SMS chunks (≤150 chars)                       │
│     ↓                                                         │
│  9. Write to Supabase (status: queued)                       │
│     ↓                                                         │
│ 10. Mark original message as read                            │
│     ↓                                                         │
│ 11. Conductor sends queued messages                          │
└──────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI Agent Configuration

### System Prompt

MotaBot uses a specialized AI persona:

**Key Characteristics**:
- 💼 Professional budtender/sales rep
- 🌿 Cannabis industry expert
- 💬 Conversational, not salesy
- 🔒 Privacy-aware (no customer data leakage)
- ✅ Confident and informative
- 📧 Can send emails over text

**System Prompt Structure**:
```
You are MotaBot, a professional budtender AI assistant for a cannabis dispensary.

CUSTOMER DATA (automatically provided):
- Name: [from CRM]
- VIP Status: [from CRM]
- Total Visits: [from CRM]
- Lifetime Value: [from CRM]
- Last Visit: [from CRM]

TOOLS AVAILABLE:
- Gmail: Send emails to customers
- Data Tables: Look up customer info, product inventory

CONVERSATION HISTORY:
[Previous messages with this customer]

GUIDELINES:
- Use customer data to personalize responses
- Be confident and informative, not salesy
- Don't mention "discovery" or "1:1 texts"
- If customer info is available, use it naturally
- Can send emails via text
- ...
```

---

## 📊 CRM Data Integration

### Automatic CRM Lookup

For every incoming message, MotaBot automatically:
1. Queries Supabase `customers` table by phone number
2. Retrieves:
   - Customer name
   - VIP status
   - Total visits
   - Lifetime value
   - Last visit date
3. Injects this data into AI's conversation context

**Example**:
```
Incoming SMS: "Do I have any points?"

CRM Data Found:
- Name: Aaron Campos
- VIP: Yes
- Visits: 47
- Lifetime Value: $3,204.50
- Last Visit: 2024-09-28

AI Response: "Hi Aaron! Yes, you have 320 reward points available
to redeem. As one of our VIP customers with 47 visits, you've
earned great benefits! Would you like to use your points on your
next visit?"
```

**Privacy Note**: AI only sees THIS customer's data, never other customers' data.

---

## 📧 Email Integration

### Gmail Tool

MotaBot can send emails directly from SMS conversation:

**Customer**: "Can you email me the menu?"

**AI**: Uses Gmail tool to send email with menu PDF attached.

**Setup**:
1. Configure Gmail OAuth2 credential in n8n
2. AI automatically detects when email is needed
3. Looks up customer email from CRM
4. Sends email via Gmail node

---

## 🔧 Workflow Nodes

### Key Nodes

| Node | Purpose |
|------|---------|
| **Schedule Trigger** | Polls every 5 seconds |
| **Get Unread Messages** | Queries Supabase for `status='unread'` |
| **Filter Unread Messages** | Extracts unread inbound messages |
| **Get Conversation History** | Fetches last messages with this number |
| **Prepare for AI** | Queries CRM, formats context |
| **AI Agent** | OpenAI chat completion |
| **Prepare SMS Response** | Sanitizes AI output |
| **Split Into Chunks** | Breaks long messages into ≤150 char chunks |
| **Delay By Index** | Progressive delays between chunks |
| **Insert Message** | Writes to Supabase (status: queued) |
| **Mark Message Read** | Updates original message status |

---

## 🎛️ Configuration Options

### Poll Interval

**Default**: 5 seconds

**Change**:
1. Open **Schedule Trigger** node
2. Set interval (e.g., 10 seconds for less frequent polling)

### AI Model

**Default**: `gpt-4o-mini` (fast, cheap)

**Change**:
1. Open **AI Agent** node
2. Select model (e.g., `gpt-4` for better quality)

### Conversation History Limit

**Default**: Entire conversation history

**Change**:
1. Open **Get Conversation History** node
2. Adjust `.limit()` parameter

### Chunk Size

**Default**: 150 characters per SMS chunk

**Change**:
1. Open **Split Into Chunks** node
2. Change `const limit = 150;`

---

## 🧪 Testing

### Test 1: Simple Response

1. Send SMS to modem: "Hello"
2. Check n8n execution log
3. Verify AI response queued in Supabase
4. Verify Conductor sends response
5. Receive SMS reply

---

### Test 2: CRM Data Usage

1. Send SMS from a customer phone number in CRM
2. Send: "What's my name?"
3. AI should respond with customer's actual name from CRM

---

### Test 3: Long Message Chunking

1. Ask AI a complex question: "Tell me about the top 5 strains"
2. AI generates long response
3. Verify response split into multiple ≤150 char chunks
4. Verify chunks arrive in order with delays

---

### Test 4: Email Tool

1. Send: "Email me the menu"
2. AI uses Gmail tool
3. Customer receives email
4. SMS confirmation sent

---

## 🐛 Troubleshooting

### Issue: Workflow not triggering

**Check**:
- Workflow is **Active** (toggle in top-right)
- Schedule Trigger is enabled
- Supabase credentials are correct

**Test Supabase connection**:
1. Run **Get Unread Messages** node manually
2. Check for errors in execution log

---

### Issue: AI not responding

**Check**:
- OpenAI API key is valid
- OpenAI account has credits
- AI Agent node is configured correctly

**Test AI**:
1. Run **AI Agent** node manually with test input
2. Check execution output

---

### Issue: Messages not being sent

**Check**:
- Conductor SMS is running
- Messages are being written to Supabase with `status='queued'`
- Check Conductor logs for send errors

---

### Issue: CRM data not appearing in responses

**Check**:
- **Prepare for AI** node is querying Supabase correctly
- Customer phone number exists in `customers` table
- CRM data is being injected into `conversation` string

**Debug**:
1. Run **Prepare for AI** node manually
2. Check output JSON
3. Verify `conversation` includes CRM data

---

## 📁 File Structure

```
motabot-ai/
├── workflows/
│   ├── active/
│   │   └── MotaBot wDB v5.100 COMPATIBLE.json  ← Current production
│   └── archive/
│       ├── MotaBot v4.3 SMS+Email.json
│       ├── MotaBot wDB v5.100.json
│       └── older_versions/
│
├── docs/
│   ├── MOTABOT_V5.100_README.md   ← Detailed technical docs
│   ├── DEPLOYMENT_GUIDE.md        ← Step-by-step setup (TODO)
│   └── SYSTEM_PROMPT_GUIDE.md     ← AI prompt engineering (TODO)
│
└── README.md                       ← This file
```

---

## 🔄 Workflow Versioning

### Current Version: v5.100 COMPATIBLE

**Versioning Scheme**: `vMAJOR.MINOR`

- **MAJOR**: Breaking changes, significant rewrites
- **MINOR**: New features, improvements, fixes

**Version History**:
- **v5.100** (Oct 11, 2025) - CRM integration with Code nodes
- **v4.3** (Oct 10, 2025) - Email integration
- **v4.2** (Oct 9, 2025) - Gmail tool added
- **v4.1** (Oct 8, 2025) - Conversation history
- **v4.0** (Oct 7, 2025) - Initial Supabase integration

---

## 📈 Performance

**Typical Performance**:
- **Poll cycle**: 5 seconds
- **CRM query**: <1 second
- **AI response time**: 2-5 seconds (depends on model)
- **Total latency**: 7-10 seconds (incoming SMS → outgoing response)
- **Throughput**: ~6-8 conversations/minute

**Optimizations**:
- Use faster AI models (`gpt-4o-mini` vs `gpt-4`)
- Reduce conversation history limit
- Increase poll interval if traffic is low

---

## 🔐 Security & Privacy

### Customer Data

- ✅ AI only sees data for the customer it's responding to
- ✅ No other customers' data in AI context
- ✅ Phone numbers masked in logs
- ✅ Message content not logged (only metadata)

### API Keys

- ⚠️ Store in n8n credentials (encrypted)
- ⚠️ Never hardcode in workflow
- ⚠️ Rotate keys regularly

---

## 🔗 Integration

### With Conductor SMS

1. Conductor writes incoming SMS → Supabase `messages` (status: `unread`)
2. MotaBot reads `unread` → generates response → writes (status: `queued`)
3. Conductor reads `queued` → sends via modem → updates (status: `sent`)

### With MoTa CRM

1. MotaBot queries `customers` by phone number
2. Retrieves name, VIP status, visits, lifetime value
3. Uses data to personalize AI responses

---

## 🆘 Support

**Detailed workflow documentation**:
```
docs/MOTABOT_V5.100_README.md
```

**n8n Community**:
https://community.n8n.io

**GitHub**: https://github.com/mmamodelai/ConductorV4.1/issues

---

## 📜 Version History

### v5.100 COMPATIBLE - October 11, 2025
- CRM data injection via Code nodes
- No custom nodes (100% compatible)
- Entire conversation history
- Email + SMS support
- Gmail tool integration

### v4.3 - October 10, 2025
- Email integration
- Gmail tool
- System prompt improvements

### v4.0 - October 7, 2025
- Initial Supabase integration
- Basic AI responses
- Long message chunking

---

**🎉 MotaBot AI is production-ready! Intelligent, personalized SMS responses powered by AI and CRM data.**

