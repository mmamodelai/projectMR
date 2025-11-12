#!/usr/bin/env python3
"""
Blaze API - STAGE Environment Full Test
Successfully connecting to stage.blaze.me
"""

import requests
import json

PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
KEY = "48f5dd5e57234145a233c79e66285925"
STAGE_URL = "https://stage.blaze.me"

headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': KEY,
    'Content-Type': 'application/json'
}

print("=" * 70)
print("BLAZE API - STAGE ENVIRONMENT TEST")
print("=" * 70)

# Test 1: Products
print("\n1. Testing Products Endpoint...")
url = f"{STAGE_URL}/api/v1/partner/products"
response = requests.get(url, headers=headers, params={'limit': 2})
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   SUCCESS! Got data with keys: {list(data.keys())}")
    if 'values' in data:
        print(f"   Products found: {len(data['values'])}")
else:
    print(f"   Response: {response.text[:200]}")

# Test 2: Transactions
print("\n2. Testing Transactions Endpoint...")
url = f"{STAGE_URL}/api/v1/partner/transactions"
response = requests.get(url, headers=headers, params={'limit': 2})
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   SUCCESS! Got data with keys: {list(data.keys())}")
    if 'values' in data:
        print(f"   Transactions found: {len(data['values'])}")
else:
    print(f"   Response: {response.text[:200]}")

# Test 3: Users
print("\n3. Testing Users Endpoint...")
url = f"{STAGE_URL}/api/v1/partner/store/user"
response = requests.get(url, headers=headers, params={'limit': 2})
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   SUCCESS! Got data with keys: {list(data.keys())}")
else:
    print(f"   Response: {response.text[:200]}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
