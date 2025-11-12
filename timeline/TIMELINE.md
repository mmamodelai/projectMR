# MoTA Rewards System Timeline
**Last Updated**: October 27, 2025  
**Team**: Stephen Clare & Aaron Frias (Engineers) | Luis (Client/MoTA Owner)  
**Status**: Planning Phase

---

## 🎯 System Architecture Overview

### The Complete System Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    MOTA INTELLIGENT CRM SYSTEM                    │
└──────────────────────────────────────────────────────────────────┘

1️⃣  BROADCAST ENGINE (Python - Daily 9 AM)
    ↓
    Analyzes 3,186 customers → Scores (0-100) → Selects top 75
    ↓
    Generates personalized opening lines
    ↓
    Writes to Supabase (status='queued' + metadata)

2️⃣  CONDUCTOR SMS (Polling every 10 seconds)
    ↓
    Finds status='queued' messages
    ↓
    Sends via modem → Updates status='sent'

3️⃣  CUSTOMER RECEIVES SMS
    ↓
    "Hey Jake! Ounce for $100 today. VIP first access!"
    ↓
    Customer replies: "Great! Coming in today."

4️⃣  SORTING AGENT (n8n - Polls every 5 seconds)
    ↓
    Reads status='unread'
    ↓
    Creates "baseball card":
      - Name: Jake
      - VIP: Yes, $5K/year
      - Location: Silver Lake
      - Context: Churn risk, ounce_100 campaign
      - Preferred budtender: Jacob
    ↓
    Routes to: IC AGENT (Silver Lake customer)

5️⃣  IC AGENT (n8n - Context-aware)
    ↓
    Reads context: VIP, churn risk, ounce $100
    ↓
    ACTION 1: Respond to Jake
      "Awesome Jake! Ounce ready for you. Jacob's here with your favorites!"
    ↓
    ACTION 2: Alert budtender Jacob (via Supabase)
      "VIP ALERT: Jake coming in for ounce $100. $5K/year customer we almost lost!"
    ↓
    ACTION 3: Log outcome to contacts_log (converted)

6️⃣  IB AGENT (n8n - Budtender handler)
    ↓
    Jacob receives VIP alert on his phone
    ↓
    Prepares for Jake's arrival

7️⃣  IN-STORE EXPERIENCE
    ↓
    Jake walks in → Jacob: "Hey Jake! Got your favorites ready!"
    ↓
    Customer retention SUCCESS 🎉

┌──────────────────────────────────────────────────────────────────┐
│  PARALLEL SYSTEMS (Same infrastructure, different purposes)      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  REX: Receipt → Points (Google Sheets + Gmail)                   │
│  XB: External budtenders (education PNGs via Bitly) [BLOCKED]    │
│  XC: External customers (rewards program) [BLOCKED]              │
│  IB: Internal budtenders (staff comms, VIP alerts)               │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Agent/Workflow Breakdown

| Agent | Type | Description | Status | Dependencies |
|-------|------|-------------|--------|--------------|
| **REX** | Closed-loop | Receipt processing → Points (Customer + Budtender) | 🟡 95% done | Small fix needed, then production |
| **XB** | External | Budtenders at OTHER dispensaries | 🔴 Blocked | Education PNGs from Luis, hosting setup |
| **XC** | External | Customers NOT ours, rewards program | 🔴 Blocked | Blaze API access, Luis clean data |
| **IC** | Internal | OUR customers (NOT rewards program) | 🟢 Working | ICv2.json workflow active |
| **IB** | Internal | OUR budtenders (NOT rewards program) | 🟡 Ready | Existing workflow, needs docs |
| **BROADCAST** | Analytics | AI-driven customer outreach based on sales patterns | 🔴 Planning | Blaze API, category definition |

---

## 🚨 CRITICAL BLOCKERS (Waiting on External Dependencies)

### 1. Luis - Education Material
- **Status**: 🔴 WAITING ON LUIS
- **Need**: Final drafts of education material (images, PDFs, etc.)
- **Use**: Send to External Budtenders (XB) via SMS with images
- **Owner**: Luis
- **Action**: Cannot proceed with XB workflow until received

