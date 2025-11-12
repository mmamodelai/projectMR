# IC Viewer v5.5 - Available Database Fields

## Overview
Complete list of all fields available in the Blaze database that we can potentially display in the viewer.

**Current Status**: Many fields available but not yet displayed. Easy to add!

---

## CUSTOMERS (`customers_blaze` table)

### ✅ Currently Displayed
- `first_name`, `last_name`
- `phone`
- `email`
- `text_opt_in` (SMS Opt-In)
- `email_opt_in`
- `total_visits` (Visits)
- `lifetime_value` (Lifetime $)
- `vip_status` (VIP Status)
- `last_visited` (Last Visit)
- `is_medical` (Medical status)

### 🆕 Available to Add

**Contact/Location**:
- `name` - Full name
- `street_address` - Street address
- `city` - City
- `state` - State
- `zip_code` - ZIP code

**Status/Metrics**:
- `member_status` - Active/Pending/Inactive (from Blaze)
- `loyalty_points` - Points balance (calculated field)
- `churn_risk` - Low/Medium/High risk assessment
- `days_since_last_visit` - Days since last visit (calculated)

**Dates**:
- `date_joined` - When they became a member
- `blaze_created` - When created in Blaze
- `blaze_modified` - Last modified in Blaze

---

## TRANSACTIONS (`transactions_blaze` table)

### ✅ Currently Displayed
- `date` - **NOW IN PST FORMAT** (11/09 3:45pm)
- `total_amount` - Total $ spent
- `payment_type` - Cash/Credit
- `blaze_status` - Completed/Refund/etc.
- `seller_id` - Budtender name
- **NEW**: `% MOTA` - Percentage of MOTA products

### 🆕 Available to Add

**Financial**:
- `total_tax` - Tax amount
- `discounts` - Total discounts applied
- `trans_type` - Sale/Refund/Adjustment

**Timing** (VERY USEFUL!):
- `start_time` - When customer checked in
- `end_time` - When transaction completed
- `completed_time` - Completion timestamp
- **Calculated**: Wait time (end_time - start_time)

**Location**:
- `shop_id` - Which store location
- `terminal_id` - Which POS terminal

**Metadata**:
- `blaze_created` - Created in Blaze system
- `blaze_modified` - Last modified

---

## ITEMS (`transaction_items_blaze` table)

### ✅ Currently Displayed
- `product_name` - Product name
- `brand` - Brand name
- `quantity` - Quantity purchased
- `total_price` - Total price

### 🆕 Available to Add

**Pricing Details**:
- `unit_price` - Price per unit
- `discount` - Discount per item
- `tax` - Tax per item

**Product Info**:
- `product_id` - Blaze product ID
- `product_sku` - SKU code
- `category` - Product category (Flower, Edibles, Vapes, etc.)

---

## PRODUCTS (`products_blaze` table)

### 🆕 Available to Join

**Potency** (VERY USEFUL for cannabis!):
- `thc_content` - THC % (e.g., "22.5%")
- `cbd_content` - CBD %
- `thca` - THCA %
- `cbda` - CBDA %
- `cbg` - CBG %

**Product Details**:
- `description` - Full product description
- `retail_price` - Retail price
- `weight_per_unit` - Weight (e.g., "3.5g", "1oz")
- `is_active` - Still available?
- `image_url` - Product image

**Metadata**:
- `category_id` - Category ID
- `vendor_id` - Vendor/supplier ID

---

## EMPLOYEES/BUDTENDERS (`budtenders` table)

### ✅ Currently Using
- `first_name`, `last_name` - Budtender name (via `seller_id`)

### 🆕 Available to Add
- `phone_number` - Budtender phone
- `dispensary_name` - Which location
- `points` - Budtender points/performance
- `email` - Budtender email

---

## Recommended Additions

### Priority 1: Transaction Timing ⏱️
**Add to Transactions**:
- `start_time` → "Check-in: 3:30pm"
- `end_time` → "Checkout: 3:45pm"
- **Wait Time** (calculated) → "15 mins"

**Why**: User asked about check-in times! This is available!

### Priority 2: Item Categories 📦
**Add to Items**:
- `category` → Flower, Edibles, Vapes, Concentrates

**Why**: See what types of products customers prefer

### Priority 3: Potency Data 🌿
**Add to Items** (join with Products):
- `thc_content`, `cbd_content`

**Why**: High-THC customers vs. balanced customers

### Priority 4: Discounts 💰
**Add to Transactions**:
- `discounts` → "$10.00"

**Why**: Track promotional effectiveness

### Priority 5: Transaction Type 🔄
**Add to Transactions**:
- `trans_type` → Sale/Refund/Adjustment

**Why**: Filter out refunds, track adjustments

---

## Calculated Fields We Can Add

### % Brand Columns
- ✅ **% MOTA** - ALREADY ADDED!
- `% Raw Garden` - Percentage Raw Garden products
- `% Pax` - Percentage Pax products
- `% Lost Farm` - Percentage Lost Farm products

### Transaction Metrics
- **Wait Time** - `end_time - start_time`
- **Items Count** - Count of items in transaction
- **Avg Item Price** - `total_amount / item_count`
- **Discount Rate** - `(discounts / total_amount) * 100`

### Customer Metrics
- **Days Since Join** - `TODAY - date_joined`
- **Avg Transaction Size** - `lifetime_value / total_visits`
- **Frequency Score** - Visits per month
- **Recency Score** - Days since last visit

### Product Mix
- **% Flower** - Percentage spent on flower
- **% Edibles** - Percentage spent on edibles
- **% Vapes** - Percentage spent on vapes
- **% Concentrates** - Percentage spent on concentrates

---

## Implementation Complexity

### Easy (5 min each):
- Add existing transaction fields (discounts, trans_type, shop_id)
- Add existing customer fields (date_joined, loyalty_points, churn_risk)
- Add existing item fields (category, discount, tax, sku)

### Medium (15 min each):
- Format timing fields (start_time, end_time)
- Calculate wait time
- Join products table to show potency

### Complex (30+ min each):
- Calculate % for multiple brands
- Calculate product mix percentages
- Build advanced analytics (cohorts, retention)

---

## Configuration Approach

All new fields should be:
1. **Optional** - User can hide via Display menu
2. **Saved** - Preferences persist in config file
3. **Fast** - No performance impact when hidden
4. **Clear** - Good column labels

---

## User Request: "What's Available?"

Based on the schema, here's what we CAN add:

### MUST HAVE (User will love):
1. ✅ **% MOTA** - Done!
2. **Transaction timing** - Check-in, checkout, wait time
3. **Item categories** - Flower/Edibles/Vapes
4. **Discounts** - See promotional impact

### NICE TO HAVE:
1. **THC/CBD content** - Product potency
2. **Transaction type** - Sale vs. Refund
3. **Multiple % brand columns** - Not just MOTA
4. **Shop/Terminal ID** - Track location

### ADVANCED (Future):
1. **Customer cohorts** - Group similar customers
2. **Retention analytics** - Churn prediction
3. **Product recommendations** - AI-based
4. **Revenue forecasting** - Predict next purchase

---

## Next Steps

1. ✅ **% MOTA added** - Working in v5.5
2. ⏱️ **Add transaction timing** - start_time, end_time, wait time
3. 📦 **Add item category** - Easy win
4. 💰 **Add discounts column** - Show promo effectiveness
5. 🔄 **Add trans_type** - Filter out refunds

**Your turn!** Which fields should we add next?

---

**Created**: November 9, 2025  
**Version**: 1.0  
**Status**: Field Inventory Complete  
**Source**: `blaze-api-sync/sql/01_create_tables.sql`

