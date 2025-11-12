# Conductor SMS System - Database Schema & Insights Guide

**Last Updated:** January 2025  
**Database:** Supabase (smsconductor project)  
**Purpose:** Complete guide to database structure and actionable insights

---

## 📊 Database Overview

### **Schema Summary**
- **12 Core Tables**: Customers, transactions, products, staff, messages, campaigns, leads, and analytics tables
- **Key Relationships**: Customer-centric design with transaction history, product affinity, visit patterns, and marketing campaigns
- **Data Sources**: Historical CSV imports + Blaze API integration (in progress)

### **Current Data Volume**
- **10,047 customers** with calculated metrics
- **186,394 transactions** (January 2025 - October 2025)
- **114,136 transaction items** (detailed line items)
- **39,555 products** with Leafly integration
- **~50 staff members**
- **Messages & campaigns** tracked in separate tables

---

## 🗄️ Complete Table Structure

### **1. customers** - Central Customer Table
**Primary Key:** `id` (auto-increment)  
**Business Key:** `member_id` (text, unique)

**Core Fields:**
- Identity: `member_id`, `name`, `phone`, `email`
- Address: `street_address`, `city`, `state`, `zip_code`
- Loyalty: `loyalty_points`, `member_group`, `marketing_source`
- Calculated Metrics: `total_visits`, `total_sales`, `lifetime_value`, `avg_sale_value`
- Segmentation: `customer_type`, `vip_status`, `churn_risk`
- Timestamps: `date_joined`, `last_visited`, `days_since_last_visit`

**Relationships:**
- → `transactions` (one-to-many)
- → `customer_visit_patterns` (one-to-one)
- → `customer_product_affinity` (one-to-many)
- → `campaign_messages` (one-to-many)
- → `scheduled_messages` (one-to-many)
- → `leads` (one-to-one)

**Key Insights Available:**
- Customer lifetime value analysis
- Churn risk prediction
- VIP customer identification
- Visit frequency patterns
- Geographic distribution
- Marketing source effectiveness

---

### **2. transactions** - Sales Transactions
**Primary Key:** `id` (auto-increment)  
**Business Key:** `transaction_id` (text, unique)

**Core Fields:**
- Identity: `transaction_id`, `customer_id` (links to `customers.member_id`)
- Financial: `total_amount`, `total_tax`, `discounts`, `loyalty_points_earned`, `loyalty_points_spent`
- Context: `date`, `shop_location`, `staff_name`, `terminal`, `payment_type`
- Status: `status` (implied from schema)

**Relationships:**
- ← `customers` (many-to-one)
- → `transaction_items` (one-to-many)
- ← `staff` (many-to-one via `staff_name`)

**Key Insights Available:**
- Daily/weekly/monthly revenue trends
- Average transaction value
- Payment method distribution
- Staff performance metrics
- Location performance comparison
- Seasonal patterns
- Customer transaction frequency

---

### **3. transaction_items** - Line Item Details
**Primary Key:** `id` (auto-increment)  
**Composite Key:** `transaction_id` + `product_sku`

**Core Fields:**
- Identity: `transaction_id`, `product_sku`, `product_name`
- Product Details: `brand`, `category`, `strain`, `flower_type`
- Financial: `quantity`, `unit_price`, `total_price`
- Potency: `thc_content`, `cbd_content`

**Relationships:**
- ← `transactions` (many-to-one)
- → `products` (many-to-one via `product_sku`)

