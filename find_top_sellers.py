#!/usr/bin/env python3
"""
Find Top Sellers to Map
Shows the most active seller_ids so you can map them to names
"""

import supabase

sb = supabase.create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

print("Finding top seller_ids by transaction count...")
print("=" * 60)

try:
    # Get top sellers
    result = sb.table('transactions_blaze').select('seller_id, total_amount').neq('seller_id', None).execute()

    seller_stats = {}
    for item in result.data:
        sid = item.get('seller_id')
        amount = item.get('total_amount', 0)
        if sid:
            if sid not in seller_stats:
                seller_stats[sid] = {'count': 0, 'total': 0}
            seller_stats[sid]['count'] += 1
            seller_stats[sid]['total'] += amount

    # Sort by transaction count
    top_sellers = sorted(seller_stats.items(), key=lambda x: x[1]['count'], reverse=True)

    print("Top Seller IDs (by transaction count):")
    print("Seller ID                    | Transactions | Total Sales")
    print("-" * 60)

    for seller_id, stats in top_sellers[:15]:  # Top 15
        count = stats['count']
        total = stats['total']
        # Truncate seller_id for display
        display_id = seller_id[:20] + "..." if len(seller_id) > 20 else seller_id
        print(f"{display_id:<25} | {count:>11} | ${total:>10.2f}")

    print("\nTo map these to names, use SQL like:")
    print("UPDATE sellers_blaze SET seller_name = 'Staff Name' WHERE seller_id = '6096c37abebf144f90cb0a5a';")

    print(f"\nTotal unique seller_ids: {len(seller_stats)}")

except Exception as e:
    print(f"Error: {e}")
    print("\nIf this times out, the table is very large. Use the SQL script instead.")
