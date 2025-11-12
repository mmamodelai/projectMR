# Supabase Database Schema - Complete Entity Relationship Diagram

**Project**: Conductor V4.1 - MoTa CRM System  
**Database**: Supabase Cloud  
**Last Updated**: January 2025  

---

## Schema Legend

| Symbol | Meaning |
|--------|---------|
| 🔑 | Primary Key |
| # | Identity (Auto-increment) |
| Ⓤ | Unique |
| ⚪ | Nullable |
| ⚫ | Non-Nullable |

---

## Database Tables Overview

The system contains **9 main tables** with complex relationships for customer data, transactions, products, and communication tracking.

---

## 1. `customers` Table

**Purpose**: Central customer information and profile data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `int4` | 🔑 ⚫ | Internal Supabase ID (surrogate key) |
| `member_id` | `text` | # Ⓤ ⚫ | **Business Key** - Unique customer identifier |
| `name` | `text` | ⚪ | Customer full name |
| `phone` | `text` | ⚪ | Phone number (E.164 format) |
| `email` | `text` | ⚪ | Email address |
| `loyalty_points` | `numeric` | ⚪ | Current loyalty points balance |
| `total_visits` | `int4` | ⚪ | Total number of visits |
| `total_sales` | `int4` | ⚪ | Total number of transactions |
| `total_refunds` | `int4` | ⚪ | Total number of refunds |
| `gross_sales` | `numeric` | ⚪ | Total sales amount ($) |
| `gross_refunds` | `numeric` | ⚪ | Total refunds amount ($) |
| `avg_sale_value` | `numeric` | ⚪ | Average transaction value ($) |
| `lifetime_value` | `numeric` | ⚪ | Customer lifetime value ($) |
| `customer_type` | `text` | ⚪ | Customer classification |
| `member_group` | `text` | ⚪ | Membership group |
| `marketing_source` | `text` | ⚪ | How customer was acquired |
| `state` | `text` | ⚪ | State/province |
| `zip_code` | `text` | ⚪ | Postal code |
| `date_joined` | `date` | ⚪ | First visit/registration date |
| `last_visited` | `date` | ⚪ | Most recent visit date |
| `vip_status` | `text` | ⚪ | VIP tier (New, Casual, Regular, VIP) |
| `churn_risk` | `text` | ⚪ | Churn risk assessment |
| `days_since_last_visit` | `int4` | ⚪ | Days since last visit |
| `created_at` | `timestamptz` | ⚪ | Record creation timestamp |
| `updated_at` | `timestamptz` | ⚪ | Last update timestamp |

**Key Relationships**:
- `member_id` → Foreign key in `transactions`, `customer_visit_patterns`, `customer_product_affinity`, `leads`

---

## 2. `transactions` Table

**Purpose**: Individual customer transaction records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `int4` | 🔑 ⚫ | Internal Supabase ID (surrogate key) |
| `transaction_id` | `text` | 🔑 ⚫ | **Business Key** - Unique transaction identifier |
| `customer_id` | `text` | ⚫ | **Foreign Key** → `customers.member_id` |
| `date` | `timestamptz` | ⚫ | Transaction date and time |
| `shop_location` | `text` | ⚪ | Store location name |
| `staff_name` | `text` | ⚪ | Budtender/staff member name |
| `terminal` | `text` | ⚪ | POS terminal identifier |
| `payment_type` | `text` | ⚪ | Payment method used |
| `total_amount` | `numeric` | ⚪ | Total transaction amount ($) |
| `total_tax` | `numeric` | ⚪ | Tax amount ($) |
| `discounts` | `numeric` | ⚪ | Discount amount ($) |
| `loyalty_points_earned` | `numeric` | ⚪ | Loyalty points earned |
| `loyalty_points_spent` | `numeric` | ⚪ | Loyalty points spent |
| `created_at` | `timestamptz` | ⚪ | Record creation timestamp |

**Key Relationships**:
- `customer_id` → References `customers.member_id`
- `transaction_id` → Foreign key in `transaction_items`

---

## 3. `transaction_items` Table

