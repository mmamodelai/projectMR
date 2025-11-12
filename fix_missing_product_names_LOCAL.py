#!/usr/bin/env python3
"""
Fix Missing Product Names - LOCAL VERSION
Backfill product_name and brand from products_blaze into transaction_items_blaze
"""

import psycopg2
import time

# Supabase connection
DB_HOST = "db.kiwmwoqrguyrcpjytgte.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "9YqTPhlCxytiXxnb"

print("=" * 80)
print("FIX MISSING PRODUCT NAMES - BACKFILL FROM PRODUCTS_BLAZE")
print("=" * 80)
print()

# Connect
print("Connecting to Supabase...")
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=30,
        options="-c statement_timeout=0"  # No timeout
    )
    conn.autocommit = False
    cursor = conn.cursor()
    print("Connected!\n")
except Exception as e:
    print(f"Connection failed: {e}")
    exit(1)

# Step 1: Check current state
print("Step 1: Current State")
print("-" * 80)
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(product_name) as with_name,
        COUNT(*) - COUNT(product_name) as missing_name
    FROM transaction_items_blaze
""")
total, with_name, missing_name = cursor.fetchone()
print(f"  Total items:        {total:,}")
print(f"  With product_name:  {with_name:,}")
print(f"  Missing name:       {missing_name:,}")
print()

if missing_name == 0:
    print("All items have product names! Nothing to fix.")
    conn.close()
    exit(0)

# Step 2: Check how many can be fixed
print("Step 2: Checking How Many Can Be Fixed")
print("-" * 80)
cursor.execute("""
    SELECT COUNT(*)
    FROM transaction_items_blaze ti
    WHERE ti.product_name IS NULL
    AND ti.product_id IS NOT NULL
    AND EXISTS (
        SELECT 1 FROM products_blaze p 
        WHERE p.product_id = ti.product_id
    )
""")
fixable = cursor.fetchone()[0]
print(f"  Can be fixed (have matching product): {fixable:,}")
print(f"  Cannot be fixed (no product match):   {missing_name - fixable:,}")
print()

if fixable == 0:
    print("No items can be fixed - products don't exist in products_blaze.")
    conn.close()
    exit(0)

confirm = input(f"Fix {fixable:,} items? This will run in batches of 50,000. (yes/no): ")
if confirm.lower() != 'yes':
    print("Cancelled.")
    conn.close()
    exit(0)

# Step 3: Backfill in batches
print("\nStep 3: Backfilling Product Names")
print("-" * 80)

batch_size = 50000
total_fixed = 0

while True:
    print(f"  Processing batch {(total_fixed // batch_size) + 1}...")
    start_time = time.time()
    
    cursor.execute(f"""
        UPDATE transaction_items_blaze ti
        SET 
            product_name = p.name,
            brand = COALESCE(ti.brand, 'Unknown')
        FROM products_blaze p
        WHERE ti.product_id = p.product_id
        AND ti.product_name IS NULL
        AND ti.id IN (
            SELECT id 
            FROM transaction_items_blaze 
            WHERE product_name IS NULL 
            AND product_id IS NOT NULL
            LIMIT {batch_size}
        )
    """)
    
    rows_updated = cursor.rowcount
    conn.commit()
    
    elapsed = time.time() - start_time
    total_fixed += rows_updated
    
    print(f"    Updated {rows_updated:,} items in {elapsed:.1f} seconds")
    
    if rows_updated == 0:
        break
    
    if rows_updated < batch_size:
        print("    (Last batch - done!)")
        break

print(f"\nTotal fixed: {total_fixed:,} items")

# Step 4: Final check
print("\nStep 4: Final Verification")
print("-" * 80)
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(product_name) as with_name,
        COUNT(*) - COUNT(product_name) as missing_name
    FROM transaction_items_blaze
""")
final_total, final_with_name, final_missing = cursor.fetchone()
print(f"  Total items:        {final_total:,}")
print(f"  With product_name:  {final_with_name:,}")
print(f"  Still missing:      {final_missing:,}")
print()

if final_missing > 0:
    print(f"NOTE: {final_missing:,} items still missing names.")
    print("These items either have no product_id or the product doesn't exist in products_blaze.")
else:
    print("SUCCESS: All items now have product names!")

cursor.close()
conn.close()

print()
print("=" * 80)
print("COMPLETE!")
print("=" * 80)
print("\nNext steps:")
print("  1. Check your IC Viewer - items should now appear correctly")
print("  2. If items still missing, re-sync products from Blaze API")
print("=" * 80)

