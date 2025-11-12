import supabase

sb = supabase.create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

print('Getting all unique seller_ids...')
try:
    result = sb.table('transactions_blaze').select('seller_id').neq('seller_id', None).execute()

    seller_ids = set()
    for item in result.data:
        sid = item.get('seller_id')
        if sid:
            seller_ids.add(sid)

    print(f'Total unique seller_ids: {len(seller_ids)}')
    print('\nFirst 10 seller_ids:')
    for sid in sorted(list(seller_ids))[:10]:
        print(f'  {sid}')

    # Check if any are numeric
    numeric = [sid for sid in seller_ids if sid.isdigit()]
    print(f'\nNumeric seller_ids: {numeric}')

    if numeric:
        print('\nTrying to match numeric IDs to budtenders...')
        for sid in numeric[:5]:
            try:
                result = sb.table('budtenders').select('first_name, last_name').eq('id', int(sid)).execute()
                if result.data:
                    budtender = result.data[0]
                    print(f'Seller {sid} -> {budtender["first_name"]} {budtender["last_name"]}')
                else:
                    print(f'Seller {sid} -> No matching budtender')
            except Exception as e:
                print(f'Seller {sid} -> Error: {e}')

except Exception as e:
    print(f'Error: {e}')

