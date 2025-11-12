-- ====================================================================
-- MERGE DUPLICATES BY PHONE + NAME
-- ====================================================================
-- Rules:
--   * Same phone (normalized)
--   * Same first + last name (case-insensitive)
--   * Pick the record with more data (phone, email, visits) as keeper
--   * Move transactions, copy missing info, delete duplicates
--   * Run repeatedly until pairs_to_merge = 0
-- ====================================================================

-- Drop temp tables if they already exist
DROP TABLE IF EXISTS tmp_phone_norm;
DROP TABLE IF EXISTS tmp_phone_groups;
DROP TABLE IF EXISTS tmp_phone_members;
DROP TABLE IF EXISTS tmp_phone_keepers;
DROP TABLE IF EXISTS tmp_phone_dupes;

-- Normalize names (strip 'medgo', lowercase, split tokens)
CREATE TEMP TABLE tmp_phone_norm AS
SELECT
    member_id,
    REGEXP_REPLACE(LOWER(TRIM(first_name)), '^medgo\s+', '') AS first_norm,
    REGEXP_REPLACE(LOWER(TRIM(last_name)), '^medgo\s+', '') AS last_norm,
    REGEXP_REPLACE(phone, '[^0-9]', '', 'g') AS phone_digits,
    phone,
    email,
    total_visits,
    lifetime_value,
    date_of_birth,
    REGEXP_REPLACE(LOWER(TRIM(first_name || ' ' || last_name)), '^medgo\s+', '') AS full_name_norm,
    REGEXP_SPLIT_TO_ARRAY(REGEXP_REPLACE(LOWER(TRIM(first_name || ' ' || last_name)), '^medgo\s+', ''), '\s+') AS tokens
FROM customers_blaze
WHERE phone IS NOT NULL
  AND phone <> '';

ALTER TABLE tmp_phone_norm
ADD COLUMN first_token TEXT,
ADD COLUMN second_token TEXT,
ADD COLUMN last_token TEXT;

UPDATE tmp_phone_norm
SET
    first_token = tokens[1],
    second_token = CASE WHEN array_length(tokens, 1) >= 2 THEN tokens[2] END,
    last_token = CASE WHEN array_length(tokens, 1) >= 2 THEN tokens[array_length(tokens,1)] ELSE tokens[1] END;

-- Build group keys using first+last and first+second tokens
CREATE TEMP TABLE tmp_phone_groups AS
SELECT
    phone_digits,
    match_key,
    COUNT(*) AS group_size
FROM (
    SELECT
        phone_digits,
        first_token || '|' || last_token AS match_key
    FROM tmp_phone_norm
    WHERE last_token IS NOT NULL
  UNION ALL
    SELECT
        phone_digits,
        first_token || '|' || second_token AS match_key
    FROM tmp_phone_norm
    WHERE second_token IS NOT NULL
) g
WHERE phone_digits IS NOT NULL
  AND phone_digits <> ''
GROUP BY phone_digits, match_key
HAVING COUNT(*) > 1;

SELECT 'DUPLICATES BY PHONE+NAME' AS status,
       COALESCE(SUM(group_size) - COUNT(*), 0) AS pairs_to_merge
FROM tmp_phone_groups;

-- If no groups, exit early
WITH check_groups AS (
    SELECT COUNT(*) AS cnt FROM tmp_phone_groups
)
SELECT CASE WHEN cnt = 0 THEN 'No duplicates left - skipping merge' ELSE 'Processing merge...' END AS info
FROM check_groups;

-- Only continue if duplicates exist
WITH check_groups AS (
    SELECT COUNT(*) AS cnt FROM tmp_phone_groups
)
SELECT * FROM check_groups WHERE cnt > 0;

-- Expand group members
CREATE TEMP TABLE tmp_phone_members AS
SELECT DISTINCT
    n.*,
    g.match_key
FROM tmp_phone_norm n
JOIN tmp_phone_groups g
  ON n.phone_digits = g.phone_digits
 AND (
        (n.last_token IS NOT NULL AND (n.first_token || '|' || n.last_token) = g.match_key)
     OR (n.second_token IS NOT NULL AND (n.first_token || '|' || n.second_token) = g.match_key)
    );

