# MoTA Rewards System - Group TODO List

**To**: Aaron Frias, Luis  
**From**: Stephen Clare  
**Date**: October 27, 2025  
**Subject**: MoTA Rewards System - Action Items & Next Steps

---

Hey team,

We've mapped out the complete MoTA Rewards system architecture and identified what each of us needs to do to move forward. Here's the breakdown:

---

## 🎯 **SYSTEM OVERVIEW (Quick Recap)**

We're building an intelligent SMS-based customer retention system with these components:

1. **Broadcast Engine**: Python script that analyzes customers daily, scores them (0-100), and sends personalized messages to the top 75
2. **Sorting Agent**: Routes incoming replies to the correct handler (IC, IB, XB, XC agents)
3. **Context-Aware Agents**: Respond based on why we contacted the customer + their history
4. **Rex**: Receipt processing for points (separate closed-loop system)
5. **XB/XC**: External budtenders & customers (rewards program)

**Current Status**: SMS infrastructure working, IC agent functional, need to build Broadcast + Sorting systems

---

## 📋 **STEPHEN'S TODO LIST** (Priority Order)

### 🚨 This Week

- [ ] **Follow up on Blaze API access** (Tomorrow AM)
  - Contact provider for status update
  - Get ETA on approval
  - Escalate if needed
  - **Why**: We need real-time customer data for the Broadcast Engine

- [ ] **Fix Rex workflow** (2-3 hours)
  - Debug the small issue mentioned
  - Test Google Sheets integration (customer lookup, points calculation)
  - Test Gmail confirmations
  - **Status**: 95% done, just needs final fix

- [ ] **Define Broadcast Engine scoring formula** (With Aaron)
  - Risk factors: How to score churn risk? (e.g., $5K/year customer + 21 days since visit = ?)
  - Campaign values: Ounce $100 = 100, 10% off edibles = 5, others?
  - Minimum contact threshold: Don't contact anyone below score of X?
  - **Output**: Python script specifications for Aaron

- [ ] **Database schema updates** (1-2 hours)
  - Add `metadata` JSONB column to `messages` table
  - Add `routed_to_agent` TEXT column to `messages` table
  - Create `contacts_log` table (track broadcast campaign outcomes)
  - **SQL provided in timeline doc**

### 🔄 Next Week

- [ ] **Build Sorting Agent** (n8n workflow)
  - Poll for unread messages
  - Create "baseball card" (customer data + context)
  - Route to correct agent (IC, IB, XB, XC)
  - **Depends on**: Database schema updates complete

- [ ] **Update IC Agent** (context-aware)
  - Read metadata from Sorting Agent
  - Add budtender notification logic (VIP alerts)
  - Log outcomes to contacts_log
  - **Depends on**: Sorting Agent complete

---

## 📋 **AARON'S TODO LIST** (Aaron Frias - Spain)

### 🔬 Testing & Infrastructure

- [ ] **Test motorewards.com image hosting** (1-2 hours)
  - Upload a test PNG to website
  - Document URL structure (e.g., `https://motorewards.com/education/test.png`)
  - Test sending URL via SMS to your phone
  - Check: Does preview/thumbnail show on iPhone? Android?
  - **Report findings to Stephen & Luis**

- [ ] **Bitly serialization for external budtenders** (3-4 hours)
  - Query Supabase for all external budtenders
  - Generate unique ID per budtender (UUID or sequential)
  - Test Bitly API integration:
    - Create short link per budtender
    - Test click tracking
  - Store mapping in Supabase: `budtender_id` → `bitly_url`
  - **Deliverable**: Working prototype + documentation

- [ ] **Build Broadcast Engine** (Python script) - **After Stephen defines scoring**
  - Location: `conductor-sms/broadcast_engine.py`
  - Query Supabase for all customers
  - Implement scoring algorithm (Stephen to provide formula)
  - Sort by score, select top 75
  - Generate AI opening lines (OpenAI API)
  - Write to Supabase with metadata
  - Schedule: Daily at 9 AM
  - **Depends on**: Stephen defines scoring formula, Blaze API access (for customer data)

### 🤖 Chatbot Improvements (Ongoing)

- [ ] **Improve IC agent conversation quality**
  - Test edge cases (unclear requests, multiple questions)
  - Better context retention across messages
  - Improve personalization (use VIP status, purchase history)
  - **Goal**: Make responses feel more natural and helpful

- [ ] **Response time optimization**
  - Monitor current AI processing latency
  - Test faster models if needed (gpt-4o-mini vs gemini)
  - Optimize n8n workflow nodes

