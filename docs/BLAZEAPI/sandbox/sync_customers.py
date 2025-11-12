#!/usr/bin/env python3
"""
Blaze API Sandbox - Customer Sync Demo
Demonstrates incremental customer sync using modified dates
"""

import requests
import json
from datetime import datetime, timedelta
from config import *

def get_customers(last_sync_time=None, limit=100):
    """Fetch customers with modified date filtering"""
    url = f"{BASE_URL}/api/{API_VERSION}/partner/store/user"
    
    params = {'limit': limit}
    if last_sync_time:
        # Blaze uses modified_after parameter for incremental sync
        params['modified_after'] = last_sync_time.isoformat()
    
    headers = {
        'partner_key': PARTNER_KEY,
        'Authorization': DISPENSARY_KEY,
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching customers: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def sync_customers():
    """Main sync function - demonstrates Blaze rules compliance"""
    print("=" * 70)
    print("BLAZE API SANDBOX - CUSTOMER SYNC DEMO")
    print("=" * 70)
    
    # Simulate last sync time (1 hour ago)
    last_sync = datetime.now() - timedelta(hours=1)
    print(f"\nLast sync time: {last_sync.isoformat()}")
    print("Fetching customers modified since last sync...")
    
    # Fetch customers
    data = get_customers(last_sync_time=last_sync)
    
    if data:
        print(f"\nResponse keys: {list(data.keys())}")
        
        if 'values' in data:
            customers = data['values']
            print(f"Customers found: {len(customers)}")
            
            if len(customers) > 0:
                print(f"\nFirst customer keys: {list(customers[0].keys())}")
                print(f"\nSample customer data:")
                print(json.dumps(customers[0], indent=2)[:500])
        else:
            print("No 'values' key in response")
            print(f"Full response: {json.dumps(data, indent=2)}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    sync_customers()
