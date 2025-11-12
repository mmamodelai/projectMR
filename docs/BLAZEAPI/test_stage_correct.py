#!/usr/bin/env python3
"""
Blaze API - CORRECT STAGE URL
Using api.stage.blaze.me
"""

import requests
import json

PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
KEY = "48f5dd5e57234145a233c79e66285925"
STAGE_API_URL = "https://api.stage.blaze.me"

headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': KEY,
    'Content-Type': 'application/json'
}

print("=" * 70)
print("BLAZE API - STAGE ENVIRONMENT (CORRECT URL)")
print("=" * 70)
print(f"Base URL: {STAGE_API_URL}")

# Test products
print("\n1. Testing Products...")
url = f"{STAGE_API_URL}/api/v1/partner/products"
response = requests.get(url, headers=headers, params={'limit': 2})
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   SUCCESS! Keys: {list(data.keys())}")
    if 'values' in data:
        print(f"   Products: {len(data['values'])}")
else:
    print(f"   Error: {response.text[:200]}")

# Test transactions
print("\n2. Testing Transactions...")
url = f"{STAGE_API_URL}/api/v1/partner/transactions"
response = requests.get(url, headers=headers, params={'limit': 2})
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   SUCCESS! Keys: {list(data.keys())}")
    if 'values' in data:
        print(f"   Transactions: {len(data['values'])}")
else:
    print(f"   Error: {response.text[:200]}")

print("\n" + "=" * 70)
