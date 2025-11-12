# Customer Profile: STEPHEN CLARE (+16199773020)
**Generated**: October 12, 2025  
**Data Source**: Supabase CRM + SMS Databases

---

## 📋 CUSTOMER OVERVIEW

| Field | Value |
|-------|-------|
| **Name** | STEPHEN CLARE |
| **Phone** | +16199773020 |
| **Email** | None (❌ **MISSING**) |
| **Member ID** | 683cea4e022c82ba434de1df |
| **Customer Type** | Adult-Use |
| **State** | CA |
| **Zip Code** | 92071 (Santee, CA) |
| **Date Joined** | June 1, 2025 |
| **Last Visited** | June 4, 2025 (129 days ago) |

---

## 💰 FINANCIAL PROFILE

| Metric | Value |
|--------|-------|
| **Lifetime Value** | $148.80 |
| **Total Visits** | 3 |
| **Total Sales** | 3 |
| **Average Transaction** | $49.60 |
| **Loyalty Points** | 5.39 |
| **Total Refunds** | 0 |

---

## 🏆 STATUS & RISK

| Category | Status | Notes |
|----------|--------|-------|
| **VIP Status** | Casual | (2-5 visits) |
| **Churn Risk** | **HIGH** | 129 days since last visit! |
| **Member Group** | Adult-Use | Not medical |

**⚠️ ALERT: Customer hasn't visited in 4+ months!**

---

## 🛍️ TRANSACTION HISTORY

### Transaction 1: $87.74 (June 1, 2025)
- **Location**: MOTA (Silverlake)
- **Staff**: Lizbeth Garcia
- **Payment**: Cash
- **Terminal**: CASH REGISTER

### Transaction 2: $17.18 (June 2, 2025)
- **Location**: MOTA (Silverlake)
- **Staff**: Lizbeth Garcia
- **Payment**: Cash
- **Terminal**: CASH REGISTER

### Transaction 3: $8.53 (June 4, 2025)
- **Location**: MOTA (Silverlake)
- **Staff**: Lizbeth Garcia
- **Payment**: Cash
- **Terminal**: CASH REGISTER

**Pattern Detected**: All 3 visits within 4 days, then disappeared

---

## 📊 DERIVED INSIGHTS (from Supabase data)

### 1. ✅ **Visit Pattern**: "Quick Burst"
- Joined June 1, made 3 purchases in 4 days
- Never returned after June 4
- **Insight**: Was trying out the dispensary, didn't stick

### 2. ✅ **Spending Trend**: Declining
- Visit 1: $87.74 (baseline)
- Visit 2: $17.18 (80% decrease)
- Visit 3: $8.53 (50% decrease)
- **Insight**: Lost interest or found alternative

### 3. ✅ **Loyalty**: Single Location, Single Budtender
- 100% of visits at Silverlake location
- 100% worked with Lizbeth Garcia
- **Insight**: Strong staff preference, but not enough to retain

### 4. ✅ **Payment Preference**: Cash Only
- 100% cash payments
- **Insight**: Privacy-conscious or no card on hand

### 5. ⚠️ **Terminal Consistency**: Always Cash Register
- Never used self-service or other terminals
- **Insight**: Prefers traditional checkout

---

## 📱 SMS COMMUNICATION HISTORY

**Status**: Checking SMS database...

(Would need to run query to see if this number appears in `messages` table)

---

## 🔍 MISSING DATA (Critical Gaps)

### ❌ HIGH PRIORITY MISSING

1. **Email Address**: 
   - Can't reach customer for win-back campaigns
   - Can't send receipts or offers
   - **Impact**: Lost marketing channel

2. **Purchase Details** (transaction_items):
   - Don't know WHAT products they bought
   - Can't recommend similar items
   - Can't identify favorite categories
   - **Impact**: No personalization possible

3. **Product Preferences**:
   - No THC/CBD preference data
   - No strain preference (Indica/Sativa/Hybrid)
   - No effects preferences (relaxing, energizing, etc.)
   - **Impact**: Can't tailor recommendations

4. **Marketing Source**:
   - How did they find us? (null in database)
   - **Impact**: Can't optimize acquisition channels

5. **Transaction Times**:
   - Only have dates, not times
   - Don't know if morning/afternoon/evening shopper
   - **Impact**: Can't time marketing messages

6. **Discount Usage**:
   - Field exists but all null
   - Don't know if price-sensitive
   - **Impact**: Don't know if deals would bring them back

7. **Loyalty Points Details**:
   - Have total (5.39 points) but no earn/spend history
   - Don't know if they understand the program
   - **Impact**: Can't nudge them to redeem

---

