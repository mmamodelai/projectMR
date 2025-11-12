#!/usr/bin/env python3
"""
Check Most Recent Data in Database
"""

from supabase import create_client, Client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("CHECKING MOST RECENT DATA")
print("=" * 80)
print()

# Check most recent transactions
print("Most recent transactions in transactions_blaze:")
recent_trans = supabase.table('transactions_blaze') \
    .select('transaction_id, customer_id, date, total_amount') \
    .order('date', desc=True) \
    .limit(10) \
    .execute()

if recent_trans.data:
    for t in recent_trans.data:
        print(f"  {t['date'][:10]} | ${t['total_amount']:.2f}")
    
    latest_date = recent_trans.data[0]['date'][:10]
    print(f"\nLatest transaction date: {latest_date}")
else:
    print("  No transactions found!")

print()

# Check customers with most recent last_visited dates
print("Customers with most recent last_visited dates:")
recent_custs = supabase.table('customers_blaze') \
    .select('member_id, name, last_visited') \
    .not_.is_('last_visited', 'null') \
    .order('last_visited', desc=True) \
    .limit(10) \
    .execute()

if recent_custs.data:
    dates_seen = set()
    for c in recent_custs.data:
        last_visit = c.get('last_visited')
        if last_visit:
            dates_seen.add(last_visit[:10] if isinstance(last_visit, str) else str(last_visit)[:10])
            print(f"  {c.get('name', 'N/A')[:30]:<30} | {last_visit[:10] if isinstance(last_visit, str) else last_visit}")
    
    print(f"\nUnique dates in top 10: {sorted(dates_seen, reverse=True)}")
else:
    print("  No customers found!")

print()
print("=" * 80)
print("DIAGNOSIS")
print("=" * 80)

if recent_trans.data:
    trans_date = recent_trans.data[0]['date'][:10]
    if recent_custs.data:
        cust_date = recent_custs.data[0]['last_visited'][:10] if isinstance(recent_custs.data[0]['last_visited'], str) else str(recent_custs.data[0]['last_visited'])[:10]
        
        print(f"\nLatest transaction: {trans_date}")
        print(f"Latest customer visit: {cust_date}")
        
        if trans_date > cust_date:
            print(f"\nPROBLEM: Customers' last_visited is not updated!")
            print(f"  Transactions go to {trans_date}")
            print(f"  But customers only show {cust_date}")
            print(f"\nSOLUTION: Need to update customers.last_visited from transactions")
        elif trans_date == cust_date:
            print(f"\nDATA IS SYNCED: Both show {trans_date}")
            print(f"The viewer is correctly showing the most recent customers.")
        else:
            print(f"\nWeird: Customer date is newer than transactions?")

print("=" * 80)

