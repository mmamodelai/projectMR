# Blaze API - Sandbox Demo & Production Promotion Plan

## What Blaze Needs to See in Sandbox

Based on Paul's email and the integration rules, Blaze needs to see:

### 1. **Proper Integration Working**
- API calls following pagination rules
- Rate limit compliance (under 10K calls per 5 minutes)
- Proper use of modified dates for incremental syncs
- Data handling according to their rules

### 2. **Technical Demonstrations**
- Fetching products/inventory correctly
- Fetching transactions properly
- Fetching members/customers correctly
- Using incremental sync (modified dates)
- Respecting rate limits
- Proper error handling

### 3. **Use Case Demonstration**
From Paul's email, we mentioned:
- "Automating Budtender performance reporting"
- "Customer Visits & Purchase Reporting"

We need to show we can:
- Pull transaction data
- Pull customer/member data
- Pull product data
- Process this data for our use case
- Follow all their rules

## Production Promotion Requirements

From the rules document:

### **Financial**
- Integration set-up fee: $_____ (amount not specified, needs to be determined)
- Tier pricing starts after promotion to production
- Initial 90 days: No overage fees, but tier adjustments still made

### **Operational Compliance**
- Follow pagination rules ✅
- Respect rate limits ✅
- Use modified dates for incremental syncs ✅
- Proper data handling ✅

### **Technical Readiness**
- API integration working in sandbox ✅
- Data mapping to our system
- Error handling in place
- Monitoring/logging setup

## Our Sandbox Demo Plan

### **Phase 1: Basic Data Fetching** (Current)
- ✅ Connect to STAGE API
- ✅ Fetch products (working!)
- ✅ Fetch transactions (working!)
- ⏳ Fetch customers/members
- ⏳ Show data structure

### **Phase 2: Incremental Sync Demo**
- Implement modified date filtering
- Show incremental customer sync
- Show incremental transaction sync
- Show incremental product sync
- Demonstrate following Blaze's timing rules

### **Phase 3: Integration with Our System**
- Map Blaze data to our Supabase schema
- Show data sync to our database
- Demonstrate updating customer calculated fields
- Show real-time data accuracy

### **Phase 4: Use Case Demonstration**
- Show budtender performance reporting
- Show customer visit tracking
- Show purchase pattern analysis
- Demonstrate value to business

## What We Should Build/Demo

### **Minimum Viable Demo:**
1. **Customer Sync Script**
   - Fetch customers with modified date filtering
   - Sync to our Supabase customers table
   - Show incremental updates working

2. **Transaction Sync Script**
   - Fetch transactions with date range
   - Sync to our Supabase transactions table
   - Show data accuracy

3. **Rate Limit Monitor**
   - Track API call volume
   - Ensure we stay under 10K per 5 minutes
   - Show compliance

4. **Data Mapping Documentation**
   - How we map Blaze → Supabase
   - Data transformation logic
   - Duplicate handling

### **What We Should Show Paul:**
- Working API integration ✅
- Data syncing correctly to our system
- Following Blaze's rules
- Ready for production promotion
- Clear use case demonstration

## Next Steps

1. **Build sync scripts** for sandbox demo
2. **Show Paul the working integration**
3. **Discuss production promotion timeline**
4. **Finalize integration fee amount**
5. **Get production credentials**
6. **Deploy to production**

## Questions for Paul

1. What's the integration set-up fee amount?
2. What's the timeline for production promotion?
3. What specific demo elements would you like to see?
4. Are there any additional requirements for production access?
5. What's the process for production promotion?

---

**Status**: We have working sandbox access ✅
**Next**: Build demo integration to show Paul
**Goal**: Get production promotion approval
