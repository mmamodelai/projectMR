#!/usr/bin/env python3
"""
Blaze API Sandbox - Endpoint Discovery Test
Discover and test all available endpoints
"""

import requests
from config import *

def test_endpoints():
    """Test various endpoints to see what's available"""
    print("=" * 70)
    print("BLAZE API SANDBOX - ENDPOINT DISCOVERY")
    print("=" * 70)
    
    headers = {
        'partner_key': PARTNER_KEY,
        'Authorization': DISPENSARY_KEY,
        'Content-Type': 'application/json'
    }
    
    # Test different endpoints
    endpoints = [
        ('Products', f"{BASE_URL}/api/{API_VERSION}/partner/products"),
        ('Products Modified', f"{BASE_URL}/api/{API_VERSION}/partner/products/modified"),
        ('Transactions', f"{BASE_URL}/api/{API_VERSION}/partner/transactions"),
        ('User', f"{BASE_URL}/api/{API_VERSION}/partner/store/user"),
        ('Cart', f"{BASE_URL}/api/{API_VERSION}/partner/store/cart"),
    ]
    
    for name, url in endpoints:
        print(f"\nTesting: {name}")
        print(f"  URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, params={'limit': 1})
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Response keys: {list(data.keys())}")
                if 'values' in data:
                    print(f"  Records: {len(data['values'])}")
            elif response.status_code == 401:
                print(f"  Auth required: {response.text[:100]}")
            elif response.status_code == 404:
                print(f"  Not found")
            else:
                print(f"  Response: {response.text[:100]}")
        except Exception as e:
            print(f"  Exception: {e}")
    
    print("\nSUCCESS: Endpoint discovery complete")
    print("=" * 70)

if __name__ == "__main__":
    test_endpoints()
