-- =====================================================================
-- Compare public.customers vs public.customers_blaze
-- Date: 2025-11-07
-- Purpose:
--   - Quantify overlap and which table has more complete data by column
--   - Show where blaze has a value and customers is NULL (and vice versa)
--   - Show examples of differing values for key fields
-- Usage:
--   Run each section in Supabase SQL Editor. Use results to decide whether to
--   migrate values from *_blaze into canonical `customers` before dropping.
-- =====================================================================

-- ---------------------------------------------------------------------
-- SECTION A: High-level overlap
-- ---------------------------------------------------------------------
SELECT
  (SELECT COUNT(*) FROM public.customers)               AS customers_rows,
  (SELECT COUNT(*) FROM public.customers_blaze)         AS customers_blaze_rows,
  (SELECT COUNT(*) FROM public.customers c
     JOIN public.customers_blaze b ON b.member_id = c.member_id) AS overlap_rows,
  (SELECT COUNT(*) FROM public.customers c
     LEFT JOIN public.customers_blaze b ON b.member_id = c.member_id
     WHERE b.member_id IS NULL)                         AS only_in_customers,
  (SELECT COUNT(*) FROM public.customers_blaze b
     LEFT JOIN public.customers c ON c.member_id = b.member_id
     WHERE c.member_id IS NULL)                         AS only_in_blaze;

