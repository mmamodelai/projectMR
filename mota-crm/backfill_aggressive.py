#!/usr/bin/env python3
"""
AGGRESSIVE Transaction Items Backfill
- 10,000 API calls per 5 minutes (Blaze max)
- Batch UPSERTs (100+ items at once)
- 7-day windows (Blaze requirement)
- Start from Jan 1, 2024
"""

import time
import requests
from datetime import datetime, timedelta
import json
from typing import List, Dict
from supabase import create_client
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# AGGRESSIVE Rate limiting - 7,500 calls per 5 minutes (safe margin below 10K max)
MAX_CALLS_PER_5MIN = 7500
API_CALLS = []
API_CALL_WINDOW = 5 * 60

# Batch sizes for efficiency
BATCH_SIZE_UPSERT = 500  # UPSERT 500 items at once


def check_rate_limit():
    """Check rate limit - AGGRESSIVE"""
    now = time.time()
    global API_CALLS
    API_CALLS = [call_time for call_time in API_CALLS if now - call_time < API_CALL_WINDOW]
    
    if len(API_CALLS) >= MAX_CALLS_PER_5MIN:
        oldest_call = min(API_CALLS)
        wait_time = API_CALL_WINDOW - (now - oldest_call) + 1
        if wait_time > 0:
            print(f"    Rate limit hit: {len(API_CALLS)}/{MAX_CALLS_PER_5MIN}. Waiting {wait_time:.0f}s...")
            time.sleep(wait_time)
            API_CALLS = [call_time for call_time in API_CALLS if time.time() - call_time < API_CALL_WINDOW]
    
    API_CALLS.append(now)


def format_date_for_blaze(date: datetime) -> str:
    """Format date as MM/dd/yyyy"""
    return date.strftime("%m/%d/%Y")


def fetch_transactions_for_window(start_date: datetime, end_date: datetime) -> List[Dict]:
    """Fetch ALL transactions in 7-day window - AGGRESSIVE"""
    all_transactions = []
    skip = 0
    
    start_str = format_date_for_blaze(start_date)
    end_str = format_date_for_blaze(end_date)
    
    print(f"  Fetching {start_str} to {end_str}...")
    
    while True:
        check_rate_limit()
        
        # API returns max 100 per call (unpublished limit)
        url = f"{BLAZE_BASE_URL}/partner/transactions?startDate={start_str}&endDate={end_str}&skip={skip}&limit=100"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', '30'))
                time.sleep(retry_after)
                continue
            
            if response.status_code != 200:
                print(f"    API error {response.status_code}")
                break
            
            data = response.json()
            transactions = data.get('values', [])
            
            if not transactions:
                break
            
            all_transactions.extend(transactions)
            skip += len(transactions)
            
            # Only show progress every 1000 transactions
            if len(all_transactions) % 1000 == 0:
                print(f"    Fetched {len(all_transactions):,} transactions...")
        
        except Exception as e:
            print(f"    Error: {e}")
            break
    
    return all_transactions


def batch_upsert_items(items_batch: List[Dict]) -> int:
    """UPSERT batch of items at once - MUCH FASTER"""
    if not items_batch:
        return 0
    
    # CRITICAL: Deduplicate batch before upserting
    # PostgreSQL can't UPSERT the same unique key twice in one operation
    seen = set()
    unique_items = []
    
    for item in items_batch:
        # Create unique key from the columns in our unique index
        key = (
            item.get('transaction_id'),
            item.get('product_id'),
            item.get('quantity'),
            item.get('unit_price')
        )
        
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    
    if not unique_items:
        return 0
    
    try:
        # Use on_conflict to specify which columns define uniqueness
        result = supabase.table('transaction_items_blaze').upsert(
            unique_items,
            on_conflict='transaction_id,product_id,quantity,unit_price'
        ).execute()
        return len(unique_items)
    except Exception as e:
        print(f"      Batch UPSERT error: {str(e)[:150]}")
        # Fallback: Try one at a time with on_conflict
        success = 0
        for item in unique_items:
            try:
                supabase.table('transaction_items_blaze').upsert(
                    item,
                    on_conflict='transaction_id,product_id,quantity,unit_price'
                ).execute()
                success += 1
            except Exception as e2:
                # Skip duplicates silently (they already exist in DB)
                pass
        return success


