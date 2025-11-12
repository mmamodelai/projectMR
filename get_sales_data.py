#!/usr/bin/env python3
"""
Sales Data Report Generator
Fetch sales data for specific dates from Blaze API database

Usage:
    python get_sales_data.py

Dates requested:
- Sept 25, 2025
- Oct 25, 2025
- Nov 1-5, 2025
- Dec 24, 2024
"""

from supabase import create_client, Client
from datetime import datetime
import pandas as pd
from tabulate import tabulate

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

# Target dates
TARGET_DATES = [
    '2024-12-24',  # Dec 24, 2024
    '2025-09-25',  # Sept 25, 2025
    '2025-10-25',  # Oct 25, 2025
    '2025-11-01',  # Nov 1, 2025
    '2025-11-02',  # Nov 2, 2025
    '2025-11-03',  # Nov 3, 2025
    '2025-11-04',  # Nov 4, 2025
    '2025-11-05',  # Nov 5, 2025
]

def get_sales_data():
    """Fetch sales data from Blaze database"""
    
    print("=" * 80)
    print("SALES DATA REPORT")
    print("=" * 80)
    print()
    
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Fetch transactions for target dates
    print("Fetching data from Blaze API database (transactions_blaze)...")
    print()
    
    results = []
    
    for date in TARGET_DATES:
        try:
            # Query transactions for this date
            response = supabase.rpc(
                'get_daily_sales_summary',
                {'target_date': date}
            ).execute()
            
            if response.data:
                results.append(response.data[0])
        except Exception as e:
            # If RPC doesn't exist, use direct query
            print(f"RPC not available, using direct query for {date}...")
            
            response = supabase.table('transactions_blaze') \
                .select('date, total_amount, total_tax, discounts, customer_id') \
                .gte('date', f'{date}T00:00:00') \
                .lte('date', f'{date}T23:59:59') \
                .eq('blaze_status', 'Completed') \
                .gt('total_amount', 0) \
                .execute()
            
            if response.data:
                transactions = response.data
                result = {
                    'date': date,
                    'transaction_count': len(transactions),
                    'gross_sales': sum(t['total_amount'] for t in transactions),
                    'total_tax': sum(t.get('total_tax', 0) or 0 for t in transactions),
                    'total_discounts': sum(t.get('discounts', 0) or 0 for t in transactions),
                    'unique_customers': len(set(t['customer_id'] for t in transactions if t.get('customer_id'))),
                    'avg_transaction': sum(t['total_amount'] for t in transactions) / len(transactions) if transactions else 0
                }
                results.append(result)
            else:
                results.append({
                    'date': date,
                    'transaction_count': 0,
                    'gross_sales': 0,
                    'total_tax': 0,
                    'total_discounts': 0,
                    'unique_customers': 0,
                    'avg_transaction': 0
                })
    
    # Display results
    if results:
        # Create DataFrame for better formatting
        df = pd.DataFrame(results)
        
        # Format currency columns
        currency_cols = ['gross_sales', 'total_tax', 'total_discounts', 'avg_transaction']
        for col in currency_cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"${x:,.2f}" if x else "$0.00")
        
        # Rename columns for display
        display_cols = {
            'date': 'Date',
            'transaction_count': 'Transactions',
            'gross_sales': 'Gross Sales',
            'total_tax': 'Tax',
            'total_discounts': 'Discounts',
            'unique_customers': 'Unique Customers',
            'avg_transaction': 'Avg Transaction'
        }
        df = df.rename(columns=display_cols)
        
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
        print()
        
        # Summary statistics
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print()
        
        # Calculate totals (from raw data)
        total_transactions = sum(r.get('transaction_count', 0) for r in results)
        total_gross = sum(r.get('gross_sales', 0) for r in results)
        total_tax = sum(r.get('total_tax', 0) for r in results)
        total_discounts = sum(r.get('total_discounts', 0) for r in results)
        
        print(f"Total Transactions: {total_transactions:,}")
        print(f"Total Gross Sales:  ${total_gross:,.2f}")
        print(f"Total Tax:          ${total_tax:,.2f}")
        print(f"Total Discounts:    ${total_discounts:,.2f}")
        print(f"Net Sales:          ${(total_gross - total_discounts):,.2f}")
        print()
        
        # Export to CSV
        csv_filename = f'sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(csv_filename, index=False)
        print(f"✅ Report saved to: {csv_filename}")
        print()
    else:
        print("❌ No data found for the specified dates")
        print()
    
    return results


def get_comparison_data():
    """Compare Blaze data vs CSV data"""
    
    print("=" * 80)
    print("DATA SOURCE COMPARISON (Blaze API vs CSV)")
    print("=" * 80)
    print()
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    comparison = []
    
    for date in TARGET_DATES:
        # Get Blaze data
        blaze_response = supabase.table('transactions_blaze') \
            .select('total_amount', count='exact') \
            .gte('date', f'{date}T00:00:00') \
            .lte('date', f'{date}T23:59:59') \
            .eq('blaze_status', 'Completed') \
            .gt('total_amount', 0) \
            .execute()
        
        blaze_count = blaze_response.count or 0
        blaze_total = sum(t.get('total_amount', 0) for t in blaze_response.data) if blaze_response.data else 0
        
        # Get CSV data
        csv_response = supabase.table('transactions') \
            .select('total_amount', count='exact') \
            .gte('date', f'{date}T00:00:00') \
            .lte('date', f'{date}T23:59:59') \
            .gt('total_amount', 0) \
            .execute()
        
        csv_count = csv_response.count or 0
        csv_total = sum(t.get('total_amount', 0) for t in csv_response.data) if csv_response.data else 0
        
        comparison.append({
            'date': date,
            'blaze_transactions': blaze_count,
            'csv_transactions': csv_count,
            'blaze_gross': f"${blaze_total:,.2f}",
            'csv_gross': f"${csv_total:,.2f}",
            'source': 'Blaze' if blaze_count > 0 else ('CSV' if csv_count > 0 else 'None')
        })
    
    if comparison:
        df = pd.DataFrame(comparison)
        df = df.rename(columns={
            'date': 'Date',
            'blaze_transactions': 'Blaze Txns',
            'csv_transactions': 'CSV Txns',
            'blaze_gross': 'Blaze Gross',
            'csv_gross': 'CSV Gross',
            'source': 'Best Source'
        })
        
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
        print()
        print("💡 Use 'Blaze' source for most complete/recent data")
        print()


if __name__ == "__main__":
    try:
        # Get main sales data
        results = get_sales_data()
        
        # Show comparison
        print()
        get_comparison_data()
        
        print("=" * 80)
        print("DONE!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()



