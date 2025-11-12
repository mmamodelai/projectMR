#!/usr/bin/env python3
"""
Quick check: Is the database healthy enough to run operations?
"""
from supabase import create_client
import time

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

def check_health():
    """Test database responsiveness"""
    print("="*70)
    print("DATABASE HEALTH CHECK")
    print("="*70)
    
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    tests = [
        ("Simple SELECT (limit 1)", lambda: client.table('transactions_blaze').select('id').limit(1).execute()),
        ("COUNT query", lambda: client.table('transactions_blaze').select('id', count='exact').limit(1).execute()),
        ("RPC function call", lambda: client.rpc('dedupe_transaction_items_batch', {'batch_size': 1}).execute()),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}...")
        start = time.time()
        try:
            result = test_func()
            elapsed = time.time() - start
            if elapsed < 5:
                status = "✅ OK"
            elif elapsed < 30:
                status = "⚠️  SLOW"
            else:
                status = "❌ TIMEOUT"
            print(f"  {status} ({elapsed:.1f}s)")
            results.append((test_name, True, elapsed))
        except Exception as e:
            elapsed = time.time() - start
            error_str = str(e).lower()
            if "timeout" in error_str:
                status = "❌ TIMEOUT"
            else:
                status = "❌ ERROR"
            print(f"  {status} ({elapsed:.1f}s) - {str(e)[:60]}")
            results.append((test_name, False, elapsed))
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    all_ok = all(r[1] for r in results)
    
    if all_ok:
        print("\n✅ Database appears HEALTHY")
        print("   You can try normal deduplication:")
        print("   python dedupe_blaze_rpc.py")
    else:
        print("\n⚠️  Database is OVERLOADED or UNHEALTHY")
        print("\nRecommendations:")
        print("  1. Check Supabase dashboard - is status 'Healthy'?")
        print("  2. Wait for database to recover")
        print("  3. Delete archive tables first (instant space)")
        print("  4. Use ultra-tiny batch deduplication:")
        print("     python dedupe_blaze_ultra_tiny.py")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    check_health()
    input("\nPress Enter to exit...")

