# SMS Campaign System (SMS SUG) - Architecture Design

**Created**: November 7, 2025  
**Status**: Planning Phase  
**Goal**: AI-generated, human-approved, scheduled SMS campaigns

---

## 🎯 Vision

Generate personalized retention/engagement SMS campaigns using customer data insights:
- "Haven't seen you in 60 days, here's a discount on flower"
- Staggered sending (looks natural, not mass blast)
- Human approval required before sending
- Separate from operational SMS system

---

## 🏗️ Architecture Decision: Separate Table

### ✅ **CHOSEN APPROACH**: Separate `campaign_messages` table + Scheduler

**Why separate?**
1. ✅ **Keeps Conductor simple and safe** - don't touch what works
2. ✅ **Clean separation**: operational SMS vs. marketing campaigns
3. ✅ **Easy to pause** campaigns without breaking MotaBot replies
4. ✅ **Better schema** for campaign-specific data
5. ✅ **Safer** - if campaign system breaks, operational SMS still works

### ❌ **REJECTED**: Adding SUG/APR/SCH to existing `messages` table

**Why not?**
- 🚨 Mixes operational SMS with campaign SMS
- Risk of breaking working Conductor system
- Status field becomes messy (7+ states)
- Hard to pause campaigns without affecting operational SMS
- No audit trail for approvals

---

## 📊 Database Schema

### New Table: `campaign_messages`

```sql
CREATE TABLE campaign_messages (
    id BIGSERIAL PRIMARY KEY,
    
    -- Target
    customer_id TEXT,
    phone_number TEXT NOT NULL,
    
    -- Message
    message_content TEXT NOT NULL,
    campaign_type TEXT, -- 'retention', 'welcome', 'vip_promo', etc.
    
    -- Status Flow
    status TEXT NOT NULL, -- 'suggested', 'approved', 'scheduled', 'sent', 'cancelled'
    
    -- Scheduling
    scheduled_send_time TIMESTAMPTZ, -- When to actually send
    
    -- Audit Trail
    suggested_date TIMESTAMPTZ DEFAULT NOW(),
    suggested_by TEXT DEFAULT 'AI', -- 'AI' or username
    
    approved_date TIMESTAMPTZ,
    approved_by TEXT, -- Username who approved
    
    sent_date TIMESTAMPTZ,
    conductor_message_id INTEGER, -- FK to messages.id when moved
    
    -- Context (why this message?)
    customer_context JSONB, -- {"days_since_visit": 60, "preferred_category": "Flower", "avg_spend": 45.50}
    campaign_batch_id TEXT, -- Group messages from same generation
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_campaign_status ON campaign_messages(status);
CREATE INDEX idx_campaign_scheduled ON campaign_messages(scheduled_send_time);
CREATE INDEX idx_campaign_batch ON campaign_messages(campaign_batch_id);
CREATE INDEX idx_campaign_customer ON campaign_messages(customer_id);
```

---

## 🔄 Workflow

### 1. AI Generation Phase
```
AI analyzes customer data
    ↓
Generates 30 personalized messages
    ↓
Inserts into campaign_messages (status: 'suggested')
    ↓
Assigns campaign_batch_id for grouping
```

### 2. Human Approval Phase
```
Human reviews in approval UI
    ↓
Sees: customer name, message, context (why this message)
    ↓
Approves/rejects/edits each message
    ↓
Sets staggered send times (10:15, 10:21, 10:40...)
    ↓
Updates status to 'approved'
```

### 3. Scheduled Sending Phase
```
campaign_scheduler.py runs every minute
    ↓
Finds: status='approved' AND scheduled_send_time <= NOW()
    ↓
Moves to messages table (status: 'queued')
    ↓
Sets conductor_message_id FK
    ↓
Updates campaign status to 'scheduled'
    ↓
Conductor picks it up and sends normally
    ↓
Updates campaign status to 'sent'
```

---

## 🛠️ Components

### 1. `campaign_generator.py` (AI System)
- Queries Blaze database for customer insights
- Generates personalized messages
- Inserts into `campaign_messages` with status='suggested'
- Tags with campaign_batch_id

### 2. `campaign_approval_ui.py` (Human Review)
- GUI to review suggested messages
- Shows customer context (why this message)
- Approve/reject/edit interface
- Sets staggered send times
- Updates status to 'approved'

### 3. `campaign_scheduler.py` (Daemon)
- Runs every minute (or as cron job)
- Checks for approved messages where time has arrived
- Moves to `messages` table with status='queued'
- Conductor handles the rest

### 4. Conductor (No Changes!)
- Keeps existing behavior
- Just sends anything with status='queued'
- Doesn't know/care about campaign system

---

## 📅 Staggered Sending Strategy

When approving 30 messages for tomorrow at 10am:

```python
import random
from datetime import datetime, timedelta

base_time = datetime(2025, 11, 8, 10, 0, 0)  # Tomorrow 10am

for i, msg in enumerate(approved_messages):
    # Random intervals between 1-15 minutes
    delay_minutes = random.randint(1, 15) * i
    msg.scheduled_send_time = base_time + timedelta(minutes=delay_minutes)
    msg.status = 'approved'
    msg.approved_by = current_user
    msg.approved_date = datetime.now()
```

