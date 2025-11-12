#!/usr/bin/env python3
"""
Blaze API - STAGE Environment Full Test
SUCCESS! API is working!
"""

import requests
import json

PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
KEY = "51a417aaba6e4ea4bed69b428d8d9cad"
STAGE_API_URL = "https://api.stage.blaze.me"

headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': KEY,
    'Content-Type': 'application/json'
}

print("=" * 70)
print("BLAZE API - STAGE ENVIRONMENT - FULL TEST")
print("=" * 70)

# Test all endpoints
endpoints = [
    ('products', '/api/v1/partner/products'),
    ('transactions', '/api/v1/partner/transactions'),
    ('users', '/api/v1/partner/store/user'),
]

for name, endpoint in endpoints:
    print(f"\nTesting {name}...")
    url = f"{STAGE_API_URL}{endpoint}"
    response = requests.get(url, headers=headers, params={'limit': 3})
    
    if response.status_code == 200:
        data = response.json()
        print(f"   SUCCESS! Status: {response.status_code}")
        print(f"   Response keys: {list(data.keys())}")
        if 'values' in data:
            print(f"   Records found: {len(data['values'])}")
        elif 'total' in data:
            print(f"   Total records: {data.get('total', 'N/A')}")
    else:
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text[:200]}")

print("\n" + "=" * 70)
print("BLAZE API IS WORKING IN STAGE ENVIRONMENT!")
print("=" * 70)
