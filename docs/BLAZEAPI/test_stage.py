#!/usr/bin/env python3
"""
Blaze API - STAGE ENVIRONMENT TEST
Using Stage.blaze.me as mentioned in email
"""

import requests

# Exact keys from Paul's email
PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
KEY = "48f5dd5e57234145a233c79e66285925"

# STAGE URL from Paul's email
STAGE_URL = "https://stage.blaze.me"

headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': KEY,
    'Content-Type': 'application/json'
}

print("Testing STAGE environment...")
print(f"Base URL: {STAGE_URL}")
print("=" * 60)

# Try products endpoint on STAGE
url = f"{STAGE_URL}/api/v1/partner/products"
print(f"\nURL: {url}")
response = requests.get(url, headers=headers, params={'limit': 1})
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:300]}")

if response.status_code == 200:
    print("\n*** SUCCESS! API is working in STAGE environment! ***")
else:
    print(f"\nStill failing with status {response.status_code}")

print("=" * 60)