---

## 📋 **LUIS' TODO LIST** (MoTA Owner)

### 🚨 Critical Blockers (Need These to Proceed)

- [ ] **Education materials for external budtenders** (XB system)
  - Finalize PNG files (product education, training materials)
  - **Questions**:
    - How many files total? (ballpark: 5, 10, 50?)
    - What naming convention? (e.g., `mota_education_topic1.png`)
    - When will they be ready? (days, weeks?)
  - **Who uploads**: Aaron can handle upload to motorewards.com once ready
  - **Why we need this**: To send education materials to external budtenders via SMS

- [ ] **Clean external customer/budtender data**
  - Provide data in usable format (CSV, Excel, or direct Supabase access)
  - **What we need**:
    - External budtenders: Name, phone, dispensary, location
    - External customers: Name, phone, email, dispensary visited
  - **Format requirements**: 
    - Phone numbers in E.164 format: +1234567890
    - Clean data (no duplicates, valid phone numbers)
  - **Why we need this**: To build XB and XC agent workflows

### 🎯 Campaign Definitions (Work with Stephen)

- [ ] **Define campaign types and values**
  - We know: "Ounce for $100" = High priority (value: 100)
  - We know: "10% off edibles" = Low priority (value: 5)
  - **What else?**:
    - New product launches = ?
    - Birthday/loyalty rewards = ?
    - Seasonal promotions = ?
  - **For each campaign, define**:
    - Campaign name
    - Priority value (0-100)
    - Message template
    - Target customer segment (VIP, Regular, New, etc.)
    - Duration (start/end dates)

- [ ] **Review promo card structure** (Meeting with Stephen)
  - What promo types exist?
  - Who creates/approves them?
  - How often do they change?

### 📊 Business Rules

- [ ] **Daily contact budget**
  - Confirm: 75 SMS contacts per day?
  - Should this vary by day? (e.g., 100 on Friday, 50 on Monday?)
  - Split by location? (e.g., 50 Silver Lake, 25 other stores?)

- [ ] **Approval workflow**
  - Should broadcast messages be reviewed before sending?
  - Or fully automated?
  - Who has final say on message content?

---

## ⏰ **TIMELINE & DEPENDENCIES**

### This Week (Oct 28 - Nov 1)
- **Stephen**: Blaze API follow-up, Rex fix, scoring formula defined, database schema updates
- **Aaron**: Image hosting test, Bitly serialization prototype
- **Luis**: Provide timeline for education PNGs and clean data

### Next Week (Nov 4 - Nov 8)
- **Stephen**: Build Sorting Agent, update IC Agent
- **Aaron**: Build Broadcast Engine (once scoring defined), continue chatbot improvements
- **Luis**: Finalize campaign definitions

### Dependencies
```
Blaze API Access → Broadcast Engine (can't score customers without data)
Luis PNG Materials → XB Agent (can't send education to external budtenders)
Luis Clean Data → XC Agent (can't build external customer system)
Database Schema → Sorting Agent → Context-Aware IC/IB Agents
```

---

## 🎯 **SUCCESS METRICS**

### Short-term (2 weeks)
- Rex workflow 100% functional
- Broadcast Engine running daily (75 contacts/day)
- Sorting Agent routing messages correctly
- IC Agent responding with context awareness

### Long-term (1 month)
- VIP customer retention system active (IC → IB budtender alerts)
- External budtender education system (XB) sending materials
- External customer rewards program (XC) operational
- Analytics dashboard showing campaign performance

---

## 💬 **QUESTIONS FOR GROUP DISCUSSION**

1. **Scoring formula**: How should we weight churn risk vs. campaign value? (Stephen + Luis)
2. **Budtender alerts**: Should we notify budtenders for ALL VIPs or only high-risk ones? (Luis)
3. **Message approval**: Fully automated or manual review? (Luis)
4. **Edge cases**: What if customer in database but location is NULL? Default to IC agent? (Stephen + Aaron)

---

## 📞 **NEXT SYNC**

Suggest we schedule a group call once:
- Stephen has Blaze API update
- Aaron has image hosting test results
- Luis has timeline for education materials

**Proposed**: Early next week (Nov 4-5)?

---

Let me know if you have questions or need clarification on any of these items. Let's crush this! 🚀

**Stephen Clare**  
System Engineer, MoTA Rewards System

---

**P.S.**: Full technical documentation available in `timeline/TIMELINE.md` if you need more details on the architecture.





