import supabase

sb = supabase.create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

print('Checking staff table...')
try:
    result = sb.table('staff').select('*').limit(10).execute()
    if result.data:
        print('Staff table contents:')
        for i, staff in enumerate(result.data[:5]):
            staff_id = staff.get('id')
            staff_name = staff.get('staff_name')
            shop = staff.get('shop_location')
            print(f'  {i+1}. ID: {staff_id}, Name: {staff_name}, Shop: {shop}')

        print(f'\nTotal staff records shown: {len(result.data)}')

        # Check if staff.id might match seller_id somehow
        print('\nChecking if staff IDs match seller patterns...')
        staff_ids = [str(staff.get('id')) for staff in result.data]
        print(f'Staff IDs: {staff_ids}')

        # Check if any staff IDs could match seller IDs
        print('\nTesting if staff IDs exist as seller_ids in transactions...')
        for staff_id in staff_ids[:3]:
            try:
                trans_result = sb.table('transactions_blaze').select('seller_id').eq('seller_id', staff_id).limit(1).execute()
                if trans_result.data:
                    print(f'  Staff ID {staff_id} found in transactions!')
                else:
                    print(f'  Staff ID {staff_id} not found in transactions')
            except Exception as e:
                print(f'  Error checking staff ID {staff_id}: {e}')

except Exception as e:
    print(f'Error: {e}')

