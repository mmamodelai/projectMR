#!/usr/bin/env python3
"""Test baseball card calculation to see what's failing"""

from supabase import create_client, Client
from collections import Counter, defaultdict
from datetime import datetime

# Supabase credentials
CRM_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
CRM_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

crm_supabase = create_client(CRM_URL, CRM_KEY)

def test_luis_card():
    """Test loading Luis Bobadilla's baseball card"""
    print("Testing baseball card for Luis Bobadilla (+16193683370)...")
    
    # 1. Find Luis
    phone_10 = "6193683370"
    result = crm_supabase.table('customers_blaze').select('*').like('phone', f'%{phone_10}').execute()
    
    if not result.data:
        print("[ERROR] Could not find Luis in customers_blaze!")
        return
    
    customer = result.data[0]
    print(f"[OK] Found customer: {customer.get('name')} (member_id: {customer.get('member_id')})")
    
    # 2. Get transactions
    member_id = customer.get('member_id')
    print(f"\n[QUERY] Querying transactions for member_id: {member_id}")
    
    trans_result = crm_supabase.table('transactions').select('*').eq('customer_id', member_id).order('date', desc=True).execute()
    transactions = trans_result.data if trans_result.data else []
    
    print(f"[OK] Found {len(transactions)} transactions")
    
    if len(transactions) == 0:
        print("[WARNING] No transactions found! This is why baseball card fails.")
        return
    
    # 3. Get transaction items
    transaction_ids = [t['transaction_id'] for t in transactions]
    print(f"\n[QUERY] Querying transaction_items for {len(transaction_ids)} transactions...")
    
    items_result = crm_supabase.table('transaction_items').select('*').in_('transaction_id', transaction_ids).execute()
    items = items_result.data if items_result.data else []
    
    print(f"[OK] Found {len(items)} items")
    
    # 4. Calculate metrics
    print("\n[METRICS] Calculating metrics...")
    
    total_visits = len(transactions)
    total_revenue = sum(float(t.get('total_amount', 0)) for t in transactions)
    avg_revenue_per_visit = total_revenue / total_visits if total_visits > 0 else 0
    
    print(f"   Total Visits: {total_visits}")
    print(f"   Total Revenue: ${total_revenue:,.2f}")
    print(f"   Avg per Visit: ${avg_revenue_per_visit:.2f}")
    
    # Top brands
    brand_revenue = defaultdict(float)
    for item in items:
        brand = item.get('brand', 'Unknown')
        revenue = float(item.get('total_price', 0))
        brand_revenue[brand] += revenue
    
    top_brands = sorted(brand_revenue.items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"\n[TOP BRANDS]:")
    for brand, revenue in top_brands:
        print(f"   - {brand}: ${revenue:.2f}")
    
    print("\n[SUCCESS] Baseball card calculation SUCCESS!")

if __name__ == "__main__":
    try:
        test_luis_card()
    except Exception as e:
        import traceback
        print(f"\n[ERROR] {e}")
        print(traceback.format_exc())

