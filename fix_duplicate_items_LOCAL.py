#!/usr/bin/env python3
"""
Fix Duplicate Transaction Items - LOCAL VERSION
Connects directly to Supabase and removes duplicates in batches
No timeout limits!
"""

import os
import psycopg2
from psycopg2 import sql
import time

# Supabase connection details
# Get these from: Supabase Dashboard -> Settings -> Database -> Connection String
DB_HOST = "db.kiwmwoqrguyrcpjytgte.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = input("Enter your Supabase database password: ")

print("=" * 80)
print("DUPLICATE ITEMS REMOVAL TOOL - LOCAL VERSION")
print("=" * 80)
print()

# Connect to database
print("Connecting to Supabase...")
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    connect_timeout=30,
    options="-c statement_timeout=0"  # No timeout!
)
conn.autocommit = False
cursor = conn.cursor()

print("✅ Connected successfully!\n")

# Step 1: Check current state
print("Step 1: Checking current state...")
cursor.execute("""
    SELECT 
        COUNT(*) as total_items,
        COUNT(DISTINCT (transaction_id, product_id, product_name, quantity)) as unique_items
    FROM transaction_items_blaze
""")
total, unique = cursor.fetchone()
duplicates = total - unique

print(f"  Total items:    {total:,}")
print(f"  Unique items:   {unique:,}")
print(f"  Duplicates:     {duplicates:,}")
print()

if duplicates == 0:
    print("✅ No duplicates found! Nothing to do.")
    conn.close()
    exit(0)

# Step 2: Create clean table
confirm = input(f"Create new table with {unique:,} unique items? (yes/no): ")
if confirm.lower() != 'yes':
    print("Cancelled.")
    conn.close()
    exit(0)

print("\nStep 2: Creating clean table...")
print("  This may take 2-5 minutes with 2.2M rows...")
start_time = time.time()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaction_items_blaze_clean AS
    SELECT DISTINCT ON (transaction_id, product_id, product_name, quantity, unit_price)
        *
    FROM transaction_items_blaze
    ORDER BY transaction_id, product_id, product_name, quantity, unit_price, id ASC
""")

elapsed = time.time() - start_time
print(f"✅ Clean table created in {elapsed:.1f} seconds!")
conn.commit()

# Step 3: Verify
print("\nStep 3: Verifying clean table...")
cursor.execute("SELECT COUNT(*) FROM transaction_items_blaze_clean")
clean_count = cursor.fetchone()[0]
print(f"  Clean table has: {clean_count:,} items")

if clean_count != unique:
    print(f"⚠️  WARNING: Expected {unique:,} but got {clean_count:,}")
    print("   Something went wrong. Aborting.")
    cursor.execute("DROP TABLE IF EXISTS transaction_items_blaze_clean")
    conn.commit()
    conn.close()
    exit(1)

print("✅ Verification passed!")
print()

# Step 4: Swap tables
confirm = input("Swap tables? This will:\n"
                "  1. Rename old table to transaction_items_blaze_old_with_dupes\n"
                "  2. Rename clean table to transaction_items_blaze\n"
                "  Type 'yes' to proceed: ")

if confirm.lower() != 'yes':
    print("Cancelled. Clean table still exists if you want to check it.")
    conn.close()
    exit(0)

print("\nStep 4: Swapping tables...")

# Rename old table
cursor.execute("""
    ALTER TABLE transaction_items_blaze 
    RENAME TO transaction_items_blaze_old_with_dupes
""")

# Rename clean table to main name
cursor.execute("""
    ALTER TABLE transaction_items_blaze_clean 
    RENAME TO transaction_items_blaze
""")

# Recreate indexes
print("  Recreating indexes...")
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_items_blaze_transaction_id 
    ON transaction_items_blaze(transaction_id)
""")
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_items_blaze_product_id 
    ON transaction_items_blaze(product_id)
""")
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_transaction_items_dedup 
    ON transaction_items_blaze(transaction_id, product_id, product_name, quantity, unit_price)
""")

conn.commit()
print("✅ Tables swapped successfully!")
print()

# Step 5: Final verification
print("Step 5: Final verification...")
cursor.execute("""
    SELECT 
        COUNT(*) as total_items,
        COUNT(DISTINCT (transaction_id, product_id, product_name, quantity)) as unique_items
    FROM transaction_items_blaze
""")
final_total, final_unique = cursor.fetchone()
final_duplicates = final_total - final_unique

print(f"  Total items:    {final_total:,}")
print(f"  Unique items:   {final_unique:,}")
print(f"  Duplicates:     {final_duplicates:,}")
print()

if final_duplicates == 0:
    print("✅ SUCCESS! All duplicates removed!")
    print(f"   Removed {duplicates:,} duplicate items")
    print(f"   Old table backed up as: transaction_items_blaze_old_with_dupes")
    print()
    print("You can drop the old table with:")
    print("   DROP TABLE transaction_items_blaze_old_with_dupes;")
else:
    print(f"⚠️  WARNING: Still have {final_duplicates:,} duplicates")

print()
print("=" * 80)
print("COMPLETE!")
print("=" * 80)

cursor.close()
conn.close()