**Purpose**: Individual line items within each transaction

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `int4` | 🔑 ⚫ | Internal Supabase ID (surrogate key) |
| `transaction_id` | `text` | ⚫ | **Foreign Key** → `transactions.transaction_id` |
| `product_sku` | `text` | ⚪ | **Foreign Key** → `products.sku` |
| `product_name` | `text` | ⚪ | Product name at time of purchase |
| `brand` | `text` | ⚪ | Brand name at time of purchase |
| `category` | `text` | ⚪ | Product category |
| `strain` | `text` | ⚪ | Cannabis strain name |
| `flower_type` | `text` | ⚪ | Flower type classification |
| `quantity` | `int4` | ⚪ | Number of units purchased |
| `unit_price` | `numeric` | ⚪ | Price per unit ($) |
| `total_price` | `numeric` | ⚪ | Total price for this line item ($) |
| `thc_content` | `numeric` | ⚪ | THC content (mg or %) |
| `cbd_content` | `numeric` | ⚪ | CBD content (mg or %) |
| `created_at` | `timestamptz` | ⚪ | Record creation timestamp |

**Key Relationships**:
- `transaction_id` → References `transactions.transaction_id`
- `product_sku` → References `products.sku`

---

## 4. `products` Table

**Purpose**: Product catalog and inventory information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `int4` | 🔑 ⚫ | Internal Supabase ID (surrogate key) |
| `product_id` | `text` | 🔑 ⚫ | **Business Key** - Unique product identifier |
| `sku` | `text` | ⚪ | Stock Keeping Unit |
| `name` | `text` | ⚪ | Product name |
| `brand` | `text` | ⚪ | Brand/manufacturer name |
| `category` | `text` | ⚪ | Product category |
| `strain` | `text` | ⚪ | Cannabis strain name |
| `flower_type` | `text` | ⚪ | Flower type (Indica, Sativa, Hybrid) |
| `vendor` | `text` | ⚪ | Vendor/supplier name |
| `thc_content` | `numeric` | ⚪ | THC content (mg or %) |
| `cbd_content` | `numeric` | ⚪ | CBD content (mg or %) |
| `retail_price` | `numeric` | ⚪ | Current retail price ($) |
| `cost` | `numeric` | ⚪ | Cost price ($) |
| `is_active` | `bool` | ⚪ | Product availability status |
| `leafly_strain_type` | `text` | ⚪ | Leafly strain classification |
| `leafly_description` | `text` | ⚪ | Leafly product description |
| `leafly_rating` | `numeric` | ⚪ | Leafly user rating |
| `leafly_review_count` | `int4` | ⚪ | Number of Leafly reviews |
| `effects` | `_text` | ⚪ | Array of effects |
| `helps_with` | `_text` | ⚪ | Array of medical benefits |
| `negatives` | `_text` | ⚪ | Array of potential side effects |
| `flavors` | `_text` | ⚪ | Array of flavor profiles |
| `terpenes` | `_text` | ⚪ | Array of terpene profiles |
| `parent_strains` | `_text` | ⚪ | Array of parent strain names |
| `lineage` | `text` | ⚪ | Strain lineage information |
| `image_url` | `text` | ⚪ | Product image URL |
| `leafly_url` | `text` | ⚪ | Leafly product page URL |
| `leafly_data_updated` | `timestamptz` | ⚪ | Last Leafly data update |

**Key Relationships**:
- `sku` → Foreign key in `transaction_items.product_sku`

---

## 5. `staff` Table

**Purpose**: Staff member and budtender information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `int4` | 🔑 ⚫ | Internal Supabase ID (surrogate key) |
| `staff_name` | `text` | ⚪ | Staff member full name |
| `shop_location` | `text` | ⚪ | Primary store location |
| `total_transactions` | `int4` | ⚪ | Total transactions handled |
| `total_sales` | `numeric` | ⚪ | Total sales amount ($) |
| `avg_transaction_value` | `numeric` | ⚪ | Average transaction value ($) |
| `created_at` | `timestamptz` | ⚪ | Record creation timestamp |

---

## 6. `messages` Table

**Purpose**: SMS communication tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `int8` | 🔑 ⚫ | Internal Supabase ID (surrogate key) |
| `phone_number` | `text` | 🔑 ⚫ | **Business Key** - Phone number (E.164 format) |
| `content` | `text` | ⚫ | Message content |
| `timestamp` | `timestamptz` | ⚫ | Message timestamp |
| `modem_timestamp` | `timestamptz` | ⚪ | Modem timestamp |
| `status` | `text` | ⚫ | Message status (sent, queued, failed, unread, read) |
| `direction` | `text` | ⚫ | Message direction (inbound, outbound) |
| `modem_index` | `text` | ⚪ | Modem storage index |
| `message_hash` | `text` | ⚪ | Duplicate detection hash |
| `updated_at` | `timestamptz` | ⚪ | Last update timestamp |
| `retry_count` | `int4` | ⚪ | Number of send attempts |

---

## 7. `leads` Table