-- ---------------------------------------------------------------------
-- SECTION B: Column completeness comparison (non-null counts and direction)
-- Key shared fields to compare; add/remove columns as needed.
-- ---------------------------------------------------------------------
WITH j AS (
  SELECT
    COALESCE(c.member_id, b.member_id) AS member_id,
    c.name           AS c_name,            b.name           AS b_name,
    c.phone          AS c_phone,           b.phone          AS b_phone,
    c.email          AS c_email,           b.email          AS b_email,
    c.state          AS c_state,           b.state          AS b_state,
    c.city           AS c_city,            b.city           AS b_city,
    c.zip_code       AS c_zip,             b.zip_code       AS b_zip,
    c.street_address AS c_addr,            b.street_address AS b_addr,
    c.last_visited   AS c_last_visited,    b.last_visited   AS b_last_visited,
    c.date_joined    AS c_date_joined,     b.date_joined    AS b_date_joined,
    c.loyalty_points AS c_points,          b.loyalty_points AS b_points,
    c.total_visits   AS c_visits,          b.total_visits   AS b_visits,
    c.lifetime_value AS c_ltv,             b.lifetime_value AS b_ltv,
    c.days_since_last_visit AS c_days_since, b.days_since_last_visit AS b_days_since,
    c.vip_status     AS c_vip,             b.vip_status     AS b_vip,
    c.churn_risk     AS c_churn,           b.churn_risk     AS b_churn
  FROM public.customers c
  FULL OUTER JOIN public.customers_blaze b
    ON b.member_id = c.member_id
)
SELECT * FROM (
  SELECT 'name' AS column,
         SUM((c_name  IS NOT NULL)::int) AS customers_non_null,
         SUM((b_name  IS NOT NULL)::int) AS blaze_non_null,
         SUM((c_name  IS NULL AND b_name  IS NOT NULL)::int) AS blaze_more_complete,
         SUM((c_name  IS NOT NULL AND b_name  IS NULL)::int) AS customers_more_complete,
         SUM((c_name  IS NOT NULL AND b_name IS NOT NULL AND c_name IS DISTINCT FROM b_name)::int) AS values_different
  FROM j
  UNION ALL
  SELECT 'phone',  SUM((c_phone IS NOT NULL)::int),  SUM((b_phone IS NOT NULL)::int),
                   SUM((c_phone IS NULL AND b_phone IS NOT NULL)::int),
                   SUM((c_phone IS NOT NULL AND b_phone IS NULL)::int),
                   SUM((c_phone IS NOT NULL AND b_phone IS NOT NULL AND c_phone IS DISTINCT FROM b_phone)::int)
  FROM j
  UNION ALL
  SELECT 'email',  SUM((c_email IS NOT NULL)::int),  SUM((b_email IS NOT NULL)::int),
                   SUM((c_email IS NULL AND b_email IS NOT NULL)::int),
                   SUM((c_email IS NOT NULL AND b_email IS NULL)::int),
                   SUM((c_email IS NOT NULL AND b_email IS NOT NULL AND c_email IS DISTINCT FROM b_email)::int)
  FROM j
  UNION ALL
  SELECT 'state',  SUM((c_state IS NOT NULL)::int),  SUM((b_state IS NOT NULL)::int),
                   SUM((c_state IS NULL AND b_state IS NOT NULL)::int),
                   SUM((c_state IS NOT NULL AND b_state IS NULL)::int),
                   SUM((c_state IS NOT NULL AND b_state IS NOT NULL AND c_state IS DISTINCT FROM b_state)::int)
  FROM j
  UNION ALL
  SELECT 'city',   SUM((c_city  IS NOT NULL)::int),  SUM((b_city  IS NOT NULL)::int),
                   SUM((c_city  IS NULL AND b_city  IS NOT NULL)::int),
                   SUM((c_city  IS NOT NULL AND b_city  IS NULL)::int),
                   SUM((c_city  IS NOT NULL AND b_city  IS NOT NULL AND c_city IS DISTINCT FROM b_city)::int)
  FROM j
  UNION ALL
  SELECT 'zip_code', SUM((c_zip IS NOT NULL)::int),  SUM((b_zip IS NOT NULL)::int),
                     SUM((c_zip IS NULL AND b_zip IS NOT NULL)::int),
                     SUM((c_zip IS NOT NULL AND b_zip IS NULL)::int),
                     SUM((c_zip IS NOT NULL AND b_zip IS NOT NULL AND c_zip IS DISTINCT FROM b_zip)::int)
  FROM j
  UNION ALL
  SELECT 'street_address', SUM((c_addr IS NOT NULL)::int),  SUM((b_addr IS NOT NULL)::int),
                           SUM((c_addr IS NULL AND b_addr IS NOT NULL)::int),
                           SUM((c_addr IS NOT NULL AND b_addr IS NULL)::int),
                           SUM((c_addr IS NOT NULL AND b_addr IS NOT NULL AND c_addr IS DISTINCT FROM b_addr)::int)
  FROM j
  UNION ALL
  SELECT 'last_visited', SUM((c_last_visited IS NOT NULL)::int),  SUM((b_last_visited IS NOT NULL)::int),
                         SUM((c_last_visited IS NULL AND b_last_visited IS NOT NULL)::int),
                         SUM((c_last_visited IS NOT NULL AND b_last_visited IS NULL)::int),
                         SUM((c_last_visited IS NOT NULL AND b_last_visited IS NOT NULL AND c_last_visited IS DISTINCT FROM b_last_visited)::int)
  FROM j
  UNION ALL
  SELECT 'date_joined', SUM((c_date_joined IS NOT NULL)::int),  SUM((b_date_joined IS NOT NULL)::int),
                        SUM((c_date_joined IS NULL AND b_date_joined IS NOT NULL)::int),
                        SUM((c_date_joined IS NOT NULL AND b_date_joined IS NULL)::int),
                        SUM((c_date_joined IS NOT NULL AND b_date_joined IS NOT NULL AND c_date_joined IS DISTINCT FROM b_date_joined)::int)
  FROM j
  UNION ALL
  SELECT 'loyalty_points', SUM((c_points IS NOT NULL)::int),  SUM((b_points IS NOT NULL)::int),
                           SUM((c_points IS NULL AND b_points IS NOT NULL)::int),
                           SUM((c_points IS NOT NULL AND b_points IS NULL)::int),
                           SUM((c_points IS NOT NULL AND b_points IS NOT NULL AND c_points IS DISTINCT FROM b_points)::int)
  FROM j
  UNION ALL
  SELECT 'total_visits', SUM((c_visits IS NOT NULL)::int),  SUM((b_visits IS NOT NULL)::int),
                         SUM((c_visits IS NULL AND b_visits IS NOT NULL)::int),
                         SUM((c_visits IS NOT NULL AND b_visits IS NULL)::int),
                         SUM((c_visits IS NOT NULL AND b_visits IS NOT NULL AND c_visits IS DISTINCT FROM b_visits)::int)
  FROM j
  UNION ALL
  SELECT 'lifetime_value', SUM((c_ltv IS NOT NULL)::int),  SUM((b_ltv IS NOT NULL)::int),
                           SUM((c_ltv IS NULL AND b_ltv IS NOT NULL)::int),
                           SUM((c_ltv IS NOT NULL AND b_ltv IS NULL)::int),
                           SUM((c_ltv IS NOT NULL AND b_ltv IS NOT NULL AND c_ltv IS DISTINCT FROM b_ltv)::int)
  FROM j
  UNION ALL
  SELECT 'days_since_last_visit', SUM((c_days_since IS NOT NULL)::int),  SUM((b_days_since IS NOT NULL)::int),
                                 SUM((c_days_since IS NULL AND b_days_since IS NOT NULL)::int),
                                 SUM((c_days_since IS NOT NULL AND b_days_since IS NULL)::int),
                                 SUM((c_days_since IS NOT NULL AND b_days_since IS NOT NULL AND c_days_since IS DISTINCT FROM b_days_since)::int)
  FROM j
  UNION ALL
  SELECT 'vip_status', SUM((c_vip IS NOT NULL)::int),  SUM((b_vip IS NOT NULL)::int),
                       SUM((c_vip IS NULL AND b_vip IS NOT NULL)::int),
                       SUM((c_vip IS NOT NULL AND b_vip IS NULL)::int),
                       SUM((c_vip IS NOT NULL AND b_vip IS NOT NULL AND c_vip IS DISTINCT FROM b_vip)::int)
  FROM j
  UNION ALL
  SELECT 'churn_risk', SUM((c_churn IS NOT NULL)::int),  SUM((b_churn IS NOT NULL)::int),
                       SUM((c_churn IS NULL AND b_churn IS NOT NULL)::int),
                       SUM((c_churn IS NOT NULL AND b_churn IS NULL)::int),
                       SUM((c_churn IS NOT NULL AND b_churn IS NOT NULL AND c_churn IS DISTINCT FROM b_churn)::int)
  FROM j
) s
ORDER BY column;