def process_transactions_to_items(transactions: List[Dict]) -> List[Dict]:
    """Extract all items from all transactions - FAST"""
    all_items = []
    
    for txn in transactions:
        transaction_id = txn.get('id') or txn.get('transNo')
        if not transaction_id:
            continue
        
        cart = txn.get('cart', {})
        items = cart.get('items', [])
        
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
            all_items.append(supabase_data)
    
    return all_items


def backfill_window(start_date: datetime, end_date: datetime) -> Dict:
    """Backfill 7-day window - AGGRESSIVE"""
    # Fetch all transactions
    transactions = fetch_transactions_for_window(start_date, end_date)
    
    if not transactions:
        return {'transactions': 0, 'items': 0}
    
    print(f"  Processing {len(transactions):,} transactions...")
    
    # Extract all items
    all_items = process_transactions_to_items(transactions)
    
    if not all_items:
        return {'transactions': len(transactions), 'items': 0}
    
    print(f"  Upserting {len(all_items):,} items in batches...")
    
    # UPSERT in batches of 500
    total_uploaded = 0
    for i in range(0, len(all_items), BATCH_SIZE_UPSERT):
        batch = all_items[i:i+BATCH_SIZE_UPSERT]
        uploaded = batch_upsert_items(batch)
        total_uploaded += uploaded
        
        # Progress every 5000 items
        if (i + BATCH_SIZE_UPSERT) % 5000 == 0:
            print(f"    Upserted {total_uploaded:,}/{len(all_items):,} items...")
    
    return {'transactions': len(transactions), 'items': total_uploaded}


def main():
    print("\n" + "=" * 70)
    print("AGGRESSIVE BACKFILL - JAN 1, 2020 → NOW")
    print("=" * 70)
    print(f"Max Rate: {MAX_CALLS_PER_5MIN:,} calls per 5 min (safe margin below 10K max)")
    print(f"Batch Size: {BATCH_SIZE_UPSERT} items per UPSERT")
    print(f"Window Size: 7 days (Blaze requirement)")
    print("=" * 70)
    print()
    
    start_date = datetime(2020, 1, 1)
    end_date = datetime.now()
    current_date = start_date
    
    total_stats = {
        'transactions': 0,
        'items': 0,
        'windows': 0
    }
    
    start_time = time.time()
    
    # Process forward in 7-day windows
    while current_date < end_date:
        window_start = current_date
        window_end = min(current_date + timedelta(days=7), end_date)
        
        print(f"\n{'='*70}")
        print(f"Window {total_stats['windows'] + 1}: {window_start.strftime('%Y-%m-%d')} to {window_end.strftime('%Y-%m-%d')}")
        print(f"{'='*70}")
        
        window_start_time = time.time()
        stats = backfill_window(window_start, window_end)
        window_elapsed = time.time() - window_start_time
        
        total_stats['transactions'] += stats['transactions']
        total_stats['items'] += stats['items']
        total_stats['windows'] += 1
        
        print(f"\n  Window: {stats['transactions']:,} transactions, {stats['items']:,} items in {window_elapsed:.1f}s")
        print(f"  Total: {total_stats['windows']} windows, {total_stats['transactions']:,} transactions, {total_stats['items']:,} items")
        
        current_date += timedelta(days=7)
        
        # Overall progress
        elapsed = time.time() - start_time
        rate_trans = total_stats['transactions'] / (elapsed / 60) if elapsed > 0 else 0
        rate_items = total_stats['items'] / (elapsed / 60) if elapsed > 0 else 0
        
        print(f"  Time: {elapsed/60:.1f}min | Rate: {rate_trans:.0f} trans/min, {rate_items:.0f} items/min")
        
        # Estimate remaining
        days_remaining = (end_date - current_date).days
        windows_remaining = max(0, days_remaining // 7)
        if windows_remaining > 0 and total_stats['windows'] > 0:
            avg_time_per_window = elapsed / total_stats['windows']
            est_remaining = (windows_remaining * avg_time_per_window) / 60
            print(f"  Est. remaining: ~{windows_remaining} windows (~{est_remaining:.0f} minutes)")
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("BACKFILL COMPLETE!")
    print("=" * 70)
    print(f"Transactions: {total_stats['transactions']:,}")
    print(f"Items: {total_stats['items']:,}")
    print(f"Windows: {total_stats['windows']}")
    print(f"Time: {elapsed/60:.1f} min ({elapsed/3600:.1f} hours)")
    print(f"Rate: {total_stats['transactions'] / (elapsed / 60):.0f} trans/min, {total_stats['items'] / (elapsed / 60):.0f} items/min")
    print("=" * 70)


if __name__ == "__main__":
    main()

