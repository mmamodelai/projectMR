#!/usr/bin/env python3
"""
Backfill Transaction Items from Blaze API
Start from Jan 1, 2024 → process in 7-day windows
Uses UPSERT to prevent duplicates
"""

import psycopg2
import time
import requests
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict
from supabase import create_client

# Blaze API Configuration
BLAZE_BASE_URL = "https://api.partners.blaze.me/api/v1"
PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
AUTH_KEY = "48f5dd5e57234145a233c79e66285925"

headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': AUTH_KEY,
    'Content-Type': 'application/json'
}

# Supabase Configuration
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Rate limiting - 2000 calls per 5 minutes (conservative)
MAX_CALLS_PER_5MIN = 2000
API_CALLS = []
API_CALL_WINDOW = 5 * 60  # 5 minutes in seconds


def check_rate_limit():
    """Check if we're approaching rate limit"""
    now = time.time()
    global API_CALLS
    API_CALLS = [call_time for call_time in API_CALLS if now - call_time < API_CALL_WINDOW]
    
    if len(API_CALLS) >= MAX_CALLS_PER_5MIN:
        oldest_call = min(API_CALLS)
        wait_time = API_CALL_WINDOW - (now - oldest_call) + 1
        if wait_time > 0:
            print(f"    Rate limit: {len(API_CALLS)}/{MAX_CALLS_PER_5MIN} calls. Waiting {wait_time:.0f}s...")
            time.sleep(wait_time)
            API_CALLS = [call_time for call_time in API_CALLS if time.time() - call_time < API_CALL_WINDOW]
    
    API_CALLS.append(now)


def format_date_for_blaze(date: datetime) -> str:
    """Format date as MM/dd/yyyy for Blaze API"""
    return date.strftime("%m/%d/%Y")