## 🎯 WHAT WE SHOULD KNOW (Derivative Data to Create)

### 1. **Purchase Frequency Score**
- **Current**: Can't calculate (need transaction_items)
- **Should Track**: Days between visits, visit momentum
- **Why**: Predict churn before it happens

### 2. **Product Diversity Score**
- **Current**: Unknown (no items data)
- **Should Track**: # of unique categories purchased
- **Why**: Cross-sell opportunities

### 3. **Price Sensitivity Index**
- **Current**: Declining spend trend suggests yes
- **Should Track**: Avg $/gram, response to discounts
- **Why**: Target with appropriate offers

### 4. **Staff Affinity Score**
- **Current**: 100% with Lizbeth
- **Should Track**: % visits with preferred staff
- **Why**: Leverage staff relationships for retention

### 5. **Engagement Score**
- **Current**: Can calculate: 3 visits in 4 days = high initial, then zero
- **Should Track**: Trend line (increasing/decreasing)
- **Why**: Early warning system for churn

### 6. **Win-Back Propensity**
- **Current**: 129 days = likely lost
- **Should Track**: Predicted LTV if reactivated
- **Why**: Prioritize high-value win-back targets

### 7. **Communication Responsiveness**
- **Current**: No SMS history to analyze
- **Should Track**: Reply rate, time to reply
- **Why**: Know which channel works

---

## 🚨 CRITICAL DATA GAPS (Blocking Insights)

### ❌ **Transaction Items Table Not Linked**

**Problem**: We have 3 transactions but NO visibility into what was purchased.

**What We're Missing**:
- Product SKUs purchased
- Quantities
- Unit prices
- Discounts applied
- Product categories
- THC/CBD levels of products bought
- Strain types purchased
- Effects preferences

**Query Needed**:
```sql
SELECT ti.*, p.*
FROM transaction_items ti
JOIN products p ON ti.product_sku = p.sku
WHERE ti.transaction_id IN (548869, 548915, 549196)
```

**Impact**: **CRITICAL** - Without this, we can't:
- Recommend products
- Understand preferences
- Calculate true customer value
- Personalize marketing
- Create look-alike audiences

---

## 🔮 RECOMMENDED DERIVATIVE TABLES/VIEWS

### 1. **Customer Visit Patterns** (Materialized View)
```sql
CREATE VIEW customer_visit_patterns AS
SELECT 
    customer_id,
    AVG(days_between_visits) as avg_days_between,
    STDDEV(days_between_visits) as visit_consistency,
    MAX(days_between_visits) as longest_gap,
    last_visit_date + (avg_days_between * INTERVAL '1 day') as predicted_next_visit,
    CASE 
        WHEN days_since_last_visit > (avg_days_between * 2) THEN 'At Risk'
        WHEN days_since_last_visit > avg_days_between THEN 'Overdue'
        ELSE 'On Track'
    END as visit_health_status
FROM (calculate from transactions)
GROUP BY customer_id
```

**Stephen's Data**:
- `avg_days_between`: 1.5 days (visits 1-3)
- `longest_gap`: 129 days (after visit 3)
- `predicted_next_visit`: June 5, 2025 (missed by 129 days!)
- `visit_health_status`: **At Risk**

### 2. **Product Affinity Matrix** (Table)
```sql
CREATE TABLE customer_product_affinity (
    customer_id TEXT,
    product_category TEXT,
    purchase_count INT,
    total_spent NUMERIC,
    avg_price_point NUMERIC,
    last_purchased DATE,
    repurchase_rate NUMERIC
)
```

**Stephen's Data**: **CANNOT CALCULATE** (no transaction_items)

### 3. **Customer Cohort Analysis** (View)
```sql
CREATE VIEW customer_cohorts AS
SELECT 
    DATE_TRUNC('month', date_joined) as cohort_month,
    customer_id,
    total_visits,
    lifetime_value,
    days_since_last_visit,
    CASE 
        WHEN days_since_last_visit <= 30 THEN 'Active'
        WHEN days_since_last_visit <= 60 THEN 'Lapsed'
        ELSE 'Churned'
    END as lifecycle_stage
FROM customers
```

**Stephen's Cohort**: June 2025
**Stephen's Stage**: **Churned** (129 days)

### 4. **Win-Back Priority Score** (Calculated Field)
```sql
ALTER TABLE customers ADD COLUMN win_back_score INT;

-- Formula:
win_back_score = (
    lifetime_value * 0.3 +
    total_visits * 0.2 +
    (1 / days_since_last_visit * 100) * 0.2 +
    avg_sale_value * 0.2 +
    loyalty_points * 0.1
)
```

