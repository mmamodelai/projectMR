#!/usr/bin/env python3
"""
Blaze API Sandbox - Transaction Sync Demo
Demonstrates batch transaction sync following Blaze rules
"""

import requests
import json
from datetime import datetime, timedelta
from config import *

def get_transactions(start_date=None, end_date=None, limit=100):
    """Fetch transactions with date range filtering"""
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
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching transactions: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def sync_transactions():
    """Main sync function - demonstrates Blaze rules compliance"""
    print("=" * 70)
    print("BLAZE API SANDBOX - TRANSACTION SYNC DEMO")
    print("=" * 70)
    
    # Blaze rule: Fetching historical transactions shall be done hourly or nightly
    # Let's fetch last 24 hours as example
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=24)
    
    print(f"\nFetching transactions from:")
    print(f"  Start: {start_date.isoformat()}")
    print(f"  End: {end_date.isoformat()}")
    
    # Fetch transactions
    data = get_transactions(start_date=start_date, end_date=end_date)
    
    if data:
        print(f"\nResponse keys: {list(data.keys())}")
        
        if 'values' in data:
            transactions = data['values']
            print(f"Transactions found: {len(transactions)}")
            
            if len(transactions) > 0:
                print(f"\nFirst transaction keys: {list(transactions[0].keys())}")
                print(f"\nSample transaction data:")
                print(json.dumps(transactions[0], indent=2)[:500])
        else:
            print("No 'values' key in response")
            print(f"Full response: {json.dumps(data, indent=2)}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    sync_transactions()
