#!/usr/bin/env python3
"""
Blaze API → Supabase Transaction Sync (Production)
Uses UPSERT to prevent duplicates
"""
import requests
import json
from datetime import datetime, timedelta
from supabase import create_client
import time

# Blaze API Configuration
PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
DISPENSARY_KEY = "51a417aaba6e4ea4bed69b428d8d9cad"
BASE_URL = "https://api.stage.blaze.me"
API_VERSION = "v1"

# Supabase Configuration
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_transactions_from_blaze(start_date=None, end_date=None, limit=1000):
    """Fetch transactions from Blaze API"""
    url = f"{BASE_URL}/api/{API_VERSION}/partner/transactions"
    
    params = {'limit': limit}
    
    # Blaze expects MM/dd/yyyy format
    if start_date:
        params['startDate'] = start_date.strftime('%m/%d/%Y')
    if end_date:
        params['endDate'] = end_date.strftime('%m/%d/%Y')
    
    headers = {
        'partner_key': PARTNER_KEY,
        'Authorization': DISPENSARY_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Blaze API error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def upsert_transaction(transaction_data):
    """
    UPSERT transaction to Supabase
    Uses transaction_id as unique key - won't create duplicates
    """
    try:
        # Map Blaze data to Supabase schema
        supabase_data = {
            'transaction_id': transaction_data.get('id'),  # Unique key
            'customer_id': transaction_data.get('customerId'),
            'date': transaction_data.get('date'),
            'shop_location': transaction_data.get('shopLocation'),
            'staff_name': transaction_data.get('staffName'),
            'terminal': transaction_data.get('terminal'),
            'payment_type': transaction_data.get('paymentType'),
            'total_amount': transaction_data.get('totalAmount'),
            'total_tax': transaction_data.get('totalTax'),
            'discounts': transaction_data.get('discounts'),
            'blaze_status': transaction_data.get('status'),
            'trans_type': transaction_data.get('transType'),
            'raw_data': transaction_data,  # Store everything for reference
            'last_synced_at': datetime.now().isoformat(),
            'sync_status': 'synced'
        }
        
        # UPSERT: Insert if new, update if exists (based on transaction_id UNIQUE constraint)
        response = supabase.table('transactions_blaze').upsert(
            supabase_data,
            on_conflict='transaction_id'  # Use UNIQUE constraint
        ).execute()
        
        return response.data
        
    except Exception as e:
        print(f"❌ Failed to upsert transaction: {e}")
        return None

def upsert_transaction_items(transaction_id, items_data):
    """
    UPSERT transaction items to Supabase
    Uses (transaction_id, product_id, quantity, unit_price) as unique key
    """
    if not items_data:
        return
    
    try:
        for item in items_data:
            supabase_data = {
                'transaction_id': transaction_id,
                'product_id': item.get('productId'),
                'product_sku': item.get('sku'),
                'product_name': item.get('productName'),
                'brand': item.get('brand'),
                'category': item.get('category'),
                'quantity': item.get('quantity'),
                'unit_price': item.get('unitPrice'),
                'total_price': item.get('totalPrice'),
                'cost': item.get('cost'),
                'discount': item.get('discount'),
                'tax': item.get('tax'),
                'final_price': item.get('finalPrice'),
                'status': item.get('status'),
                'raw_data': item
            }
            
            # UPSERT: The UNIQUE index on (transaction_id, product_id, quantity, unit_price) prevents duplicates
            response = supabase.table('transaction_items_blaze').upsert(
                supabase_data
            ).execute()
            
    except Exception as e:
        print(f"❌ Failed to upsert transaction items: {e}")

def sync_transactions(days_back=7):
    """
    Main sync function
    Fetches last N days of transactions and UPSERTs to Supabase
    """
    print("="*70)
    print("BLAZE → SUPABASE TRANSACTION SYNC")
    print("="*70)
    
    # Fetch recent transactions
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"\n📅 Syncing transactions from:")
    print(f"   Start: {start_date.strftime('%Y-%m-%d')}")
    print(f"   End: {end_date.strftime('%Y-%m-%d')}")
    print()
    
    # Fetch from Blaze API
    print("🔄 Fetching from Blaze API...")
    data = get_transactions_from_blaze(start_date=start_date, end_date=end_date)
    
    if not data or 'values' not in data:
        print("❌ No transactions returned from Blaze")
        return
    
    transactions = data['values']
    print(f"✅ Found {len(transactions)} transactions from Blaze")
    
    # UPSERT to Supabase
    print("\n🔄 Upserting to Supabase...")
    synced_count = 0
    error_count = 0
    
    for i, trans in enumerate(transactions, 1):
        try:
            # UPSERT transaction
            result = upsert_transaction(trans)
            
            if result:
                # UPSERT transaction items
                if 'items' in trans:
                    upsert_transaction_items(trans['id'], trans['items'])
                
                synced_count += 1
                
                if i % 100 == 0:
                    print(f"   Progress: {i}/{len(transactions)} transactions")
            else:
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error syncing transaction {trans.get('id')}: {e}")
            error_count += 1
            continue
    
    print("\n" + "="*70)
    print("SYNC COMPLETE")
    print("="*70)
    print(f"✅ Synced: {synced_count} transactions")
    print(f"❌ Errors: {error_count}")
    print()

if __name__ == "__main__":
    import sys
    
    # Allow specifying days back as argument
    days = 7  # Default: last 7 days
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except:
            pass
    
    print(f"🚀 Starting sync (last {days} days)...")
    sync_transactions(days_back=days)