-- ---------------------------------------------------------------------
-- SECTION C: Sample diffs (top 20) where blaze has value, customers NULL
-- ---------------------------------------------------------------------
-- Phone
SELECT j.member_id, j.c_phone AS customers_phone, j.b_phone AS blaze_phone
FROM (
  SELECT COALESCE(c.member_id, b.member_id) AS member_id, c.phone AS c_phone, b.phone AS b_phone
  FROM public.customers c
  FULL OUTER JOIN public.customers_blaze b ON b.member_id = c.member_id
 ) j
WHERE j.c_phone IS NULL AND j.b_phone IS NOT NULL
LIMIT 20;

-- Email
SELECT j.member_id, j.c_email AS customers_email, j.b_email AS blaze_email
FROM (
  SELECT COALESCE(c.member_id, b.member_id) AS member_id, c.email AS c_email, b.email AS b_email
  FROM public.customers c
  FULL OUTER JOIN public.customers_blaze b ON b.member_id = c.member_id
 ) j
WHERE j.c_email IS NULL AND j.b_email IS NOT NULL
LIMIT 20;

-- Address
SELECT j.member_id, j.c_addr AS customers_address, j.b_addr AS blaze_address
FROM (
  SELECT COALESCE(c.member_id, b.member_id) AS member_id, c.street_address AS c_addr, b.street_address AS b_addr
  FROM public.customers c
  FULL OUTER JOIN public.customers_blaze b ON b.member_id = c.member_id
 ) j
WHERE j.c_addr IS NULL AND j.b_addr IS NOT NULL
LIMIT 20;

-- ---------------------------------------------------------------------
-- SECTION D: “Best-of” merged preview (read-only)
-- Uses blaze value when customers is NULL, otherwise customers.
-- Helpful to estimate benefits of a one-time merge before drop.
-- ---------------------------------------------------------------------
SELECT
  COALESCE(c.member_id, b.member_id) AS member_id,
  COALESCE(c.name,            b.name)            AS name,
  COALESCE(c.phone,           b.phone)           AS phone,
  COALESCE(c.email,           b.email)           AS email,
  COALESCE(c.state,           b.state)           AS state,
  COALESCE(c.city,            b.city)            AS city,
  COALESCE(c.zip_code,        b.zip_code)        AS zip_code,
  COALESCE(c.street_address,  b.street_address)  AS street_address,
  COALESCE(c.last_visited,    b.last_visited)    AS last_visited,
  COALESCE(c.date_joined,     b.date_joined)     AS date_joined,
  COALESCE(c.loyalty_points,  b.loyalty_points)  AS loyalty_points,
  COALESCE(c.total_visits,    b.total_visits)    AS total_visits,
  COALESCE(c.lifetime_value,  b.lifetime_value)  AS lifetime_value,
  COALESCE(c.days_since_last_visit, b.days_since_last_visit) AS days_since_last_visit,
  COALESCE(c.vip_status,      b.vip_status)      AS vip_status,
  COALESCE(c.churn_risk,      b.churn_risk)      AS churn_risk
FROM public.customers c
FULL OUTER JOIN public.customers_blaze b
  ON b.member_id = c.member_id
LIMIT 100;

-- =====================================================================
-- End of file
-- =====================================================================