### 2. Luis - Data Cleanup
- **Status**: 🔴 WAITING ON LUIS  
- **Need**: Clean, properly formatted data for import
- **Issue**: Current data too messy to use
- **Owner**: Luis (must do himself, we can't clean it for him)
- **Action**: Luis knows this, we're waiting

### 3. Blaze API Access
- **Status**: 🔴 WAITING ON API APPROVAL
- **Need**: Full API access for real-time customer data
- **Impact**: All systems need this for accurate data
- **Next Step**: Stephen to follow up (see tasks below)

---

## 📋 STEPHEN'S IMMEDIATE TASKS (Tomorrow AM)

### Priority 1: API Follow-Up
- [ ] **Follow up on Blaze API access request**
  - Check status with provider
  - Get timeline for approval
  - Escalate if needed

### Priority 2: Coordinate with Aaron (Spain)
- [ ] **Sync on technical tasks**
  - Image hosting test results
  - Bitly serialization approach
  - Chatbot improvements

---

## 📋 AARON'S TODO LIST (Aaron Frias - Spain)

**Focus**: Testing, serialization, and chatbot improvements

### 🔬 Testing & Infrastructure

- [ ] **Test motorewards.com image hosting**
  - Upload test PNG to website
  - Get direct URL structure
  - Test: Does URL work when texted to phone?
  - Document findings (preview behavior on iPhone/Android)

- [ ] **Serialize external budtender database**
  - Query Supabase for all external budtenders
  - Generate unique identifier per budtender (UUID or sequential)
  - Store in database: `budtender_id` → `unique_link_id`
  - Test Bitly API integration:
    - Create short link per budtender
    - Verify click tracking works
    - Store mapping: `budtender_id` → `bitly_url`
  - Document approach for Stephen

### 🤖 Chatbot Improvements (Ongoing)

- [ ] **Improve conversation quality**
  - Review current IC agent responses
  - Test edge cases (unclear requests, multiple questions)
  - Improve context retention across messages
  - Add fallback responses for unknown queries

- [ ] **Response time optimization**
  - Monitor AI processing latency
  - Test faster models if needed (e.g., gpt-4o-mini vs gemini)
  - Optimize n8n workflow nodes

- [ ] **Personalization enhancements**
  - Better use of customer data (VIP status, purchase history)
  - Tone adjustments (friendly but professional)
  - Product recommendations based on past purchases

### 📊 Nice-to-Have (Low Priority)

- [ ] **Analytics dashboard mockup**
  - Sketch what metrics we want to track
  - Conversion rates, response times, agent performance
  - Share ideas with Stephen

---

## 📧 GROUP EMAIL TODO LIST

**See `timeline/GROUP_EMAIL_TODO.md` for ready-to-send email to Aaron & Luis**

Quick summary of action items:

### Stephen (This Week)
- Follow up on Blaze API access (tomorrow AM)
- Fix Rex workflow (small issue)
- Define Broadcast Engine scoring formula
- Database schema updates (add metadata column, create contacts_log table)

### Aaron (This Week)
- Test motorewards.com image hosting
- Build Bitly serialization for external budtenders
- Improve chatbot conversation quality

### Luis (Need Timeline)
- Education PNGs for external budtenders (when ready?)
- Clean data for external customers/budtenders
- Define campaign types and values
- Review daily contact budget (75/day confirmed?)

---

## 🎬 NEXT ACTIONS (In Order)

1. **Stephen**: Follow up on API access (tomorrow AM)
2. **Stephen**: Meeting with Aaron - promo cards & education (tomorrow AM)
3. **Aaron**: Start research on image hosting & SMS preview
4. **Aaron**: Test Bitly integration with motorewards.com
5. **Aaron**: Document findings in this timeline
6. **Wait**: For Luis to provide education materials & clean data
7. **Wait**: For API access approval
8. **Build**: XB and XC workflows once blockers clear

---

## 📝 NOTES

### System Separation Rules
- **IC/IV workflows**: Do NOT involve Rex, rewards, or external people
- **REX workflow**: Completely closed-loop, only receipt → points
- **XB/XC workflows**: Only for external budtenders/customers, separate from IC/IV
- **No overlap**: These systems run in parallel, different databases/tables

### Development Principles
- One workflow = one agent = one purpose
- No monolithic workflows
- Each agent polls its own data source
- Shared Supabase for data consistency

---

## 🔧 SMS SYSTEM ARCHITECTURE (How It Works)

### Hardware Setup
- **Modem**: SIM7600G-H USB modem on COM24
- **Connection**: 115200 baud, serial communication
- **Polling**: Every 10 seconds (brief connect → read/send → disconnect)

### Database-Driven Message Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 CONDUCTOR SMS SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. n8n workflow writes message to Supabase:                │
│     - phone_number: +1234567890                             │
│     - content: "Your message here"                          │
│     - status: "queued"                                      │
│     - direction: "outbound"                                 │
│                                                              │
│  2. Conductor polls Supabase every 10 seconds               │
│     - Finds messages with status='queued'                   │
│     - Connects to modem                                     │
│     - Sends via AT+CMGS command                             │
│     - Updates status to 'sent' or 'failed'                  │
│     - Disconnects modem                                     │
│                                                              │
│  3. Incoming messages:                                      │
│     - Conductor polls modem for new SMS                     │
│     - Saves to Supabase with status='unread'                │
│     - n8n workflow polls for unread messages                │
│     - AI processes and responds                             │
│     - Marks message status='read'                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Points
- **No API calls to send SMS** - just write to Supabase with status='queued'
- **Conductor handles all modem communication** (polling-based, no COM port conflicts)
- **Message detection latency**: ~10 seconds max
- **GSM character encoding**: Automatic sanitization
- **Long messages**: Auto-split into ≤150 char chunks

---

## 🎯 BROADCAST SYSTEM (The Brain)

### Vision
**NOT an n8n workflow** - this is a Python script (built in Cursor) that intelligently ranks and selects the highest-value customer contacts.

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│           BROADCAST ENGINE (Python Script)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. DAILY BATCH JOB (runs once per day)                     │
│                                                              │
│  2. ANALYZE ALL CUSTOMERS                                   │
│     - Query Supabase for customer data                      │
│     - Calculate "Contact Value Score" (0-100) for each      │
│                                                              │
│  3. SCORING ALGORITHM                                       │
│     Score = Risk + Reward + Campaign Value                  │
│                                                              │
│     RISK FACTORS:                                           │
│     - Churn risk (hasn't visited in X days)                 │
│     - High-LTV customer about to leave = 100 points         │
│     - Low-LTV customer inactive = 20 points                 │
│                                                              │
│     REWARD FACTORS:                                         │
│     - Customer lifetime value                               │
│     - Average transaction size                              │
│     - Visit frequency                                       │
│                                                              │
│     CAMPAIGN VALUE:                                         │
│     - "Ounce for $100" = 100 (highest priority)             │
│     - "New product launch" = 75                             │
│     - "10% off edibles" = 5 (lowest priority)               │
│                                                              │
│  4. RANK ALL CUSTOMERS                                      │
│     - Sort by Contact Value Score (highest first)           │
│                                                              │
│  5. SELECT TOP N CONTACTS (daily budget)                    │
│     - Example: Top 75 customers per day                     │
│                                                              │
│  6. GENERATE OPENING LINES                                  │
│     - AI generates personalized message for each            │
│     - Context: Name, VIP status, reason for contact         │
│     - Example: "Hey Jake! We have ounces for $100 today.    │
│       As one of our VIPs, you get first access!"            │
│                                                              │
│  7. WRITE TO SUPABASE                                       │
│     - phone_number: +1234567890                             │
│     - content: "Generated opening line"                     │
│     - status: "queued"                                      │
│     - direction: "outbound"                                 │
│     - metadata: {                                           │
│         contact_reason: "churn_risk",                       │
│         campaign_type: "ounce_100",                         │
│         contact_value_score: 95,                            │
│         agent_target: "IC"                                  │
│       }                                                     │
│                                                              │
│  8. CONDUCTOR SENDS MESSAGES                                │
│     - Polls Supabase for status='queued'                    │
│     - Sends via modem                                       │
│     - Updates status='sent'                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Example Scoring

| Customer | LTV | Days Since Visit | Campaign | Score | Action |
|----------|-----|------------------|----------|-------|--------|
| Jake (VIP) | $5,000/year | 21 days | Ounce $100 | **95** | ✅ Contact (Top priority) |
| Sarah (Regular) | $1,200/year | 45 days | Ounce $100 | **80** | ✅ Contact |
| Mike (New) | $50 | 90 days | Ounce $100 | **25** | ⏸️ Skip (low value) |
| Lisa (Casual) | $300/year | 10 days | 10% off edibles | **5** | ⏸️ Skip (low urgency) |

**Budget**: 75 contacts/day → Top 75 scored customers get contacted

### Technical Architecture

**Language**: Python (built in Cursor, not n8n)

**Dependencies**:
- Supabase client (read customer data, write messages)
- OpenAI API (generate personalized opening lines)
- Pandas (data analysis, scoring algorithm)
- Schedule library (daily cron job)

**Script Location**: `conductor-sms/broadcast_engine.py` (to be created)

**Run Schedule**: Daily at 9:00 AM (before store opens)

**Output**: 75 messages written to Supabase with metadata for Sorting Agent

---

## 🎯 SORTING AGENT (The Router)

### Vision
An n8n workflow that creates a "baseball card" for every incoming phone number and routes messages to the correct agent (IC, IB, XB, XC).

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│              SORTING AGENT (n8n Workflow)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. POLL FOR INCOMING MESSAGES (every 5 seconds)            │
│     - Query Supabase: status='unread'                       │
│                                                              │
│  2. CREATE "BASEBALL CARD" FOR PHONE NUMBER                 │
│                                                              │
│     Phone: +1-619-977-3020                                  │
│     ┌──────────────────────────────────────────┐            │
│     │ NAME: Stephen Clare                      │            │
│     │ ROLE: System Admin (IC)                  │            │
│     │ LOCATION: Silver Lake                    │            │
│     │ VIP STATUS: Yes                          │            │
│     │ LTV: $5,000/year                         │            │
│     │ LAST VISIT: 21 days ago                  │            │
│     │                                           │            │
│     │ RECENT CONTACT:                          │            │
│     │ - Reason: Churn Risk                     │            │
│     │ - Campaign: Ounce for $100               │            │
│     │ - Sent by: Broadcast Engine              │            │
│     │ - Agent: IC                               │            │
│     │                                           │            │
│     │ PREFERRED BUDTENDER: Jacob                │            │
│     └──────────────────────────────────────────┘            │
│                                                              │
│  3. LOOKUP LOGIC                                            │
│     Query Supabase:                                         │
│     - customers table (by phone)                            │
│     - messages table (last outbound message to this phone)  │
│     - Extract metadata: contact_reason, campaign, agent     │
│                                                              │
│  4. ROUTING DECISION                                        │
│     If phone in customers table:                            │
│       - location = "Silver Lake" → IC Agent                 │
│       - location = "External" → XC Agent                    │
│     If phone in budtenders table:                           │
│       - works_at = "Silver Lake" → IB Agent                 │
│       - works_at = "External" → XB Agent                    │
│     If phone not found:                                     │
│       → Default Agent (generic response)                    │
│                                                              │
│  5. PASS MESSAGE + CONTEXT TO AGENT                         │
│     Send to appropriate agent with full context:            │
│     {                                                        │
│       "phone": "+16199773020",                              │
│       "message": "Great! I'll come by today.",              │
│       "customer": {                                         │
│         "name": "Stephen Clare",                            │
│         "vip_status": "Yes",                                │
│         "ltv": 5000,                                        │
│         "preferred_budtender": "Jacob",                     │
│         "location": "Silver Lake"                           │
│       },                                                    │
│       "context": {                                          │
│         "contact_reason": "churn_risk",                     │
│         "campaign": "ounce_100",                            │
│         "last_contact": "2025-10-20"                        │
│       }                                                     │
│     }                                                       │
│                                                              │
│  6. MARK MESSAGE AS ROUTED                                  │
│     - Update status: 'unread' → 'routed'                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Routing Logic Table

| Phone Found In | Location/Type | Route To | Example |
|----------------|---------------|----------|---------|
| `customers` | Silver Lake | **IC Agent** | Stephen (VIP, our customer) |
| `customers` | External | **XC Agent** | Maria (rewards program) |
| `budtenders` | Silver Lake | **IB Agent** | Jacob (our budtender) |
| `budtenders` | External | **XB Agent** | Luis (external budtender) |
| Not found | N/A | **Default Agent** | Unknown number |

### Database Schema Updates Needed

**New columns in `messages` table**:
```sql
ALTER TABLE messages ADD COLUMN metadata JSONB;
ALTER TABLE messages ADD COLUMN routed_to_agent TEXT;
```

**Example metadata**:
```json
{
  "contact_reason": "churn_risk",
  "campaign_type": "ounce_100",
  "contact_value_score": 95,
  "agent_target": "IC",
  "broadcast_date": "2025-10-27"
}
```

**New table: `contacts_log`** (track all broadcast contacts)
```sql
CREATE TABLE contacts_log (
  id UUID PRIMARY KEY,
  phone_number TEXT,
  contact_date DATE,
  contact_reason TEXT,
  campaign_type TEXT,
  contact_value_score INT,
  message_sent TEXT,
  response_received TEXT,
  response_date TIMESTAMPTZ,
  agent_routed_to TEXT,
  outcome TEXT  -- 'converted', 'replied', 'no_response'
);
```

---

## 🎯 AGENT SYSTEM (IC, IB, XB, XC)

### IC Agent (Internal Customers)

**Purpose**: Handle OUR customers at OUR dispensaries

**Context-Aware Actions**:

```
INCOMING MESSAGE: "Great! I'll come by today."

AGENT ANALYZES CONTEXT:
- Customer: Stephen Clare (VIP)
- Reason for contact: Churn risk (21 days since visit)
- Campaign: Ounce for $100
- Location: Silver Lake
- Preferred Budtender: Jacob

AGENT ACTIONS:

1. RESPOND TO CUSTOMER:
   "Awesome Stephen! We'll have an ounce ready for you. 
    Jacob will be here today and he's got your favorites in stock. 
    See you soon! 🙌"

2. MESSAGE BUDTENDER JACOB (via Supabase):
   Phone: Jacob's cell
   Message: "VIP ALERT: Stephen Clare coming in today for ounce $100 deal. 
            He's a $5K/year customer we almost lost. Make it special! 
            His favorites: [Product X, Product Y]"
   Status: queued

3. LOG OUTCOME TO SUPABASE:
   contacts_log: outcome = 'converted'
```

**Technical Implementation**:
- n8n workflow: `IC_Agent_v2.json` (already exists)
- Add context-aware logic:
  - Read metadata from Sorting Agent
  - Query customer preferences
  - Generate personalized response
  - Trigger budtender notification if VIP

### IB Agent (Internal Budtenders)

**Purpose**: Handle OUR budtenders at OUR dispensaries

**Use Cases**:
- Staff scheduling
- Inventory notifications
- VIP customer alerts (from IC agent)
- Performance updates

**Technical Implementation**:
- n8n workflow: `IB_Agent.json` (needs to be created/documented)

### XB Agent (External Budtenders)

**Purpose**: Handle budtenders at OTHER dispensaries (rewards program)

**Use Cases**:
- Education material delivery (PNGs via Bitly links)
- Rewards program updates
- Product training

**Blocked Until**:
- Luis provides PNG education materials
- Bitly integration setup
- motorewards.com hosting configured

**Technical Implementation**:
- n8n workflow: `XB_Agent.json` (needs to be created)

### XC Agent (External Customers)

**Purpose**: Handle customers NOT ours (rewards program)

**Use Cases**:
- Rewards program inquiries
- Cross-dispensary promotions
- Loyalty points

**Blocked Until**:
- Blaze API access (for cross-dispensary data)
- Luis provides clean data

**Technical Implementation**:
- n8n workflow: `XC_Agent.json` (needs to be created)

## ❓ QUESTIONS FOR YOU (Stephen)

### 1. Broadcast Engine Scoring
- **What's the formula?** Exactly how to weight risk + reward + campaign?
  - Example: High LTV (5K/year) + 21 days since visit + Ounce $100 campaign = what score?
  - What's the minimum score to contact? (e.g., don't contact anyone below 20?)
  
- **Campaign value assignments**:
  - Ounce for $100 = 100 (confirmed)
  - 10% off edibles = 5 (confirmed)
  - New product launch = ?
  - Birthday/loyalty rewards = ?
  - Custom campaigns = how to define?

- **Daily budget**:
  - 75 contacts per day (confirmed)
  - Can this vary by day? (e.g., 100 on Friday, 50 on Monday?)
  - Split by location? (50 Silver Lake, 25 other?)

### 2. Blaze API Integration
- **What data fields do we pull?**
  - Customer: purchase history, visit dates, products bought, amounts spent?
  - Real-time data or daily sync?
  - Where to store? (Existing `customers`/`transactions` tables or new?)
  
- **API rate limits?**
  - How many calls per day?
  - Do we cache data locally?
  
- **When do you expect API access?**
  - Stephen following up tomorrow - ETA days? weeks?

### 3. Budtender Phone Numbers
- **Do we have budtender phone numbers in database?**
  - Need this for IB agent (VIP alerts from IC agent)
  - Where stored? (New `budtenders` table? Or in `staff`?)
  
- **Budtender preferences**:
  - How do we know which budtender to notify?
  - Is it in `customers.preferred_budtender` field?
  - What if budtender isn't working that day?

### 4. Rex Workflow
- **What's broken?** Specific error/symptom?
- **Where is it deployed?** (n8n workflow active? needs import?)
- **Timeline to fix?** (Hours? Days?)

### 5. Database Schema - Do These Tables Exist?

| Table | Exists? | Columns Needed |
|-------|---------|----------------|
| `customers` | ✅ Yes | phone, name, vip_status, lifetime_value, preferred_location, preferred_budtender |
| `budtenders` | ❓ | id, name, phone, location, active |
| `staff` | ✅ Yes (3,299 records?) | Can this be used for budtenders? |
| `contacts_log` | ❌ No | Need to create (see schema in doc) |
| `messages.metadata` | ❌ No | Need to add JSONB column |

**Question**: Can we use `staff` table for budtender phone lookups? Or create separate `budtenders` table?

### 6. Approval Workflow
- **Is Broadcast Engine fully automated?**
  - Or does someone review the 75 contacts before sending?
  - Who has final say? (You? Aaron? Luis?)
  
- **What if AI generates bad message?**
  - Manual review?
  - Automated filters? (e.g., no profanity, must include campaign name)

### 7. Luis Dependencies
- **Education PNGs**:
  - How many files? (ballpark: 5, 10, 50?)
  - When will they be ready? (days, weeks, months?)
  - Who uploads to motorewards.com? (Luis? Aaron? You?)
  
- **Clean data**:
  - What data specifically? (External customers? External budtenders?)
  - What format? (CSV? Direct Supabase import?)
  - ETA?

### 8. Sorting Agent Routing - Edge Cases
- **What if customer is in database but location is NULL?**
  - Route to IC or Default Agent?
  
- **What if phone number matches multiple customers?**
  - (e.g., shared phone, family account)
  - Pick most recent? Highest LTV? Ask user?
  
- **What if reply comes from unknown number?**
  - Add to database automatically?
  - Send to Default Agent for manual review?

### 9. Campaign Management
- **How do you define new campaigns?**
  - Manual entry in Python script?
  - Config file (JSON/YAML)?
  - Database table with campaign definitions?
  
- **Example campaign definition needed**:
  ```json
  {
    "campaign_id": "ounce_100",
    "campaign_name": "Ounce for $100",
    "campaign_value": 100,
    "message_template": "Hey {name}! We have ounces for $100 today...",
    "start_date": "2025-10-27",
    "end_date": "2025-10-31",
    "target_segment": "VIP"
  }
  ```
  
  **Does this structure work? Or different format?**

---

## 🔄 UPDATE LOG

| Date | Update | By |
|------|--------|-----|
| 2025-10-27 | Initial timeline created | Agent |
| 2025-10-27 | Added SMS architecture explanation, Broadcast system vision | Agent |
| 2025-10-27 | Fixed: IB (not IV), Rex status (95% done), PNG image delivery research | Agent |
| 2025-10-27 | **MAJOR UPDATE**: Broadcast Engine (Python, not n8n), Sorting Agent (baseball card router), Context-aware agents with budtender notifications | Agent |
| 2025-10-27 | **FIXED TEAM STRUCTURE**: Stephen & Aaron = engineers, Luis = client/owner. Simplified Aaron's todo list (testing, serialization, chatbot) | Agent |

---

**Remember**: This is ONE document. All updates go here. No separate files for each system.

