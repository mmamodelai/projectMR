# Blaze → Database Mapping Audit

Purpose: identify what we can pull live from Blaze API and how it fits into our existing schema. Each field is tagged:
- R = Replace (supersede existing report-derived value)
- A = Augment (new column or nullable addition)
- D = Derived (compute from API data in-app/DB)

## 1) Members → `customers`
- Identity: `Member.id` → `customers.member_id` [R]
- Name: `firstName`, `lastName` → `customers.name` (concat) [R]
- Contact: `primaryPhone` → `customers.phone` [R]; `email` → `customers.email` [R]
- Status/flags: `status` → `customers.customer_type` or new `member_status` [A]; `medical` → new `is_medical` [A]; `textOptIn`, `emailOptIn` → new consent flags [A]
- Address: `address` → `street_address`, `city`, `state`, `zip_code` [R]
- Activity: `lastVisitDate` → `customers.last_visited` [R]; D: `days_since_last_visit` [D]
- Loyalty: via loyalty endpoints or `pointSpent` signals → `loyalty_points` [R/A]
- Audit: `created`, `modified` → `created_at`, `updated_at` [A]
- Notes/metadata: `notes[]`, `metadata[]` → new related table or JSONB column [A]

Key API: `/api/v1/partner/members` (supports startDate/endDate epoch ms, skip/limit), `/api/v1/partner/members/{id}`, searches by phone/email.

## 2) Transactions → `transactions`
- Identity: `Transaction.id` → `transactions.transaction_id` [R]
- Linking: `memberId` → `transactions.customer_id` [R]; seller/terminal fields → `staff_name`/`terminal` [A]
- Timestamps: `startTime`, `endTime`, `completedTime` → `date` [R] (+ store raw fields) [A]
- Status: `status` (Queued/Completed/Refund/etc.) → `status` [R]
- Financials (from `cart`): `subTotal`, `total`, `tax`, `feeTotal`, `balanceDue` → `total_amount`, `total_tax`, etc. [R]
- Payment: `paymentOption` → `payment_type` [R]
- Location: `shopId` → `shop_location` [A]

Key API: `/api/v1/partner/transactions` (startDate/endDate strings + skip/limit), `/api/v1/partner/transactions/{id}`.

## 3) Transaction Items → `transaction_items`
- Links: `OrderItem.parentId` or transaction → `transaction_items.transaction_id` [R]
- Product: `productId` → `transaction_items.product_id` [R]; `productSku` → `product_sku` [R]
- Qty/Pricing: `quantity`, `unitPrice`, `finalPrice`, `discount`, `calcTax` → `quantity`, `unit_price`, `final_price`, `discount`, `tax` [R]
- Categorization: `categoryName`, `brandName`, `productType`, `weightPerUnit` → `category`, `brand`, `flower_type` [R]

Source: `Transaction.cart.items[] (OrderItem)`.

## 4) Products → `products`
- Identity: `Product.id` → `products.product_id` [R]
- Basics: `sku`, `name`, `description`, `categoryId`, `vendorId` → `sku`, `name`, `category`, `vendor` [R]
- Pricing/weights: `unitPrice`, `unitValue`, `weightPerUnit` → `retail_price`, `unit_value`, `weight` [R]
- Potency: `thc`, `cbd`, `thca`, `cbda`, `cbg` → `thc_content`, `cbd_content`, etc. [A]
- Status: `active`/`archived` → `is_active` [R]
- Media: `assets[]` (images) → `image_url(s)` [A]

Key API: `/api/v1/partner/products`, `/api/v1/partner/products/{id}`, `/sku/{sku}`, `/modified`.

## 5) Staff / Budtenders → `staff`, `budtenders`
- From transactions (`sellerId`, `createdById`) + staff endpoints (if enabled) → `staff.id`, `staff_name`, counts [A]

## 6) Messages / Scheduled Messages
- Not in Blaze; continue using existing SMS system tables.

---

## Replace vs Augment vs Derived (high level)
- Replace: `customers.phone`, `email`, `last_visited`; `transactions.total_amount/total_tax/payment_type/status`; `transaction_items` pricing/qty; `products` core fields
- Augment: consent flags, medical flag, address normalization, product potency, images, staff and terminal metadata
- Derived: `days_since_last_visit`, `lifetime_value`, `total_visits`, `avg_sale_value`, churn/vip flags

## Sync Plan (light)
- Cadence (per Blaze rules): Members hourly (modified window), Transactions hourly (window), Products every 5 min (modified)
- Windows: Members use epoch ms `startDate/endDate`; Transactions accept string timestamps (ISO)
- Pagination: `skip/limit` in 500–1000 record batches; loop until empty
- Idempotency: upsert on primary keys (`id`, `sku`, etc.)
- Safety: rate limit headroom; backoff on 429; log last successful watermark per entity

## Minimal Field Fetch Sets
- Members: `id, firstName, lastName, primaryPhone, email, status, lastVisitDate, address, modified`
- Transactions: `id, memberId, status, startTime, endTime, cart{subTotal,total,tax,items{productId,productSku,quantity,unitPrice,finalPrice,discount,calcTax}}`
- Products: `id, sku, name, categoryId, vendorId, unitPrice, active, thc,cbd,thca,cbda,cbg`

## Verification Snippets (PowerShell)
- Members last 24h (limit 1) and Transactions (limit 1) are already in `docs/BLAZEAPI/next_steps.md`.

## Gaps / Open Questions
- Loyalty points source: confirm endpoint and shape for member balance/activity
- Staff directory endpoint availability; otherwise derive from transactions
- Any multi-location nuances (companyId/shopId filtering policy)
- Images/assets hosting preference and storage strategy

## Next Actions
1) Implement incremental fetchers (3 endpoints) writing to staging tables
2) Add transforms for Derived metrics (in DB views or ETL step)
3) Validate against a small rolling window, then widen
4) Flip dashboards to live tables after parity checks
