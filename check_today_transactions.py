import supabase
from datetime import datetime, timedelta

sb = supabase.create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

print('Checking recent transactions...')
print('=' * 50)

try:
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime('%Y-%m-%d')
    print(f'Today is: {today}')

    # Get transactions from today
    result = sb.table('transactions_blaze').select('transaction_id, customer_id, total_amount, created_at, seller_id').gte('created_at', f'{today}T00:00:00').order('created_at', desc=True).execute()

    if result.data:
        print(f'\nFound {len(result.data)} transactions today:')
        total_sales = 0

        for i, trans in enumerate(result.data[:10]):  # Show first 10
            amount = trans.get('total_amount', 0)
            total_sales += amount
            created = trans.get('created_at', 'Unknown')
            customer_id = trans.get('customer_id', 'Unknown')
            seller_id = trans.get('seller_id', 'Unknown')

            print(f'{i+1:2d}. ${amount:6.2f} | {created[11:19] if created != "Unknown" else "Unknown":8} | Seller: {seller_id[:10]}...')

        print(f'\nTotal sales today: ${total_sales:.2f}')

        if len(result.data) > 10:
            print(f'... and {len(result.data) - 10} more transactions')
    else:
        print('\nNo transactions found for today yet.')

    # Also check yesterday for comparison
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_result = sb.table('transactions_blaze').select('count', count='exact').gte('created_at', f'{yesterday}T00:00:00').lt('created_at', f'{today}T00:00:00').execute()

    print(f'\nFor comparison - Yesterday had {yesterday_result.count} transactions')

except Exception as e:
    print(f'Error: {e}')