**Purpose**: Lead management and conversion tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `int8` | 🔑 ⚫ | Internal Supabase ID (surrogate key) |
| `phone_number` | `text` | 🔑 ⚫ | **Business Key** - Lead phone number |
| `lead_status` | `text` | ⚫ | Lead status |
| `conversation_stage` | `text` | ⚫ | Conversation stage |
| `last_message` | `text` | ⚪ | Last message content |
| `created_at` | `timestamptz` | ⚪ | Lead creation timestamp |
| `updated_at` | `timestamptz` | ⚪ | Last update timestamp |
| `customer_id` | `text` | ⚪ | **Foreign Key** → `customers.member_id` (when converted) |
| `conversion_probability` | `numeric` | ⚪ | Conversion probability score |

---

## 8. `customer_visit_patterns` Table

**Purpose**: Customer visit behavior analysis

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `customer_id` | `text` | 🔑 ⚫ | **Primary Key** → `customers.member_id` |
| `avg_days_between_visits` | `numeric` | ⚪ | Average days between visits |
| `visit_consistency_score` | `numeric` | ⚪ | Visit consistency rating |
| `predicted_next_visit` | `date` | ⚪ | Predicted next visit date |
| `last_visit_deviation_days` | `int4` | ⚪ | Deviation from average pattern |
| `longest_gap_days` | `int4` | ⚪ | Longest gap between visits |
| `shortest_gap_days` | `int4` | ⚪ | Shortest gap between visits |
| `total_visits` | `int4` | ⚪ | Total number of visits |
| `updated_at` | `timestamptz` | ⚪ | Last update timestamp |

---

## 9. `customer_product_affinity` Table

**Purpose**: Customer product preferences and purchase history

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `customer_id` | `text` | 🔑 ⚫ | **Primary Key** → `customers.member_id` |
| `product_sku` | `text` | 🔑 ⚫ | **Primary Key** → `products.sku` |
| `product_name` | `text` | ⚪ | Product name |
| `category` | `text` | ⚪ | Product category |
| `brand` | `text` | ⚪ | Brand name |
| `purchase_count` | `int4` | ⚪ | Number of times purchased |
| `total_spent` | `numeric` | ⚪ | Total amount spent on this product ($) |
| `last_purchased` | `date` | ⚪ | Last purchase date |
| `avg_price_paid` | `numeric` | ⚪ | Average price paid ($) |
| `repurchase_rate` | `numeric` | ⚪ | Repurchase probability |
| `created_at` | `timestamptz` | ⚪ | Record creation timestamp |
| `updated_at` | `timestamptz` | ⚪ | Last update timestamp |

---

## Key Relationships Summary

### Primary Foreign Key Links

1. **Customer Chain**:
   ```
   customers.member_id → transactions.customer_id
   customers.member_id → customer_visit_patterns.customer_id
   customers.member_id → customer_product_affinity.customer_id
   customers.member_id → leads.customer_id (when converted)
   ```

2. **Transaction Chain**:
   ```
   transactions.transaction_id → transaction_items.transaction_id
   ```

3. **Product Chain**:
   ```
   products.sku → transaction_items.product_sku
   products.sku → customer_product_affinity.product_sku
   ```

4. **Communication Chain**:
   ```
   customers.phone → messages.phone_number
   customers.phone → leads.phone_number
   ```

### Critical Data Duplication Notes

When duplicating customer data (like AARON AMADO → Keanu Klare):

1. **Generate new `member_id`** for the new customer
2. **Update all foreign key references** in related tables
3. **Generate new transaction IDs** for duplicated transactions
4. **Maintain referential integrity** across all tables
5. **Update timestamps** appropriately for new records

---

## Database Statistics

| Table | Estimated Records | Purpose |
|-------|------------------|---------|
| `customers` | ~10,000 | Customer profiles |
| `transactions` | ~200,000 | Transaction records |
| `transaction_items` | ~500,000 | Line items |
| `products` | ~5,000 | Product catalog |
| `staff` | ~100 | Staff members |
| `messages` | ~50,000 | SMS messages |
| `leads` | ~1,000 | Lead records |
| `customer_visit_patterns` | ~10,000 | Visit analytics |
| `customer_product_affinity` | ~50,000 | Purchase preferences |

---

## Integration Points

- **SMS System**: Uses `messages` table
- **CRM Viewers**: Uses all customer-related tables
- **MotaBot AI**: Queries customer data for personalized responses
- **Analytics**: Uses `customer_visit_patterns` and `customer_product_affinity`

---

**Note**: This schema supports full customer data duplication while maintaining referential integrity across all related tables.


