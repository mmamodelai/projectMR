#!/usr/bin/env python3
"""
Fix Duplicate Transaction Items - IMMEDIATE VERSION
Password pre-filled for quick execution
"""

import psycopg2
import time

# Supabase connection - pre-filled
DB_HOST = "db.kiwmwoqrguyrcpjytgte.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "9YqTPhlCxytiXxnb"  # Pre-filled

print("=" * 80)
print("DUPLICATE ITEMS REMOVAL - RUNNING NOW")
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
        options="-c statement_timeout=0"  # No timeout!
    )
    conn.autocommit = False
    cursor = conn.cursor()
    print("✅ Connected!\n")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

# Step 1: Check state
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
    print("✅ No duplicates! Already clean.")
    conn.close()
    exit(0)

# Step 2: Create clean table
print("Step 2: Creating clean table...")
print(f"  Removing {duplicates:,} duplicates...")
print("  This will take 2-5 minutes...\n")

start_time = time.time()

try:
    # Drop if exists from previous run
    cursor.execute("DROP TABLE IF EXISTS transaction_items_blaze_clean")
    conn.commit()
    
    # Create clean table
    cursor.execute("""
        CREATE TABLE transaction_items_blaze_clean AS
        SELECT DISTINCT ON (transaction_id, product_id, product_name, quantity, unit_price)
            *
        FROM transaction_items_blaze
        ORDER BY transaction_id, product_id, product_name, quantity, unit_price, id ASC
    """)
    
    conn.commit()
    elapsed = time.time() - start_time
    print(f"✅ Clean table created in {elapsed:.1f} seconds!")
    
except Exception as e:
    print(f"❌ Error creating clean table: {e}")
    conn.rollback()
    conn.close()
    exit(1)

# Step 3: Verify
print("\nStep 3: Verifying...")
cursor.execute("SELECT COUNT(*) FROM transaction_items_blaze_clean")
clean_count = cursor.fetchone()[0]
print(f"  Clean table: {clean_count:,} items")

if clean_count != unique:
    print(f"⚠️  ERROR: Expected {unique:,} but got {clean_count:,}")
    cursor.execute("DROP TABLE transaction_items_blaze_clean")
    conn.commit()
    conn.close()
    exit(1)

print("✅ Verification passed!")

# Step 4: Swap tables
print("\nStep 4: Swapping tables...")
print("  (backing up old table as transaction_items_blaze_old_with_dupes)")

try:
    # Rename old table
    cursor.execute("""
        ALTER TABLE transaction_items_blaze 
        RENAME TO transaction_items_blaze_old_with_dupes
    """)
    
    # Rename clean to main
    cursor.execute("""
        ALTER TABLE transaction_items_blaze_clean 
        RENAME TO transaction_items_blaze
    """)
    
    conn.commit()
    print("✅ Tables swapped!")
    
except Exception as e:
    print(f"❌ Error swapping tables: {e}")
    conn.rollback()
    conn.close()
    exit(1)

# Step 5: Recreate indexes
print("\nStep 5: Recreating indexes...")

try:
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
    print("✅ Indexes created!")
    
except Exception as e:
    print(f"⚠️  Index warning: {e}")

# Step 6: Final verification
print("\nStep 6: Final verification...")
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
    print("=" * 80)
    print("✅ SUCCESS! ALL DUPLICATES REMOVED!")
    print("=" * 80)
    print(f"   Removed:  {duplicates:,} duplicate items")
    print(f"   Kept:     {final_total:,} unique items")
    print(f"   Old table backed up as: transaction_items_blaze_old_with_dupes")
    print()
    print("Next steps:")
    print("  1. Check your viewer - items should look correct now")
    print("  2. Drop old table: DROP TABLE transaction_items_blaze_old_with_dupes;")
    print("  3. Fix Python code: Replace supabase_client.py with supabase_client_FIXED.py")
    print()
else:
    print(f"⚠️  WARNING: Still have {final_duplicates:,} duplicates")

cursor.close()
conn.close()

print("=" * 80)
print("DONE!")
print("=" * 80)