**Key Insights Available:**
- Product performance (best sellers)
- Brand performance
- Category trends
- Price points analysis
- THC/CBD content preferences
- Bundling patterns (what's bought together)
- Product affinity (cross-sell opportunities)

---

### **4. products** - Product Catalog
**Primary Key:** `id` (auto-increment)  
**Business Key:** `sku` (text, unique)

**Core Fields:**
- Identity: `sku`, `product_id`, `name`, `brand`, `category`, `vendor`
- Cannabis-Specific: `strain`, `flower_type`, `thc_content`, `cbd_content`
- Leafly Integration: `leafly_strain_type`, `leafly_description`, `leafly_rating`, `leafly_review_count`, `leafly_url`
- Cannabis Details: `effects`, `helps_with`, `negatives`, `flavors`, `terpenes`, `parent_strains`, `lineage`
- Financial: `retail_price`, `cost`
- Status: `is_active`

**Relationships:**
- → `transaction_items` (one-to-many via `product_sku`)
- → `customer_product_affinity` (one-to-many via `product_sku`)

**Key Insights Available:**
- Product catalog completeness
- Price point distribution
- Strain popularity
- Leafly rating correlation with sales
- THC/CBD content preferences
- Category performance
- Brand performance
- Product lifecycle (new vs. discontinued)

---

### **5. customers → customer_visit_patterns** - Visit Analytics
**Primary Key:** `customer_id` (text, references `customers.member_id`)

**Core Fields:**
- Metrics: `avg_days_between_visits`, `visit_consistency_score`, `predicted_next_visit`
- Analysis: `last_visit_deviation_from_avg`, `longest_gap_days`, `shortest_gap_days`
- Counts: `total_visits`
- Timestamp: `updated_at`

**Key Insights Available:**
- Customer visit frequency patterns
- Visit consistency scoring
- Predicted next visit dates
- Churn prediction (based on gap patterns)
- Visit regularity analysis
- Customer lifecycle stage identification

---

### **6. customers → customer_product_affinity** - Product Preferences
**Composite Primary Key:** `customer_id` + `product_sku`

**Core Fields:**
- Product: `product_sku`, `product_name`, `category`, `brand`
- Metrics: `purchase_count`, `total_spent`, `avg_price_paid`, `repurchase_rate`
- Timestamps: `last_purchased`

**Key Insights Available:**
- Customer favorite products (top 3-5 per customer)
- Product recommendation engine data
- Cross-sell opportunities
- Brand loyalty patterns
- Category preferences
- Price sensitivity analysis
- Repurchase behavior

---

### **7. staff** - Staff Performance
**Primary Key:** `id` (auto-increment)

**Core Fields:**
- Identity: `staff_name`, `shop_location`
- Metrics: `total_transactions`, `total_sales`, `avg_transaction_value`
- Timestamp: `created_at`

**Relationships:**
- → `transactions` (one-to-many via `staff_name`)

**Key Insights Available:**
- Staff performance rankings
- Sales per staff member
- Average transaction value by staff
- Location performance (if staff are location-specific)
- Staff productivity metrics

---

### **8. budtenders** - Budtender Management
**Primary Key:** `id` (auto-increment)

**Core Fields:**
- Identity: `first_name`, `last_name`, `phone`, `email`, `dispensary_name`
- Rewards: `points` (loyalty/rewards system)
- Timestamps: `created_at`, `updated_at`

**Key Insights Available:**
- Budtender contact information
- Points/rewards tracking
- Dispensary assignment

---

### **9. messages** - SMS Message Log
**Primary Key:** `id` (auto-increment)

**Core Fields:**
- Identity: `phone_number`
- Content: `content`, `message_hash` (deduplication)
- Timing: `timestamp`, `modem_timestamp`
- Status: `status`, `direction` (inbound/outbound), `modem_index`
- Retry: `retry_count`

**Relationships:**
- → `scheduled_messages` (one-to-many via `message_id`)

**Key Insights Available:**
- Message delivery rates
- Response rates
- Message volume trends
- Failed message analysis
- Duplicate detection

---

### **10. scheduled_messages** - Campaign Messages
**Primary Key:** `id` (auto-increment)

**Core Fields:**
- Customer: `customer_id`, `phone_number`, `customer_segment`
- Content: `message_content`, `original_message`, `message_id` (links to `messages`)
- AI Generation: `generated_by`, `generation_prompt`, `generation_model`, `generation_cost`
- Strategy: `strategy_type`, `reasoning`, `confidence_score`
- Context: `days_since_visit`, `favorite_budtender`, `favorite_product`
- Scheduling: `scheduled_send_time`, `actual_send_time`
- Status: `status`, `delivery_status`, `error_message`
- Campaign: `campaign_name`, `campaign_batch_id`
- Review: `reviewed_by`, `reviewed_at`, `human_override`

**Relationships:**
- ← `customers` (many-to-one)
- → `messages` (one-to-one via `message_id`)

**Key Insights Available:**
- Campaign performance metrics
- AI generation costs per campaign
- Strategy effectiveness (which strategies work best)
- Message delivery success rates
- Response rates by strategy type
- Campaign ROI analysis
- Human override rates

---

### **11. campaign_messages** - Bulk Campaign Analytics
**Primary Key:** `id` (auto-increment)

**Core Fields:**
- Customer: `customer_id`, `customer_name`, `phone_number`, `customer_segment`
- Content: `message_content`, `strategy_type`, `confidence`, `reasoning`
- Context: `days_since_visit`, `favorite_budtender`, `favorite_product`, `total_visits`, `lifetime_value`
- Scheduling: `preferred_day`, `preferred_time`, `scheduling_reasoning`
- Generation: `generated_by`, `generation_cost`, `generated_at`
- Status: `status`, `campaign_name`, `campaign_batch_id`, `priority`
- Export: `exported_at`, `exported_to`, `conductor_message_id`
- Review: `reviewed_by`, `reviewed_at`, `feedback_notes`

**Relationships:**
- ← `customers` (many-to-one)

**Key Insights Available:**
- Campaign batch performance
- Strategy effectiveness comparison
- Customer segment targeting results
- Scheduling optimization (best days/times)
- Generation cost analysis
- Export and delivery tracking

---

### **12. leads** - Lead Management
**Primary Key:** `id` (auto-increment)

**Core Fields:**
- Identity: `phone_number`, `customer_id` (nullable, links when converted)
- Status: `load_status`, `conversation_stage`
- Content: `last_message`
- Metrics: `conversion_probability`
- Timestamps: `created_at`, `updated_at`

**Relationships:**
- → `customers` (one-to-one when converted)

**Key Insights Available:**
- Lead conversion rates
- Conversation stage progression
- Lead quality scoring
- Conversion funnel analysis

---

## 🎯 Actionable Insights by Category

### **1. Customer Insights**

#### **Customer Segmentation**
```sql
-- VIP Customers (High value, frequent visitors)
SELECT name, lifetime_value, total_visits, last_visited
FROM customers
WHERE vip_status = 'VIP'
ORDER BY lifetime_value DESC;

-- High Churn Risk Customers
SELECT name, days_since_last_visit, lifetime_value, churn_risk
FROM customers
WHERE churn_risk = 'High'
ORDER BY lifetime_value DESC;

-- New Customers (Last 30 days)
SELECT name, date_joined, total_visits, lifetime_value
FROM customers
WHERE date_joined >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date_joined DESC;
```

#### **Customer Lifetime Value Analysis**
```sql
-- LTV Distribution
SELECT 
  CASE 
    WHEN lifetime_value < 100 THEN '$0-$100'
    WHEN lifetime_value < 500 THEN '$100-$500'
    WHEN lifetime_value < 1000 THEN '$500-$1,000'
    WHEN lifetime_value < 2500 THEN '$1,000-$2,500'
    ELSE '$2,500+'
  END as ltv_segment,
  COUNT(*) as customer_count,
  AVG(lifetime_value) as avg_ltv,
  SUM(lifetime_value) as total_ltv
FROM customers
GROUP BY ltv_segment
ORDER BY MIN(lifetime_value);
```

#### **Customer Purchase Patterns**
```sql
-- Customers with favorite products
SELECT 
  c.name,
  cpa.product_name,
  cpa.purchase_count,
  cpa.total_spent,
  cpa.last_purchased
FROM customers c
JOIN customer_product_affinity cpa ON c.member_id = cpa.customer_id
WHERE cpa.purchase_count >= 2
ORDER BY cpa.purchase_count DESC, cpa.total_spent DESC;
```

---

### **2. Sales & Revenue Insights**

#### **Revenue Trends**
```sql
-- Monthly Revenue Trend
SELECT 
  DATE_TRUNC('month', date) as month,
  COUNT(*) as transactions,
  SUM(total_amount) as revenue,
  AVG(total_amount) as avg_transaction,
  SUM(total_tax) as total_tax
FROM transactions
WHERE total_amount > 0
GROUP BY DATE_TRUNC('month', date)
ORDER BY month DESC;

-- Daily Revenue (Last 30 Days)
SELECT 
  date::date as sale_date,
  COUNT(*) as transactions,
  SUM(total_amount) as revenue,
  AVG(total_amount) as avg_transaction
FROM transactions
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
  AND total_amount > 0
GROUP BY date::date
ORDER BY sale_date DESC;
```

#### **Payment Method Analysis**
```sql
-- Payment Method Distribution
SELECT 
  payment_type,
  COUNT(*) as transaction_count,
  SUM(total_amount) as total_revenue,
  AVG(total_amount) as avg_transaction,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM transactions
WHERE payment_type IS NOT NULL
GROUP BY payment_type
ORDER BY total_revenue DESC;
```

#### **Average Transaction Value**
```sql
-- AOV by Customer Segment
SELECT 
  CASE 
    WHEN c.lifetime_value < 100 THEN 'Low Value'
    WHEN c.lifetime_value < 500 THEN 'Medium Value'
    WHEN c.lifetime_value < 2500 THEN 'High Value'
    ELSE 'VIP'
  END as segment,
  COUNT(DISTINCT t.customer_id) as customers,
  COUNT(*) as transactions,
  AVG(t.total_amount) as avg_transaction_value,
  SUM(t.total_amount) as total_revenue
FROM transactions t
JOIN customers c ON t.customer_id = c.member_id
WHERE t.total_amount > 0
GROUP BY segment
ORDER BY avg_transaction_value DESC;
```

---

### **3. Product Performance Insights**

#### **Top Products**
```sql
-- Best Selling Products (By Revenue)
SELECT 
  ti.product_name,
  ti.brand,
  ti.category,
  COUNT(*) as times_sold,
  SUM(ti.quantity) as total_units_sold,
  SUM(ti.total_price) as total_revenue,
  AVG(ti.unit_price) as avg_price
FROM transaction_items ti
GROUP BY ti.product_name, ti.brand, ti.category
ORDER BY total_revenue DESC
LIMIT 20;

-- Best Selling Products (By Volume)
SELECT 
  ti.product_name,
  ti.brand,
  SUM(ti.quantity) as total_units_sold,
  COUNT(*) as transactions,
  SUM(ti.total_price) as total_revenue
FROM transaction_items ti
GROUP BY ti.product_name, ti.brand
ORDER BY total_units_sold DESC
LIMIT 20;
```

#### **Category Performance**
```sql
-- Revenue by Category
SELECT 
  category,
  COUNT(DISTINCT product_sku) as unique_products,
  COUNT(*) as transactions,
  SUM(total_price) as total_revenue,
  AVG(unit_price) as avg_price
FROM transaction_items
WHERE category IS NOT NULL
GROUP BY category
ORDER BY total_revenue DESC;

-- Brand Performance
SELECT 
  brand,
  COUNT(DISTINCT product_sku) as unique_products,
  COUNT(*) as transactions,
  SUM(total_price) as total_revenue
FROM transaction_items
WHERE brand IS NOT NULL
GROUP BY brand
ORDER BY total_revenue DESC
LIMIT 20;
```

#### **Cannabis-Specific Insights**
```sql
-- THC Content Preferences
SELECT 
  CASE 
    WHEN ti.thc_content < 15 THEN '< 15%'
    WHEN ti.thc_content < 20 THEN '15-20%'
    WHEN ti.thc_content < 25 THEN '20-25%'
    WHEN ti.thc_content < 30 THEN '25-30%'
    ELSE '30%+'
  END as thc_range,
  COUNT(*) as transactions,
  SUM(ti.total_price) as revenue
FROM transaction_items ti
WHERE ti.thc_content IS NOT NULL AND ti.thc_content > 0
GROUP BY thc_range
ORDER BY MIN(ti.thc_content);

-- Strain Popularity
SELECT 
  strain,
  COUNT(*) as times_sold,
  SUM(total_price) as total_revenue
FROM transaction_items
WHERE strain IS NOT NULL
GROUP BY strain
ORDER BY times_sold DESC
LIMIT 20;
```

---

### **4. Staff Performance Insights**

#### **Staff Sales Performance**
```sql
-- Top Performing Staff
SELECT 
  staff_name,
  shop_location,
  COUNT(*) as transactions,
  SUM(total_amount) as total_sales,
  AVG(total_amount) as avg_transaction,
  COUNT(DISTINCT customer_id) as unique_customers
FROM transactions
WHERE staff_name IS NOT NULL
GROUP BY staff_name, shop_location
ORDER BY total_sales DESC;

-- Staff Performance by Month
SELECT 
  staff_name,
  DATE_TRUNC('month', date) as month,
  COUNT(*) as transactions,
  SUM(total_amount) as total_sales,
  AVG(total_amount) as avg_transaction
FROM transactions
WHERE staff_name IS NOT NULL
GROUP BY staff_name, DATE_TRUNC('month', date)
ORDER BY month DESC, total_sales DESC;
```

---

### **5. Campaign & Marketing Insights**

#### **Campaign Performance**
```sql
-- Campaign Effectiveness
SELECT 
  campaign_name,
  COUNT(*) as messages_sent,
  COUNT(DISTINCT customer_id) as unique_customers,
  SUM(CASE WHEN delivery_status = 'delivered' THEN 1 ELSE 0 END) as delivered,
  SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
  SUM(generation_cost) as total_cost,
  AVG(generation_cost) as avg_cost_per_message
FROM scheduled_messages
WHERE campaign_name IS NOT NULL
GROUP BY campaign_name
ORDER BY messages_sent DESC;

-- Strategy Effectiveness
SELECT 
  strategy_type,
  COUNT(*) as messages,
  AVG(confidence_score::numeric) as avg_confidence,
  SUM(CASE WHEN delivery_status = 'delivered' THEN 1 ELSE 0 END) as delivered,
  SUM(generation_cost) as total_cost
FROM scheduled_messages
WHERE strategy_type IS NOT NULL
GROUP BY strategy_type
ORDER BY messages DESC;
```

#### **Customer Segmentation for Campaigns**
```sql
-- Customers by Segment
SELECT 
  customer_segment,
  COUNT(*) as customer_count,
  AVG(lifetime_value) as avg_ltv,
  AVG(total_visits) as avg_visits,
  AVG(days_since_last_visit::numeric) as avg_days_since_visit
FROM customers
WHERE customer_segment IS NOT NULL
GROUP BY customer_segment
ORDER BY avg_ltv DESC;
```

---

### **6. Visit Pattern Insights**

#### **Visit Frequency Analysis**
```sql
-- Visit Consistency Analysis
SELECT 
  CASE 
    WHEN visit_consistency_score < 0.3 THEN 'Low Consistency'
    WHEN visit_consistency_score < 0.6 THEN 'Medium Consistency'
    ELSE 'High Consistency'
  END as consistency_level,
  COUNT(*) as customers,
  AVG(avg_days_between_visits) as avg_days_between,
  AVG(total_visits) as avg_total_visits
FROM customer_visit_patterns
GROUP BY consistency_level
ORDER BY consistency_level;

-- Predicted Next Visits
SELECT 
  c.name,
  c.phone,
  cvp.predicted_next_visit,
  cvp.avg_days_between_visits,
  c.days_since_last_visit,
  c.lifetime_value
FROM customers c
JOIN customer_visit_patterns cvp ON c.member_id = cvp.customer_id
WHERE cvp.predicted_next_visit BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
ORDER BY cvp.predicted_next_visit;
```

---

### **7. Cross-Sell & Product Affinity Insights**

#### **Product Bundling**
```sql
-- What Products Are Bought Together
SELECT 
  ti1.product_name as product_1,
  ti2.product_name as product_2,
  COUNT(*) as times_bought_together
FROM transaction_items ti1
JOIN transaction_items ti2 ON ti1.transaction_id = ti2.transaction_id
WHERE ti1.product_sku < ti2.product_sku
GROUP BY ti1.product_name, ti2.product_name
ORDER BY times_bought_together DESC
LIMIT 20;
```

#### **Category Cross-Sell Opportunities**
```sql
-- Category Combinations
SELECT 
  ti1.category as category_1,
  ti2.category as category_2,
  COUNT(*) as times_bought_together
FROM transaction_items ti1
JOIN transaction_items ti2 ON ti1.transaction_id = ti2.transaction_id
WHERE ti1.category < ti2.category AND ti1.category IS NOT NULL AND ti2.category IS NOT NULL
GROUP BY ti1.category, ti2.category
ORDER BY times_bought_together DESC
LIMIT 20;
```

---

### **8. Geographic & Location Insights**

#### **Customer Distribution**
```sql
-- Customers by State
SELECT 
  state,
  COUNT(*) as customer_count,
  AVG(lifetime_value) as avg_ltv,
  SUM(lifetime_value) as total_ltv
FROM customers
WHERE state IS NOT NULL
GROUP BY state
ORDER BY customer_count DESC;

-- Customers by Zip Code
SELECT 
  zip_code,
  COUNT(*) as customer_count,
  AVG(lifetime_value) as avg_ltv
FROM customers
WHERE zip_code IS NOT NULL
GROUP BY zip_code
ORDER BY customer_count DESC
LIMIT 20;
```

#### **Shop Location Performance**
```sql
-- Revenue by Location
SELECT 
  shop_location,
  COUNT(*) as transactions,
  SUM(total_amount) as total_revenue,
  AVG(total_amount) as avg_transaction,
  COUNT(DISTINCT customer_id) as unique_customers
FROM transactions
WHERE shop_location IS NOT NULL
GROUP BY shop_location
ORDER BY total_revenue DESC;
```

---

### **9. Real-Time Metrics & Monitoring**

#### **Today's Performance**
```sql
-- Today's Sales
SELECT 
  COUNT(*) as transactions_today,
  SUM(total_amount) as revenue_today,
  AVG(total_amount) as avg_transaction_today,
  COUNT(DISTINCT customer_id) as unique_customers_today
FROM transactions
WHERE date::date = CURRENT_DATE;

-- Customers Who Visited Today
SELECT 
  COUNT(DISTINCT customer_id) as customers_today,
  SUM(total_amount) as revenue
FROM transactions
WHERE date::date = CURRENT_DATE;
```

#### **Customer Activity (Last 7 Days)**
```sql
-- Active Customers This Week
SELECT 
  COUNT(DISTINCT customer_id) as active_customers,
  COUNT(*) as transactions,
  SUM(total_amount) as revenue
FROM transactions
WHERE date >= CURRENT_DATE - INTERVAL '7 days';
```

---

### **10. Predictive Analytics**

#### **Churn Prediction**
```sql
-- High Churn Risk Customers
SELECT 
  name,
  phone,
  days_since_last_visit,
  lifetime_value,
  total_visits,
  churn_risk,
  CASE 
    WHEN days_since_last_visit > 90 THEN 'Critical Risk'
    WHEN days_since_last_visit > 60 THEN 'High Risk'
    WHEN days_since_last_visit > 30 THEN 'Medium Risk'
    ELSE 'Low Risk'
  END as risk_level
FROM customers
WHERE churn_risk = 'High' OR days_since_last_visit > 60
ORDER BY days_since_last_visit DESC, lifetime_value DESC;
```

#### **Next Purchase Prediction**
```sql
-- Customers Likely to Visit Soon
SELECT 
  c.name,
  c.phone,
  cvp.predicted_next_visit,
  cvp.avg_days_between_visits,
  c.days_since_last_visit,
  c.lifetime_value,
  cpa.product_name as favorite_product
FROM customers c
JOIN customer_visit_patterns cvp ON c.member_id = cvp.customer_id
LEFT JOIN customer_product_affinity cpa ON c.member_id = cpa.customer_id
WHERE cvp.predicted_next_visit BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '14 days'
  AND cpa.purchase_count = (SELECT MAX(purchase_count) FROM customer_product_affinity WHERE customer_id = c.member_id)
ORDER BY cvp.predicted_next_visit;
```

---

## 🔄 Integration with Blaze API

### **Current State**
- **Historical Data**: CSV imports (January 2025 - October 2025)
- **Migration Plan**: Gradual migration to Blaze API for real-time data
- **Status**: Sandbox testing complete, production migration in progress

### **Data Mapping (Blaze → Supabase)**
See `docs/BLAZEAPI/data_mapping_audit.md` for complete mapping details.

**Key Mappings:**
- `Member.id` → `customers.member_id`
- `Transaction.id` → `transactions.transaction_id`
- `OrderItem` → `transaction_items`
- `Product.id` → `products.product_id`

### **Benefits of Blaze Integration**
- ✅ Real-time customer data (phone, email, address)
- ✅ Accurate `last_visited` dates
- ✅ Live product pricing
- ✅ Current transaction status
- ✅ Accurate calculated fields (LTV, visit counts)
- ✅ Better segmentation (VIP, churn risk)

---

## 📈 Recommended Dashboards & Reports

### **Executive Dashboard**
1. **Revenue Metrics**
   - Today's revenue vs. yesterday
   - Monthly revenue trend
   - Average transaction value
   - Revenue by location

2. **Customer Metrics**
   - Total customers
   - New customers this month
   - VIP customers count
   - Active customers (last 30 days)

3. **Product Metrics**
   - Top 10 products by revenue
   - Category performance
   - Brand performance

### **Operations Dashboard**
1. **Staff Performance**
   - Sales by staff member
   - Average transaction by staff
   - Transactions per staff member

2. **Campaign Performance**
   - Messages sent vs. delivered
   - Campaign costs
   - Strategy effectiveness

3. **Inventory Insights**
   - Product popularity
   - Slow-moving products
   - Category trends

### **Marketing Dashboard**
1. **Campaign Analytics**
   - Campaign ROI
   - Message delivery rates
   - Customer response rates
   - Strategy performance

2. **Customer Segmentation**
   - Segment distribution
   - LTV by segment
   - Churn risk distribution

3. **Targeting Insights**
   - Best days/times to contact
   - Preferred products by segment
   - Visit prediction accuracy

---

## 🚀 Quick Start Queries

### **Most Common Queries**

```sql
-- 1. Find Customer by Phone
SELECT * FROM customers WHERE phone = '+16199773020';

-- 2. Customer Purchase History
SELECT t.*, ti.*
FROM customers c
JOIN transactions t ON c.member_id = t.customer_id
JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
WHERE c.phone = '+16199773020'
ORDER BY t.date DESC;

-- 3. Top Customers
SELECT name, lifetime_value, total_visits, last_visited
FROM customers
ORDER BY lifetime_value DESC
LIMIT 10;

-- 4. Revenue This Month
SELECT SUM(total_amount) as revenue
FROM transactions
WHERE DATE_TRUNC('month', date) = DATE_TRUNC('month', CURRENT_DATE);

-- 5. Product Recommendations for Customer
SELECT product_name, purchase_count, total_spent, last_purchased
FROM customer_product_affinity
WHERE customer_id = 'MEMBER_ID'
ORDER BY purchase_count DESC, total_spent DESC
LIMIT 5;
```

---

## 📝 Notes & Limitations

### **Data Quality Issues**
- ⚠️ **Transaction Items**: Some transactions may have incomplete line items (documented in `mota-crm/docs/README_DB.md`)
- ⚠️ **Calculated Fields**: May be stale until Blaze API migration completes
- ⚠️ **Staff Table**: Currently empty (staff data comes from transactions)

### **Performance Considerations**
- Use `customer_sms_context` view for n8n integrations (optimized single query)
- `customer_product_affinity` table is pre-calculated for fast product recommendations
- `customer_visit_patterns` table provides pre-computed visit analytics

### **Future Enhancements**
- Real-time data sync via Blaze API
- Webhook integration for instant updates
- Advanced predictive analytics
- Automated campaign optimization

---

## 📚 Related Documentation

- **Database Schema**: `docs/BLAZEAPI/data_mapping_audit.md`
- **Blaze API Integration**: `docs/BLAZEAPI/README.md`
- **Migration Strategy**: `docs/BLAZEAPI/migration_strategy.md`
- **Database Viewers**: `DATABASE_VIEWERS_GUIDE.md`
- **CRM Documentation**: `mota-crm/docs/README_DB.md`

---

**Last Updated:** January 2025  
**Maintained By:** Conductor SMS System Team



