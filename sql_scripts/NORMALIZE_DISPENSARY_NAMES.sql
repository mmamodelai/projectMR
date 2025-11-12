-- =====================================================
-- NORMALIZE DISPENSARY NAMES
-- Fixes case-sensitive duplicates and renames
-- =====================================================

-- Step 1: Show current state
SELECT 'BEFORE CLEANUP:' AS status;
SELECT 
    dispensary_name,
    COUNT(*) AS budtender_count
FROM budtenders
WHERE dispensary_name IS NOT NULL
GROUP BY dispensary_name
ORDER BY dispensary_name;

-- Step 2: Rename X1/x1 variations to "Altamont Wellness"
UPDATE budtenders
SET dispensary_name = 'Altamont Wellness'
WHERE LOWER(dispensary_name) = 'x1';

-- Step 3: Rename Club W variations to "The W"
UPDATE budtenders
SET dispensary_name = 'The W'
WHERE LOWER(dispensary_name) IN ('club w', 'club w.');

-- Step 4: Fix other case-sensitive duplicates (normalize to proper case)
UPDATE budtenders
SET dispensary_name = 'Phenos'
WHERE LOWER(dispensary_name) = 'phenos';

UPDATE budtenders
SET dispensary_name = 'Firehouse'
WHERE LOWER(dispensary_name) = 'firehouse';

UPDATE budtenders
SET dispensary_name = 'Higher Level'
WHERE dispensary_name = 'Higher level';  -- Note: lowercase 'l' only

-- Step 5: Show final state
SELECT 'AFTER CLEANUP:' AS status;
SELECT 
    dispensary_name,
    COUNT(*) AS budtender_count
FROM budtenders
WHERE dispensary_name IS NOT NULL
GROUP BY dispensary_name
ORDER BY dispensary_name;

-- Step 6: Verify specific changes
SELECT 'VERIFICATION:' AS status;
SELECT 
    'Altamont Wellness (was X1/x1)' AS change_description,
    COUNT(*) AS budtender_count
FROM budtenders
WHERE dispensary_name = 'Altamont Wellness'
UNION ALL
SELECT 
    'The W (was Club W/Club w)' AS change_description,
    COUNT(*) AS budtender_count
FROM budtenders
WHERE dispensary_name = 'The W'
UNION ALL
SELECT 
    'Phenos (normalized)' AS change_description,
    COUNT(*) AS budtender_count
FROM budtenders
WHERE dispensary_name = 'Phenos'
UNION ALL
SELECT 
    'Firehouse (normalized)' AS change_description,
    COUNT(*) AS budtender_count
FROM budtenders
WHERE dispensary_name = 'Firehouse'
UNION ALL
SELECT 
    'Higher Level (normalized)' AS change_description,
    COUNT(*) AS budtender_count
FROM budtenders
WHERE dispensary_name = 'Higher Level';

-- Step 7: Check for any remaining case-sensitive duplicates
SELECT 'REMAINING DUPLICATES:' AS status;
SELECT 
    LOWER(dispensary_name) AS lowercase_name,
    ARRAY_AGG(DISTINCT dispensary_name) AS variations,
    COUNT(*) AS total_budtenders
FROM budtenders
WHERE dispensary_name IS NOT NULL
GROUP BY LOWER(dispensary_name)
HAVING COUNT(DISTINCT dispensary_name) > 1;

-- Summary
SELECT 'SUMMARY:' AS status;
SELECT 
    COUNT(DISTINCT dispensary_name) AS unique_dispensaries,
    COUNT(*) AS total_budtenders,
    COUNT(DISTINCT LOWER(dispensary_name)) AS unique_lowercase_dispensaries
FROM budtenders
WHERE dispensary_name IS NOT NULL;

SELECT 
    CASE 
        WHEN COUNT(DISTINCT dispensary_name) = COUNT(DISTINCT LOWER(dispensary_name))
        THEN 'SUCCESS! No case-sensitive duplicates remaining.'
        ELSE 'WARNING: Case-sensitive duplicates still exist.'
    END AS result
FROM budtenders
WHERE dispensary_name IS NOT NULL;



