import supabase

sb = supabase.create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

print('Analyzing seller_id patterns...')
try:
    # Get sample seller IDs
    result = sb.table('transactions_blaze').select('seller_id').neq('seller_id', None).limit(50).execute()

    seller_ids = []
    for item in result.data:
        sid = item.get('seller_id')
        if sid:
            seller_ids.append(sid)

    print(f'Found {len(seller_ids)} seller_ids')
    print('\nSample seller_ids:')
    for i, sid in enumerate(seller_ids[:10]):
        print(f'  {i+1}. {sid} (len={len(sid)})')

    # Check for patterns
    print('\nAnalyzing patterns:')
    print(f'  All are 24 chars (MongoDB ObjectId): {all(len(sid) == 24 for sid in seller_ids)}')
    print(f'  All are hex: {all(all(c in "0123456789abcdef" for c in sid.lower()) for sid in seller_ids)}')

    # Look for the specific one the user mentioned
    target = "6096c37abebf144f90cb0a5a"
    if target in seller_ids:
        print(f'\nFOUND: Seller ID {target} exists in transactions!')
    else:
        print(f'\nSeller ID {target} not found in sample')

    # Check if any seller_ids could be interpreted as numeric
    numeric_parts = []
    for sid in seller_ids:
        # Try extracting numeric parts
        import re
        numbers = re.findall(r'\d+', sid)
        if numbers:
            numeric_parts.extend(numbers)

    if numeric_parts:
        print(f'\nPossible numeric parts found: {numeric_parts[:10]}')
        # Check if these could match budtender IDs
        for num in numeric_parts[:5]:
            try:
                num_int = int(num)
                if 1 <= num_int <= 10000:  # Reasonable ID range
                    result = sb.table('budtenders').select('first_name, last_name').eq('id', num_int).execute()
                    if result.data:
                        print(f'  Numeric {num} -> {result.data[0]["first_name"]} {result.data[0]["last_name"]}')
            except:
                pass

except Exception as e:
    print(f'Error: {e}')

