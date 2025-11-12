#!/usr/bin/env python3
"""
Blaze API - NEW STAGE CREDENTIALS TEST
"""

import requests
import json

# NEW STAGE credentials
PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
KEY = "51a417aaba6e4ea4bed69b428d8d9cad"
SECRET = "fddTd5ZN2NsboG4Bkzt09aZPiIPlSs9y8IF9Q6HTV0DeVOUmwq5XEC3B57/Oa0IAdoVUWg5xGaBt8FQcj74WwQ=="

STAGE_API_URL = "https://api.stage.blaze.me"

headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': KEY,
    'Content-Type': 'application/json'
}

print("=" * 70)
print("TESTING NEW STAGE CREDENTIALS")
print("=" * 70)

# Test products
print("\n1. Testing Products with NEW KEY...")
url = f"{STAGE_API_URL}/api/v1/partner/products"
response = requests.get(url, headers=headers, params={'limit': 3})
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   SUCCESS! Keys: {list(data.keys())}")
    if 'values' in data:
        print(f"   Products found: {len(data['values'])}")
        if len(data['values']) > 0:
            print(f"   First product: {list(data['values'][0].keys())}")
else:
    print(f"   Error: {response.text[:200]}")

# Try with SECRET if KEY fails
if response.status_code != 200:
    print("\n2. Trying with SECRET instead...")
    headers['Authorization'] = SECRET
    response = requests.get(url, headers=headers, params={'limit': 3})
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   SUCCESS WITH SECRET! Keys: {list(data.keys())}")
        if 'values' in data:
            print(f"   Products found: {len(data['values'])}")
    else:
        print(f"   Error: {response.text[:200]}")

print("\n" + "=" * 70)
