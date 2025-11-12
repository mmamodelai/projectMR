#!/usr/bin/env python3
"""
Blaze API - CORRECTED Base URL
Using api.partners.blaze.me/ as shown in their docs
"""

import requests

# Exact keys
KEY = "48f5dd5e57234145a233c79e66285925"
SECRET = "yuZLWx8b64Q5KyIp03vumIWVhOQ3bxtnpvk5U0i4+9hpHhqL678jmM5RBWCnjfLBMaNZ0//MNG1sM7V9hJqo+Q=="
PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"

# CORRECTED Base URL from their docs
BASE_URL = "https://api.partners.blaze.me"  # Note: NO /api/v1

headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': KEY,
    'Content-Type': 'application/json'
}

print("Testing with CORRECTED base URL...")
print(f"Base URL: {BASE_URL}")
print("=" * 60)

# Try products endpoint
url = f"{BASE_URL}/api/v1/partner/products"
print(f"\nURL: {url}")
response = requests.get(url, headers=headers, params={'limit': 1})
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")

if response.status_code == 200:
    print("\n✅ SUCCESS!")
else:
    print(f"\n❌ Still failing with status {response.status_code}")

print("=" * 60)
