-- =====================================================================
-- Switch FK references from public.customers → public.customers_blaze
-- and drop public.customers
-- Date: 2025-11-07
-- SAFE PLAN:
--   1) Run Preflight checks (A). If OK:
--   2) Ensure uniqueness on customers_blaze.member_id (B).
--   3) Re-point FK constraints to customers_blaze (C).
--   4) Drop old customers table (D).
-- Notes:
--   - This assumes your FKs reference customers(member_id), as in your schema.
--   - If any “missing in blaze” rows appear in A2, fix/import those first.
-- =====================================================================

-- ---------------------------------------------------------------------
-- SECTION A: Preflight
-- ---------------------------------------------------------------------
-- A1) Show current FKs pointing at public.customers
SELECT
  tc.table_name   AS child_table,
  kcu.column_name AS child_column,
  ccu.table_name  AS parent_table,
  ccu.column_name AS parent_column,
  tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
  AND ccu.table_name = 'customers'
ORDER BY child_table, constraint_name;

-- A2) Check that every referencing customer_id exists in customers_blaze
--     for each known child table. If any rows return, resolve before switching.
WITH missing AS (
  SELECT 'transactions' AS src, t.customer_id AS customer_id
  FROM public.transactions t
  LEFT JOIN public.customers_blaze b ON b.member_id = t.customer_id
  WHERE b.member_id IS NULL AND t.customer_id IS NOT NULL
  UNION ALL
  SELECT 'leads', l.customer_id
  FROM public.leads l
  LEFT JOIN public.customers_blaze b ON b.member_id = l.customer_id
  WHERE b.member_id IS NULL AND l.customer_id IS NOT NULL
  UNION ALL
  SELECT 'customer_product_affinity', a.customer_id
  FROM public.customer_product_affinity a
  LEFT JOIN public.customers_blaze b ON b.member_id = a.customer_id
  WHERE b.member_id IS NULL AND a.customer_id IS NOT NULL
  UNION ALL
  SELECT 'customer_visit_patterns', v.customer_id
  FROM public.customer_visit_patterns v
  LEFT JOIN public.customers_blaze b ON b.member_id = v.customer_id
  WHERE b.member_id IS NULL AND v.customer_id IS NOT NULL
  UNION ALL
  SELECT 'scheduled_messages', s.customer_id
  FROM public.scheduled_messages s
  LEFT JOIN public.customers_blaze b ON b.member_id = s.customer_id
  WHERE b.member_id IS NULL AND s.customer_id IS NOT NULL
)
SELECT * FROM missing LIMIT 50;

-- A3) Check duplicates/nulls in customers_blaze.member_id
SELECT member_id, COUNT(*) AS c
FROM public.customers_blaze
GROUP BY member_id
HAVING member_id IS NULL OR COUNT(*) > 1
ORDER BY c DESC NULLS LAST;

-- ---------------------------------------------------------------------
-- SECTION B: Ensure uniqueness on customers_blaze.member_id
--   (Required for FK target. Create a unique index if none exists.)
--   NOTE: Run only after A3 confirms no duplicates/nulls.
-- ---------------------------------------------------------------------
-- CREATE UNIQUE INDEX IF NOT EXISTS ux_customers_blaze_member_id
--   ON public.customers_blaze(member_id);

-- ---------------------------------------------------------------------
-- SECTION C: Re-point FK constraints
--   Drops old FKs that reference customers(member_id) and recreates them
--   to point at customers_blaze(member_id).
-- ---------------------------------------------------------------------
-- BEGIN;

-- customer_product_affinity.customer_id → customers_blaze.member_id
-- (drop old, then add new)
-- ALTER TABLE IF EXISTS public.customer_product_affinity
--   DROP CONSTRAINT IF EXISTS fk_affinity_customer;
-- ALTER TABLE IF EXISTS public.customer_product_affinity
--   ADD CONSTRAINT fk_affinity_customer
--   FOREIGN KEY (customer_id)
--   REFERENCES public.customers_blaze(member_id);

-- customer_visit_patterns.customer_id → customers_blaze.member_id
-- ALTER TABLE IF EXISTS public.customer_visit_patterns
--   DROP CONSTRAINT IF EXISTS customer_visit_patterns_customer_id_fkey;
-- ALTER TABLE IF EXISTS public.customer_visit_patterns
--   ADD CONSTRAINT customer_visit_patterns_customer_id_fkey
--   FOREIGN KEY (customer_id)
--   REFERENCES public.customers_blaze(member_id);

-- leads.customer_id → customers_blaze.member_id
-- ALTER TABLE IF EXISTS public.leads
--   DROP CONSTRAINT IF EXISTS leads_customer_id_fkey;
-- ALTER TABLE IF EXISTS public.leads
--   ADD CONSTRAINT leads_customer_id_fkey
--   FOREIGN KEY (customer_id)
--   REFERENCES public.customers_blaze(member_id);

-- scheduled_messages.customer_id → customers_blaze.member_id
-- ALTER TABLE IF EXISTS public.scheduled_messages
--   DROP CONSTRAINT IF EXISTS scheduled_messages_customer_id_fkey;
-- ALTER TABLE IF EXISTS public.scheduled_messages
--   ADD CONSTRAINT scheduled_messages_customer_id_fkey
--   FOREIGN KEY (customer_id)
--   REFERENCES public.customers_blaze(member_id);

-- transactions.customer_id → customers_blaze.member_id
-- ALTER TABLE IF EXISTS public.transactions
--   DROP CONSTRAINT IF EXISTS transactions_customer_id_fkey;
-- ALTER TABLE IF EXISTS public.transactions
--   ADD CONSTRAINT transactions_customer_id_fkey
--   FOREIGN KEY (customer_id)
--   REFERENCES public.customers_blaze(member_id);

-- COMMIT;

-- ---------------------------------------------------------------------
-- SECTION D: Drop old customers table (after FK switch)
-- ---------------------------------------------------------------------
-- BEGIN;
-- DROP TABLE IF EXISTS public.customers;
-- COMMIT;

-- (Optional) For safety, create a compatibility VIEW named customers that
-- points at customers_blaze (uncomment if you want temporary compatibility):
-- CREATE OR REPLACE VIEW public.customers AS
-- SELECT
--   NULL::integer AS id, -- placeholder to match old schema if needed
--   member_id,
--   name, phone, email, loyalty_points, total_visits, total_sales,
--   total_refunds, gross_sales, gross_refunds, avg_sale_value, lifetime_value,
--   customer_type, member_group, marketing_source, state, zip_code, date_joined,
--   last_visited, vip_status, churn_risk, days_since_last_visit,
--   NOW() AS created_at, NOW() AS updated_at,
--   street_address, city
-- FROM public.customers_blaze;

-- =====================================================================
-- End of file
-- =====================================================================