def fetch_transactions_for_window(start_date: datetime, end_date: datetime) -> List[Dict]:
    """Fetch all transactions in a 7-day window from Blaze API"""
    all_transactions = []
    skip = 0
    limit = 500
    
    start_str = format_date_for_blaze(start_date)
    end_str = format_date_for_blaze(end_date)
    
    print(f"  Fetching {start_str} to {end_str}...")
    
    while True:
        check_rate_limit()
        
        url = f"{BLAZE_BASE_URL}/partner/transactions?startDate={start_str}&endDate={end_str}&skip={skip}&limit={limit}"
        
        try:
            response = requests.get(url, headers=headers, timeout=60)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', '60'))
                print(f"    Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue
            
            if response.status_code != 200:
                print(f"    API error {response.status_code}: {response.text[:200]}")
                break
            
            data = response.json()
            transactions = data.get('values', [])
            
            if not transactions:
                break
            
            all_transactions.extend(transactions)
            actual_count = len(transactions)
            
            print(f"    Fetched {actual_count} transactions (skip={skip}, total={len(all_transactions)})")
            
            # API returns max 100 per page
            skip += actual_count
            
            if actual_count == 0:
                break
            
            time.sleep(0.1)  # 100ms delay
        
        except Exception as e:
            print(f"    Error: {e}")
            break
    
    return all_transactions


def upsert_transaction_items(transaction_id: str, items: List[Dict]) -> int:
    """UPSERT transaction items to Supabase"""
    if not items:
        return 0
    
    try:
        uploaded = 0
        for item in items:
            supabase_data = {
                'transaction_id': transaction_id,
                'product_id': item.get('productId'),
                'product_sku': item.get('productSku'),
                'product_name': item.get('productName'),
                'brand': item.get('brandName'),
                'category': item.get('categoryName'),
                'quantity': item.get('quantity'),
                'unit_price': item.get('unitPrice'),
                'total_price': item.get('totalPrice'),
                'cost': item.get('cost'),
                'discount': item.get('discount'),
                'tax': item.get('calcTax'),
                'final_price': item.get('finalPrice'),
                'status': item.get('status'),
                'raw_data': item
            }
            
            # UPSERT: Unique index prevents duplicates
            supabase.table('transaction_items_blaze').upsert(supabase_data).execute()
            uploaded += 1
        
        return uploaded
    except Exception as e:
        print(f"      Error upserting items for {transaction_id}: {str(e)[:200]}")
        return 0


def backfill_window(start_date: datetime, end_date: datetime) -> Dict:
    """Backfill items for all transactions in a 7-day window"""
    transactions = fetch_transactions_for_window(start_date, end_date)
    
    if not transactions:
        return {'transactions_processed': 0, 'items_uploaded': 0}
    
    print(f"  Processing {len(transactions):,} transactions...")
    
    total_items = 0
    transactions_processed = 0
    
    for txn in transactions:
        transaction_id = txn.get('id') or txn.get('transNo')
        
        if not transaction_id:
            continue
        
        # Extract items from cart
        cart = txn.get('cart', {})
        items = cart.get('items', [])
        
        if not items:
            continue
        
        # UPSERT items
        items_uploaded = upsert_transaction_items(transaction_id, items)
        
        if items_uploaded > 0:
            total_items += items_uploaded
            transactions_processed += 1
    
    return {
        'transactions_processed': transactions_processed,
        'items_uploaded': total_items
    }


def main():
    print("\n" + "=" * 70)
    print("TRANSACTION ITEMS BACKFILL - JAN 1, 2024 → NOW")
    print("=" * 70)
    print(f"Rate Limit: {MAX_CALLS_PER_5MIN:,} calls per 5 minutes")
    print(f"Using UPSERT (no duplicates)")
    print("=" * 70)
    print()
    
    # Process from Jan 1, 2024 to now in 7-day windows
    start_date = datetime(2024, 1, 1)
    end_date = datetime.now()
    current_date = start_date
    
    total_stats = {
        'transactions_processed': 0,
        'items_uploaded': 0,
        'windows_processed': 0
    }
    
    start_time = time.time()
    
    while current_date < end_date:
        window_start = current_date
        window_end = min(current_date + timedelta(days=7), end_date)
        
        print(f"\n{'='*70}")
        print(f"Window {total_stats['windows_processed'] + 1}: {window_start.strftime('%Y-%m-%d')} to {window_end.strftime('%Y-%m-%d')}")
        print(f"{'='*70}")
        
        stats = backfill_window(window_start, window_end)
        
        total_stats['transactions_processed'] += stats['transactions_processed']
        total_stats['items_uploaded'] += stats['items_uploaded']
        total_stats['windows_processed'] += 1
        
        print(f"\n  Window Results:")
        print(f"    Transactions: {stats['transactions_processed']}")
        print(f"    Items: {stats['items_uploaded']:,}")
        print(f"\n  Running Totals:")
        print(f"    Windows: {total_stats['windows_processed']}")
        print(f"    Transactions: {total_stats['transactions_processed']:,}")
        print(f"    Items: {total_stats['items_uploaded']:,}")
        
        current_date += timedelta(days=7)  # Move forward
        
        elapsed = time.time() - start_time
        rate = total_stats['transactions_processed'] / (elapsed / 60) if elapsed > 0 else 0
        print(f"\n  Progress:")
        print(f"    Time: {elapsed/60:.1f} minutes ({elapsed/3600:.2f} hours)")
        print(f"    Rate: {rate:.1f} transactions/minute")
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("BACKFILL COMPLETE!")
    print("=" * 70)
    print(f"Transactions processed: {total_stats['transactions_processed']:,}")
    print(f"Items uploaded: {total_stats['items_uploaded']:,}")
    print(f"Windows processed: {total_stats['windows_processed']}")
    print(f"Time: {elapsed/60:.1f} minutes ({elapsed/3600:.1f} hours)")
    print(f"Rate: {total_stats['transactions_processed'] / (elapsed / 60):.0f} transactions/minute")
    print("=" * 70)


if __name__ == "__main__":
    main()

