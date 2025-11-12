from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

params = {
    'filter_email': False,
    'filter_phone': False,
    'days_cutoff': None,
    'search_term': None
}

print("Querying get_customers_fast with params:", params)
res = sb.rpc('get_customers_fast', params).execute()
print("Total customers returned:", len(res.data))
print("Sample:")
for row in res.data[:5]:
    print(row['member_id'], row['first_name'], row['last_name'], row.get('phone'))

search = 'stephen clare'
params['search_term'] = search
res = sb.rpc('get_customers_fast', params).execute()
print(f"\nSearch '{search}' -> {len(res.data)} results")
for row in res.data:
    print(row['member_id'], row['first_name'], row['last_name'], row.get('phone'), row.get('total_visits'))