**Stephen's Score**: 
- `lifetime_value`: $148.80 * 0.3 = 44.64
- `total_visits`: 3 * 0.2 = 0.6
- `recency`: (1/129 * 100) * 0.2 = 0.15
- `avg_sale`: $49.60 * 0.2 = 9.92
- `points`: 5.39 * 0.1 = 0.54
- **TOTAL**: **55.85** (LOW - probably not worth aggressive win-back)

### 5. **Staff Performance Impact** (Aggregation)
```sql
CREATE VIEW staff_retention_impact AS
SELECT 
    staff_name,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(customer_lifetime_value) as avg_customer_ltv,
    AVG(customer_return_rate) as avg_return_rate
FROM transactions
JOIN customers ON transactions.customer_id = customers.customer_id
GROUP BY staff_name
```

**Lizbeth Garcia's Impact on Stephen**:
- Worked with him 3/3 times
- Didn't retain him (0% return rate after June)
- LTV: $148.80

---

## 💡 ACTIONABLE INSIGHTS

### 🎯 For This Customer (Stephen Clare)

1. **Low Priority for Win-Back**: 
   - Low LTV ($148.80)
   - Declining spend pattern
   - 129 days since last visit
   - No email for outreach
   - **Action**: Move to "dormant" list, maybe one SMS attempt

2. **If SMS Outreach Attempted**:
   - **Message**: "Hey Stephen! It's been a while since we've seen you at MOTA Silverlake. Lizbeth misses you! 😊 We've got some great new products. $10 off your next visit? Reply YES"
   - **Timing**: Don't bother if no reply - move on
   - **Cost/Benefit**: Low expected ROI

3. **Learn from This Pattern**:
   - Joined June 1, churned by June 5
   - **Why?** Need to investigate:
     - Product quality issues?
     - Price too high?
     - Better competitor nearby?
     - Bad first experience?
   - **Action**: Survey other June 2025 cohort members

### 🎯 For Future Customers (Prevent This Pattern)

1. **Implement Email Capture**:
   - Make it mandatory or incentivize
   - Stephen has NO email = can't retarget
   
2. **Early Engagement Program**:
   - Trigger for "3 visits in first week" pattern
   - Send personalized thank you + loyalty explanation
   - Offer "4th visit bonus"
   
3. **Staff Training**:
   - Lizbeth built good rapport (3/3 visits)
   - But didn't close the relationship
   - Train on: loyalty program benefits, asking for email
   
4. **Product Tracking**:
   - **CRITICAL**: Link transaction_items properly
   - Can't improve what we can't measure
   
5. **Churn Prediction**:
   - Flag customers with declining spend
   - Auto-trigger win-back at 14 days (not 129!)

---

## 📊 SUMMARY: DATA QUALITY vs. INSIGHT CAPABILITY

### ✅ **What Supabase HAS:**
- Customer demographics (name, phone, zip, state)
- Purchase frequency (visits count)
- Financial metrics (LTV, avg sale)
- Transaction metadata (date, location, staff, payment)
- Auto-calculated fields (VIP status, churn risk)

### ❌ **What Supabase LACKS:**
- **Email addresses** (critical gap!)
- **Transaction line items** (products purchased)
- **Product preferences** (THC, CBD, strain, effects)
- **Marketing attribution** (how they found us)
- **Transaction times** (only dates, not hours)
- **Discount/promo tracking** (all null)
- **SMS engagement** (separate DB, not linked)

### 🔮 **What We SHOULD Derive:**
1. Purchase frequency score
2. Product diversity index
3. Price sensitivity score
4. Staff affinity score
5. Engagement trend line
6. Win-back propensity score
7. Next predicted visit date
8. Lifetime value projection (6mo, 1yr, 5yr)
9. Cohort retention rate
10. Cross-sell opportunity score

---

## 🎯 FINAL VERDICT

**Stephen Clare is a LOST customer with LOW recovery potential.**

**But the real issue isn't Stephen - it's that we can't even properly analyze WHY we lost him because:**

1. ❌ No transaction_items data → Don't know what he bought
2. ❌ No email → Can't reach him easily
3. ❌ No marketing source → Don't know why he came
4. ❌ No product preferences → Can't personalize offers
5. ❌ No engagement tracking → Don't know if he saw our messages

**The system has the STRUCTURE for good insights, but MISSING KEY DATA that would make those insights actionable.**

---

**Next Steps**: 
1. Fix transaction_items linkage (if it exists)
2. Implement mandatory email capture
3. Create derived metric tables (visit patterns, product affinity, win-back scores)
4. Build churn prevention automations
5. Link SMS database to CRM for unified customer view


