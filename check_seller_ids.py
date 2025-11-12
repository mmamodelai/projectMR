import supabase

sb = supabase.create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

print('Checking if seller_ids are numeric...')
try:
    # Get a few seller IDs
    result = sb.table('transactions_blaze').select('seller_id').neq('seller_id', None).limit(20).execute()

    numeric_ids = []
    mongo_ids = []

    for item in result.data:
        sid = item.get('seller_id')
        if sid:
            try:
                int(sid)
                numeric_ids.append(sid)
            except ValueError:
                mongo_ids.append(sid[:10] + '...')  # Truncate for display

    print(f'Numeric seller_ids: {numeric_ids[:5]}')
    print(f'MongoDB-style seller_ids: {mongo_ids[:5]}')

    # Check if numeric ones could match budtender ids
    if numeric_ids:
        print('\nChecking if numeric seller_ids match budtender ids...')
        for sid in numeric_ids[:3]:
            try:
                result = sb.table('budtenders').select('first_name, last_name').eq('id', int(sid)).execute()
                if result.data:
                    budtender = result.data[0]
                    print(f'Seller {sid} -> {budtender["first_name"]} {budtender["last_name"]}')
                else:
                    print(f'Seller {sid} -> No matching budtender')
            except Exception as e:
                print(f'Seller {sid} -> Error checking: {e}')

except Exception as e:
    print(f'Error: {e}')

