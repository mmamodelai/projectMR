import supabase

sb = supabase.create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

print('Investigating customer: 323-972-0353')
print('=' * 50)

# Find the customer
try:
    # Try different phone formats
    phone_formats = ['3239720353', '323-972-0353', '(323) 972-0353', '+13239720353']

    customer = None
    for phone in phone_formats:
        result = sb.table('customers_blaze').select('*').eq('phone', phone).execute()
        if result.data:
            customer = result.data[0]
            print(f'Customer found with phone format: {phone}')
            break

    if not customer:
        print('Customer not found with any phone format')
        # Search for similar phones
        print('Searching for similar phones...')
        similar_result = sb.table('customers_blaze').select('first_name, last_name, phone, member_id').ilike('phone', '%323972%').execute()
        if similar_result.data:
            print('Similar phones found:')
            for cust in similar_result.data[:5]:
                print(f'  {cust["first_name"]} {cust["last_name"]} - {cust["phone"]} - ID: {cust["member_id"]}')
        exit()

    print(f'Customer: {customer["first_name"]} {customer["last_name"]}')
    print(f'Member ID: {customer["member_id"]}')
    print(f'Phone: {customer["phone"]}')
    print()

    # Get their transactions
    member_id = customer['member_id']
    trans_result = sb.table('transactions_blaze').select('transaction_id, seller_id, total_amount, created_at').eq('customer_id', member_id).execute()

    if trans_result.data:
        print(f'Found {len(trans_result.data)} transactions:')
        for i, trans in enumerate(trans_result.data[:5]):  # Show first 5
            seller_id = trans.get('seller_id', 'None')
            amount = trans.get('total_amount', 0)
            created = trans.get('created_at', 'Unknown')[:10] if trans.get('created_at') else 'Unknown'
            print(f'  {i+1}. Seller ID: {seller_id}, Amount: ${amount}, Date: {created}')

            # Check what this seller_id resolves to
            if seller_id and seller_id != 'None':
                try:
                    emp_result = sb.table('employees_blaze').select('name, first_name, last_name').eq('employee_id', seller_id).execute()
                    if emp_result.data:
                        emp = emp_result.data[0]
                        first_name = emp.get('first_name', 'None')
                        last_name = emp.get('last_name', 'None')
                        full_name = emp.get('name', 'None')
                        print(f'      -> Employee: {full_name} (First: {first_name}, Last: {last_name})')
                    else:
                        print(f'      -> Employee not found in employees_blaze table')
                except Exception as e:
                    print(f'      -> Error checking employee: {e}')
            print()
    else:
        print('No transactions found for this customer')

except Exception as e:
    print(f'Error: {e}')

