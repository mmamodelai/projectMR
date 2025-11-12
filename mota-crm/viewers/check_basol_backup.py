#!/usr/bin/env python3
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("CHECKING BACKUP FOR BASOL GUNGOR")
print("=" * 80)

# Check backup
try:
    basol_backup = sb.table('customers_blaze_backup_20251106')\
        .select('member_id, first_name, last_name, phone, email, date_of_birth, total_visits, lifetime_value')\
        .ilike('first_name', 'basol')\
        .ilike('last_name', 'gungor')\
        .execute()
    
    if basol_backup.data:
        print(f"\nFound {len(basol_backup.data)} Basol Gungor in BACKUP:")
        for b in basol_backup.data:
            print(f"\n  ID: {b['member_id']}")
            print(f"  Name: {b['first_name']} {b['last_name']}")
            print(f"  Phone: {b.get('phone')}")
            print(f"  Email: {b.get('email')}")
            print(f"  DOB: {b.get('date_of_birth')}")
            print(f"  BACKUP Total Visits: {b.get('total_visits')}")
            print(f"  BACKUP Lifetime Value: ${b.get('lifetime_value', 0):.2f}")
        
        # Now check current
        basol_current = sb.table('customers_blaze')\
            .select('member_id, total_visits, lifetime_value')\
            .eq('member_id', basol_backup.data[0]['member_id'])\
            .execute()
        
        if basol_current.data:
            print(f"\n  CURRENT Total Visits: {basol_current.data[0].get('total_visits')}")
            print(f"  CURRENT Lifetime Value: ${basol_current.data[0].get('lifetime_value', 0):.2f}")
            
            if basol_backup.data[0].get('total_visits', 0) > 0 and basol_current.data[0].get('total_visits', 0) == 0:
                print(f"\n  >>> TRANSACTIONS WERE LOST IN MERGE! <<<")
                print(f"  >>> He HAD {basol_backup.data[0].get('total_visits')} visits BEFORE! <<<")
        
        # Check where his transactions went
        print(f"\n" + "=" * 80)
        print("CHECKING WHERE BASOL'S TRANSACTIONS WENT")
        print("=" * 80)
        
        # Check transactions_blaze for Basol's ID
        basol_tx = sb.table('transactions_blaze')\
            .select('transaction_id, customer_id, date, total_amount, blaze_status')\
            .eq('customer_id', basol_backup.data[0]['member_id'])\
            .execute()
        
        print(f"\nTransactions with Basol's customer_id ({basol_backup.data[0]['member_id']}):")
        print(f"  Found: {len(basol_tx.data)}")
        
        if len(basol_tx.data) == 0:
            print(f"\n  NO TRANSACTIONS FOUND!")
            print(f"  But backup shows he had {basol_backup.data[0].get('total_visits', 0)} visits!")
            print(f"\n  >>> TRANSACTIONS WERE MOVED SOMEWHERE ELSE! <<<")
            print(f"\n  Possible causes:")
            print(f"  1. Merge script moved them to a duplicate record")
            print(f"  2. Phone number conflict caused mis-assignment")
            print(f"  3. Database corruption during merge")
            
            # Try to find them by searching for transactions around that date
            print(f"\n  Searching for transactions that might be his...")
            print(f"  (Looking for transactions with phone (619) 368-3370 customers)")
            
            # Get all customer IDs with that phone
            phone_customers = sb.table('customers_blaze')\
                .select('member_id, first_name, last_name')\
                .eq('phone', '(619) 368-3370')\
                .execute()
            
            print(f"\n  Customers with phone (619) 368-3370:")
            for pc in phone_customers.data:
                tx_count = sb.table('transactions_blaze')\
                    .select('transaction_id', count='exact')\
                    .eq('customer_id', pc['member_id'])\
                    .eq('blaze_status', 'Completed')\
                    .execute()
                print(f"    - {pc['first_name']} {pc['last_name']}: {tx_count.count} transactions")
        else:
            print(f"  Transactions still exist:")
            for tx in basol_tx.data[:5]:
                print(f"    - {tx['date'][:10]}: ${tx['total_amount']:.2f} ({tx['blaze_status']})")
    
    else:
        print("\nNO BASOL GUNGOR FOUND IN BACKUP!")
        print("This means he was created AFTER the backup was made (Nov 6)")
        
except Exception as e:
    print(f"\nError checking backup: {e}")

print("\n" + "=" * 80)
print("USER IS RIGHT:")
print("=" * 80)
print("In your system, customers don't get created without transactions.")
print("If Basol has a customer record, his transactions MUST exist somewhere.")
print("They were either moved during merge or there's a deeper issue.")

