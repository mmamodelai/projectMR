#!/usr/bin/env python3
"""
Blaze API Sandbox - Product Sync Demo
Demonstrates product sync with modified date filtering
"""

import requests
import json
from datetime import datetime, timedelta
from config import *

def get_products(modified_after=None, limit=100):
    """Fetch products with modified date filtering"""
    url = f"{BASE_URL}/api/{API_VERSION}/partner/products/modified"
    
    params = {'limit': limit}
    
    # Convert to Unix timestamp if provided
    if modified_after:
        params['startDate'] = int(modified_after.timestamp() * 1000)
    
    headers = {
        'partner_key': PARTNER_KEY,
        'Authorization': DISPENSARY_KEY,
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching products: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def sync_products():
    """Main sync function - demonstrates Blaze rules compliance"""
    print("=" * 70)
    print("BLAZE API SANDBOX - PRODUCT SYNC DEMO")
    print("=" * 70)
    
    # Blaze rule: Fetching inventory shall be done no more than every 5 minutes
    # Use modified date to fetch only changed products
    last_sync = datetime.now() - timedelta(minutes=5)
    
    print(f"\nLast sync time: {last_sync.isoformat()}")
    print("Fetching products modified since last sync...")
    
    # Fetch products
    data = get_products(modified_after=last_sync)
    
    if data:
        print(f"\nResponse keys: {list(data.keys())}")
        
        if 'values' in data:
            products = data['values']
            print(f"Products found: {len(products)}")
            
            if len(products) > 0:
                print(f"\nFirst product keys: {list(products[0].keys())}")
                print(f"\nSample product data:")
                print(json.dumps(products[0], indent=2)[:500])
        else:
            print("No 'values' key in response")
            print(f"Full response: {json.dumps(data, indent=2)}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    sync_products()
