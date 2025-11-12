import supabase

sb = supabase.create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

print('Double-checking customer lookup...')
try:
    # First find by phone again
    phone_result = sb.table('customers_blaze').select('member_id, first_name, last_name, phone').eq('phone', '3239720353').execute()
    if phone_result.data:
        customer = phone_result.data[0]
        member_id = customer['member_id']
        print(f'Found by phone: {member_id}')
        print(f'Name from phone query: {customer["first_name"]} {customer["last_name"]}')

        # Now try to find by member_id
        id_result = sb.table('customers_blaze').select('first_name, last_name, phone').eq('member_id', member_id).execute()
        if id_result.data:
            print('Also found by member_id - good')
            cust = id_result.data[0]
            print(f'Name from ID query: {cust["first_name"]} {cust["last_name"]}')
        else:
            print('NOT found by member_id - this is the issue!')
    else:
        print('Customer not found by phone either')

except Exception as e:
    print(f'Error: {e}')

