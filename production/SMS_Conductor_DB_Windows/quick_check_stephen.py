from supabase import create_client
import json

sb = create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

# Get customer
c = sb.table('customers').select('*').eq('phone', '+16199773020').execute()
customer = c.data[0]
member_id = customer['member_id']

print(f"Customer: {customer['name']}")
print(f"Member ID: {member_id}")
print(f"ID: {customer['id']}")

# Try transactions by member_id (as customer_id)
print(f"\nChecking transactions by customer_id = member_id...")
t = sb.table('transactions').select('*').eq('customer_id', member_id).limit(5).execute()
print(f"Found {len(t.data)} transactions")
if t.data:
    for tx in t.data[:3]:
        print(f"  - Trans {tx['transaction_id']}: ${tx['total']} on {tx['date']}")

