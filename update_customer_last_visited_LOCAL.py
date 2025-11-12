#!/usr/bin/env python3
"""
Update Customer Last Visited Dates
Fix the "stuck on Nov 5" problem by updating last_visited from transactions
"""

import psycopg2

DB_HOST = "db.kiwmwoqrguyrcpjytgte.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "9YqTPhlCxytiXxnb"

print("=" * 80)
print("UPDATE CUSTOMER LAST_VISITED DATES")
print("=" * 80)
print()

# Connect
print("Connecting...")
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    connect_timeout=30,
    options="-c statement_timeout=0"
)
conn.autocommit = False
cursor = conn.cursor()
print("Connected!\n")

# Check how many are out of date
print("Checking how many customers are out of date...")
cursor.execute("""
    SELECT COUNT(*)
    FROM customers_blaze c
    WHERE EXISTS (
        SELECT 1 
        FROM transactions_blaze t 
        WHERE t.customer_id = c.member_id 
        AND t.date::date > c.last_visited::date
    )
""")
out_of_date = cursor.fetchone()[0]
print(f"  {out_of_date:,} customers have transactions newer than their last_visited")
print()

if out_of_date == 0:
    print("All customers are up to date!")
    conn.close()
    exit(0)

confirm = input(f"Update {out_of_date:,} customers? (yes/no): ")
if confirm.lower() != 'yes':
    print("Cancelled.")
    conn.close()
    exit(0)

# Update
print("\nUpdating customer last_visited dates...")
cursor.execute("""
    UPDATE customers_blaze c
    SET last_visited = (
        SELECT MAX(t.date)::date
        FROM transactions_blaze t
        WHERE t.customer_id = c.member_id
    )
    WHERE EXISTS (
        SELECT 1 
        FROM transactions_blaze t 
        WHERE t.customer_id = c.member_id
    )
""")

rows_updated = cursor.rowcount
conn.commit()

print(f"Updated {rows_updated:,} customers")
print()

# Verify
print("Verifying - Most recent customers now:")
cursor.execute("""
    SELECT name, last_visited
    FROM customers_blaze
    WHERE last_visited IS NOT NULL
    ORDER BY last_visited DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"  {row[0][:30]:<30} | {row[1]}")

cursor.close()
conn.close()

print()
print("=" * 80)
print("COMPLETE!")
print("=" * 80)
print("\nNow restart the IC Viewer:")
print("  cd mota-crm/viewers")
print("  python crm_integrated_blaze_v5.py")
print()
print("It should now show Nov 9 customers at the top!")
print("=" * 80)

