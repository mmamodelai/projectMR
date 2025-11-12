# Duplicate Customer Records Issue

## Problem
Blaze API sometimes creates multiple `member_id` records for the same person. This causes:
- Multiple records with same name
- One might have phone, one doesn't
- One might have transactions, one doesn't
- Viewers show the "wrong" record

## Example: Stephen Clare
```
Record 1: member_id = 61394100d18e30747f2b67f7
  - first_name: "stephen clare" (lowercase)
  - phone: +16199773020 ✅
  - Has data

Record 2: member_id = 683cea4e022c82ba434de1df
  - first_name: "STEPHEN CLARE" (uppercase)
  - phone: NULL ❌
  - Likely empty/duplicate
```

## Solutions

### Option 1: Update Duplicate with Missing Data
If they're the same person, copy the phone to the duplicate:
```sql
UPDATE customers_blaze
SET phone = '+16199773020'
WHERE member_id = '683cea4e022c82ba434de1df';
```

### Option 2: Delete Empty Duplicates
If the duplicate is truly empty:
```sql
DELETE FROM customers_blaze
WHERE member_id = '683cea4e022c82ba434de1df'
AND phone IS NULL
AND total_visits = 0;
```

### Option 3: Merge Records (Advanced)
1. Move all transactions from duplicate to main record
2. Copy any non-NULL fields from duplicate to main
3. Delete duplicate

## Prevention
The Blaze API sync should:
1. Check for existing records by name/phone before inserting
2. Use upsert logic with multiple keys (not just member_id)
3. Merge data if duplicate detected

## Finding Duplicates
Run: `sql_scripts/find_duplicate_customers.sql`

This shows all customers with >1 record.