-- Determine keeper per group
CREATE TEMP TABLE tmp_phone_keepers AS
SELECT
    phone_digits,
    match_key,
    member_id AS keeper_id,
    phone AS keeper_phone
FROM (
    SELECT
        m.*,
        1000 +
        CASE WHEN m.email IS NOT NULL AND m.email <> '' THEN 500 ELSE 0 END +
        COALESCE(m.total_visits, 0) * 10 +
        COALESCE(m.lifetime_value, 0) AS score,
        ROW_NUMBER() OVER (
            PARTITION BY phone_digits, match_key
            ORDER BY
                (1000 +
                 CASE WHEN m.email IS NOT NULL AND m.email <> '' THEN 500 ELSE 0 END +
                 COALESCE(m.total_visits, 0) * 10 +
                 COALESCE(m.lifetime_value, 0)) DESC,
                m.member_id ASC
        ) AS rank_in_group
    FROM tmp_phone_members m
) ranked
WHERE rank_in_group = 1;

CREATE TEMP TABLE tmp_phone_dupes AS
SELECT
    m.member_id AS dupe_id,
    k.keeper_id,
    m.phone_digits,
    m.first_token,
    m.second_token,
    m.last_token,
    m.phone AS dupe_phone,
    m.email AS dupe_email,
    m.total_visits,
    m.lifetime_value
FROM tmp_phone_members m
JOIN tmp_phone_keepers k
  ON m.phone_digits = k.phone_digits
 AND m.match_key = k.match_key
WHERE m.member_id <> k.keeper_id;

SELECT 'DUPLICATES IDENTIFIED' AS status, COUNT(*) AS dupes_found
FROM tmp_phone_dupes;

-- Copy missing contact info
UPDATE customers_blaze c
SET
    email = COALESCE(c.email, d.dupe_email),
    updated_at = NOW()
FROM tmp_phone_dupes d
WHERE c.member_id = d.keeper_id
  AND (c.email IS NULL OR c.email = '');

-- Move transactions
UPDATE transactions_blaze t
SET customer_id = d.keeper_id
FROM tmp_phone_dupes d
WHERE t.customer_id = d.dupe_id;

-- Delete duplicates
DELETE FROM customers_blaze c
USING tmp_phone_dupes d
WHERE c.member_id = d.dupe_id;

-- Recalculate stats for keepers
UPDATE customers_blaze c
SET
    total_visits = (
        SELECT COUNT(*)
        FROM transactions_blaze t
        WHERE t.customer_id = c.member_id
          AND t.blaze_status = 'Completed'
    ),
    lifetime_value = (
        SELECT COALESCE(SUM(total_amount), 0)
        FROM transactions_blaze t
        WHERE t.customer_id = c.member_id
          AND t.blaze_status = 'Completed'
    ),
    last_visited = (
        SELECT MAX(date::DATE)
        FROM transactions_blaze t
        WHERE t.customer_id = c.member_id
          AND t.blaze_status = 'Completed'
    ),
    vip_status = CASE
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = c.member_id
              AND t.blaze_status = 'Completed'
        ) >= 16 THEN 'VIP'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = c.member_id
              AND t.blaze_status = 'Completed'
        ) BETWEEN 11 AND 15 THEN 'Regular2'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = c.member_id
              AND t.blaze_status = 'Completed'
        ) BETWEEN 5 AND 10 THEN 'Regular1'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = c.member_id
              AND t.blaze_status = 'Completed'
        ) BETWEEN 2 AND 4 THEN 'Casual'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = c.member_id
              AND t.blaze_status = 'Completed'
        ) = 1 THEN 'First'
        ELSE 'New'
    END,
    updated_at = NOW()
WHERE c.member_id IN (SELECT keeper_id FROM tmp_phone_keepers);

SELECT 'MERGE COMPLETE - RUN AGAIN IF NEEDED' AS status;
