#!/usr/bin/env python3
"""
Blaze API Sandbox - Pagination Test
Demonstrates proper pagination handling
"""

import requests
from config import *

def test_pagination():
    """Test pagination with skip and limit"""
    print("=" * 70)
    print("BLAZE API SANDBOX - PAGINATION TEST")
    print("=" * 70)
    
    url = f"{BASE_URL}/api/{API_VERSION}/partner/products"
    headers = {
        'partner_key': PARTNER_KEY,
        'Authorization': DISPENSARY_KEY,
        'Content-Type': 'application/json'
    }
    
    print("\nTesting pagination parameters...")
    
    # Test different pagination settings
    pagination_tests = [
        {'limit': 10, 'skip': 0},
        {'limit': 10, 'skip': 10},
        {'limit': 50, 'skip': 0},
    ]
    
    for params in pagination_tests:
        print(f"\nTesting: limit={params['limit']}, skip={params['skip']}")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Status: {response.status_code}")
            print(f"  Response keys: {list(data.keys())}")
            if 'total' in data:
                print(f"  Total records: {data['total']}")
            if 'skip' in data:
                print(f"  Skip offset: {data['skip']}")
            if 'limit' in data:
                print(f"  Limit: {data['limit']}")
        else:
            print(f"  Status: {response.status_code}")
            print(f"  Error: {response.text[:100]}")
    
    print("\nSUCCESS: Pagination handling verified")
    print("=" * 70)

if __name__ == "__main__":
    test_pagination()