Result:
- Message 1: 10:15
- Message 2: 10:21
- Message 3: 10:40
- Message 4: 10:43
- Message 5: 10:50
- Etc...

Looks natural, not like a mass blast! ✅

---

## 🔐 Safety Features

### 1. Rate Limiting
- Max messages per minute: 5
- Max messages per hour: 100
- Prevents accidental spam

### 2. Approval Required
- NO messages sent without human approval
- Clear audit trail (who approved, when)

### 3. Cancel Anytime
- Update status to 'cancelled' before sending
- Scheduler skips cancelled messages

### 4. Isolated System
- If campaign system breaks, operational SMS continues
- Conductor is untouched

### 5. Testing Mode
- Send to test numbers first
- Verify before going live

---

## 🎨 Example Campaign

### Scenario: 60-Day Inactive Flower Buyers

**Query Blaze DB:**
```sql
SELECT 
    c.member_id,
    c.phone,
    c.name,
    MAX(t.date) as last_visit,
    COUNT(ti.id) as flower_purchases
FROM customers_blaze c
JOIN transactions_blaze t ON c.member_id = t.customer_id
JOIN transaction_items_blaze ti ON t.transaction_id = ti.transaction_id
WHERE ti.category = 'Flower'
    AND t.date < NOW() - INTERVAL '60 days'
    AND c.text_opt_in = true
GROUP BY c.member_id
HAVING COUNT(ti.id) >= 5;
```

**AI Generates Messages:**
```
"Hey Sarah! We haven't seen you in 2 months and miss you! 
Here's 10% off any flower strain this week. See you soon! 🌿"
```

**Stored as:**
```json
{
  "customer_id": "12345",
  "phone_number": "+16199773020",
  "message_content": "Hey Sarah! We haven't...",
  "status": "suggested",
  "customer_context": {
    "days_since_visit": 63,
    "preferred_category": "Flower",
    "lifetime_purchases": 28,
    "avg_spend": 42.50
  }
}
```

**Human reviews → Approves → Schedules for 10:15am tomorrow**

**Scheduler moves to messages at 10:15am**

**Conductor sends normally**

---

## 📊 Monitoring & Analytics

### Track Campaign Performance

```sql
-- Campaign success rate
SELECT 
    campaign_type,
    COUNT(*) as total_sent,
    COUNT(CASE WHEN status = 'sent' THEN 1 END) as successfully_sent,
    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled
FROM campaign_messages
WHERE approved_date >= NOW() - INTERVAL '30 days'
GROUP BY campaign_type;

-- Response rate (requires tracking replies)
SELECT 
    cm.campaign_type,
    COUNT(DISTINCT cm.phone_number) as customers_messaged,
    COUNT(DISTINCT m.phone_number) as customers_replied,
    ROUND(COUNT(DISTINCT m.phone_number)::numeric / 
          COUNT(DISTINCT cm.phone_number) * 100, 2) as response_rate
FROM campaign_messages cm
LEFT JOIN messages m ON cm.phone_number = m.phone_number
    AND m.direction = 'inbound'
    AND m.timestamp > cm.sent_date
    AND m.timestamp < cm.sent_date + INTERVAL '7 days'
WHERE cm.status = 'sent'
    AND cm.sent_date >= NOW() - INTERVAL '30 days'
GROUP BY cm.campaign_type;
```

---

## 🚀 Implementation Phases

### Phase 1: Database & Scheduler ✅ **START HERE**
- [ ] Create `campaign_messages` table
- [ ] Build `campaign_scheduler.py`
- [ ] Test manually inserting messages
- [ ] Verify scheduler moves them to `messages`
- [ ] Confirm Conductor sends normally

### Phase 2: Simple Approval UI
- [ ] Build basic approval interface
- [ ] Show message + customer context
- [ ] Approve/reject buttons
- [ ] Set send time picker

### Phase 3: AI Generation
- [ ] Query Blaze DB for insights
- [ ] Generate messages using AI/templates
- [ ] Insert as 'suggested' status

### Phase 4: Advanced Features
- [ ] A/B testing campaigns
- [ ] Response tracking
- [ ] Performance analytics
- [ ] Template library

---

## 💡 Key Principles

1. **Keep Conductor Simple** - Don't touch what works
2. **Human in the Loop** - No auto-send without approval
3. **Natural Looking** - Staggered timing, personalized messages
4. **Audit Trail** - Track who approved what and when
5. **Safety First** - Rate limits, cancel anytime, testing mode

---

## 🤔 Open Questions

1. **Approval UI**: Web-based or desktop app?
2. **AI Model**: GPT-4 API or local templates?
3. **Response Tracking**: Link replies to campaigns automatically?
4. **Scheduler**: Python daemon or Supabase cron job?
5. **Rate Limits**: What's safe/comfortable for your business?

---

**Next Steps**: See `SMS SUG/ROADMAP.md` for implementation plan

**Status**: Ready to build Phase 1

