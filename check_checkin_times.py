#!/usr/bin/env python3
"""
Check Customer Check-In Times
Shows when customers checked in vs when they completed their purchases
"""

import os
from supabase import create_client, Client
from datetime import datetime, timedelta
import pytz

# Initialize Supabase
url = os.environ.get("SUPABASE_URL", "https://kiwmwoqrguyrcpjytgte.supabase.co")
key = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyODkyNzY4NCwiZXhwIjoyMDQ0NTAzNjg0fQ.O2prfiL0qB8tpqmLa1Qyo4LZWR0j4BW4U7oOV9Y1VFI")
supabase: Client = create_client(url, key)

print("=" * 80)
print("CUSTOMER CHECK-IN TIMES ANALYSIS")
print("=" * 80)
print()

# Get recent transactions with timing data
print("Fetching recent transactions with check-in times...")
response = supabase.table('transactions_blaze') \
    .select('transaction_id, customer_id, start_time, end_time, total_amount, date') \
    .not_.is_('start_time', 'null') \
    .not_.is_('end_time', 'null') \
    .order('date', desc=True) \
    .limit(20) \
    .execute()

transactions = response.data

if not transactions:
    print("No transactions with timing data found")
    exit(0)

print(f"Found {len(transactions)} recent transactions with timing data\n")

# Pacific timezone
pacific = pytz.timezone('America/Los_Angeles')

print("=" * 80)
print("RECENT CUSTOMER CHECK-INS")
print("=" * 80)
print(f"{'Date':<12} {'Check-In':<10} {'Check-Out':<10} {'Wait':<8} {'Amount':<10} {'Customer ID'}")
print("-" * 80)

wait_times = []

for txn in transactions:
    # Parse timestamps
    start = datetime.fromisoformat(txn['start_time'].replace('Z', '+00:00'))
    end = datetime.fromisoformat(txn['end_time'].replace('Z', '+00:00'))
    
    # Convert to Pacific time
    start_pacific = start.astimezone(pacific)
    end_pacific = end.astimezone(pacific)
    
    # Calculate wait time in minutes
    wait_minutes = (end - start).total_seconds() / 60.0
    wait_times.append(wait_minutes)
    
    # Format output
    date_str = start_pacific.strftime('%m/%d/%Y')
    checkin_str = start_pacific.strftime('%I:%M %p')
    checkout_str = end_pacific.strftime('%I:%M %p')
    wait_str = f"{wait_minutes:.1f}m"
    amount_str = f"${txn['total_amount']:.2f}"
    customer = txn['customer_id'][:12] + "..." if txn['customer_id'] and len(txn['customer_id']) > 12 else txn['customer_id'] or "N/A"
    
    print(f"{date_str:<12} {checkin_str:<10} {checkout_str:<10} {wait_str:<8} {amount_str:<10} {customer}")

# Statistics
print("-" * 80)
print("\nWAIT TIME STATISTICS (from these {0} transactions)".format(len(wait_times)))
print("-" * 40)
print(f"  Fastest:  {min(wait_times):.1f} minutes")
print(f"  Slowest:  {max(wait_times):.1f} minutes")
print(f"  Average:  {sum(wait_times)/len(wait_times):.1f} minutes")
print(f"  Median:   {sorted(wait_times)[len(wait_times)//2]:.1f} minutes")
print()

# Get overall stats for last 7 days
print("=" * 80)
print("OVERALL STATS (LAST 7 DAYS)")
print("=" * 80)

seven_days_ago = (datetime.now(pacific) - timedelta(days=7)).isoformat()

response = supabase.rpc('get_wait_time_stats', {
    'start_date': seven_days_ago[:10],
    'end_date': datetime.now(pacific).isoformat()[:10]
}).execute()

if response.data and len(response.data) > 0:
    stats = response.data[0]
    print(f"  Total Transactions: {stats['transactions_with_wait_time']}")
    print(f"  Fastest:  {stats['fastest_minutes']:.2f} minutes")
    print(f"  Slowest:  {stats['slowest_minutes']:.2f} minutes")
    print(f"  Average:  {stats['avg_minutes']:.2f} minutes")
    print(f"  Median:   {stats['median_minutes']:.2f} minutes")
    print(f"  75th %ile: {stats['p75_minutes']:.2f} minutes")
    print(f"  95th %ile: {stats['p95_minutes']:.2f} minutes")

print()
print("=" * 80)
print("YES - We track customer check-in times!")
print("=" * 80)
print()
print("AVAILABLE DATA:")
print("  - start_time  - When customer checked in")
print("  - end_time    - When transaction completed")
print("  - date        - Transaction date")
print("  - customer_id - Customer identifier")
print()
print("AVAILABLE VIEWS/FUNCTIONS:")
print("  - get_wait_time_stats(start_date, end_date) - Custom date range stats")
print("  - wait_time_stats_today - Today's wait time stats")
print("  - wait_time_by_hour - Wait times by hour of day")
print()
print("Documentation: blaze-api-sync/WAIT_TIME_STATS.md")
print("=" * 80)

