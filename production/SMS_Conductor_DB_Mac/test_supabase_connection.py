#!/usr/bin/env python3
"""Quick test to verify Supabase connection works"""
import sys

try:
    from supabase import create_client
    print("[OK] supabase module imported")
except ImportError as e:
    print(f"[ERROR] Failed to import supabase: {e}")
    print("Install with: pip install supabase")
    input("Press Enter to exit...")
    sys.exit(1)

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

print(f"\nConnecting to: {SUPABASE_URL}")
print("Testing connection...")

try:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Client created")
    
    # Test query
    print("\nTesting query on transaction_items_blaze...")
    response = client.table('transaction_items_blaze').select('id').limit(5).execute()
    
    if response.data:
        print(f"[OK] Query successful! Found {len(response.data)} rows")
        print(f"Sample IDs: {[r['id'] for r in response.data[:3]]}")
    else:
        print("[WARNING] Query returned no data")
    
    # Check total count (this might timeout if DB is slow)
    print("\nChecking total row count (this may take a moment)...")
    try:
        count_response = client.table('transaction_items_blaze').select('id', count='exact').limit(1).execute()
        if hasattr(count_response, 'count'):
            print(f"[OK] Total rows in transaction_items_blaze: {count_response.count:,}")
        else:
            print("[INFO] Count not available in response")
    except Exception as e:
        print(f"[WARNING] Count query failed (DB might be slow): {e}")
    
    print("\n" + "="*60)
    print("CONNECTION TEST: SUCCESS")
    print("="*60)
    print("\nYou can now run: python dedupe_blaze_supabase.py")
    
except Exception as e:
    print(f"\n[ERROR] Connection failed: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*60)
    print("CONNECTION TEST: FAILED")
    print("="*60)

input("\nPress Enter to exit...")

