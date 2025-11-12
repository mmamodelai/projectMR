#!/usr/bin/env python3
"""
Blaze API Test - Fresh Start
Based on swagger.json specification
"""

import requests
import json

# API Credentials (from owner)
PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
DISPENSARY_KEY = "48f5dd5e57234145a233c79e66285925"

# API Configuration
BASE_URL = "https://api.partners.blaze.me/api/v1"

# Headers per swagger spec
headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': DISPENSARY_KEY,
    'Content-Type': 'application/json'
}

print("=" * 60)
print("BLAZE API TEST - FRESH START")
print("=" * 60)
print(f"\nPartner Key: {PARTNER_KEY[:20]}...")
print(f"Dispensary Key: {DISPENSARY_KEY[:20]}...")
print(f"\nBase URL: {BASE_URL}")
print("\n" + "=" * 60)

# Test 1: Try products endpoint
print("\nTEST 1: Products Endpoint")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/partner/products", headers=headers, params={'limit': 1})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("SUCCESS: Products endpoint working!")
        data = response.json()
        print(f"Keys in response: {list(data.keys())}")
    else:
        print(f"ERROR: Request failed")
except Exception as e:
    print(f"EXCEPTION: {e}")

# Test 2: Try transactions endpoint
print("\nTEST 2: Transactions Endpoint")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/partner/transactions", headers=headers, params={'limit': 1})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("SUCCESS: Transactions endpoint working!")
        data = response.json()
        print(f"Keys in response: {list(data.keys())}")
    else:
        print(f"ERROR: Request failed")
except Exception as e:
    print(f"EXCEPTION: {e}")

# Test 3: Try user endpoint
print("\nTEST 3: User Endpoint")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/partner/store/user", headers=headers, params={'limit': 1})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("SUCCESS: User endpoint working!")
        data = response.json()
        print(f"Keys in response: {list(data.keys())}")
    else:
        print(f"ERROR: Request failed")
except Exception as e:
    print(f"EXCEPTION: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
