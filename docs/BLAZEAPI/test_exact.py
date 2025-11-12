#!/usr/bin/env python3
"""
Blaze API - Exact Key Verification
Check for any hidden characters or issues
"""

import requests

# Exact keys - checking for any issues
KEY = "48f5dd5e57234145a233c79e66285925"
SECRET = "yuZLWx8b64Q5KyIp03vumIWVhOQ3bxtnpvk5U0i4+9hpHhqL678jmM5RBWCnjfLBMaNZ0//MNG1sM7V9hJqo+Q=="
PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"

print("Verifying keys...")
print(f"KEY length: {len(KEY)}")
print(f"SECRET length: {len(SECRET)}")
print(f"PARTNER_KEY length: {len(PARTNER_KEY)}")
print()

# Standard combination per swagger
headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': KEY,
    'Content-Type': 'application/json'
}

print("Headers:")
for k, v in headers.items():
    print(f"  {k}: {v} (len={len(v)})")

print("\n" + "=" * 60)
print("Making request...")

url = "https://api.partners.blaze.me/api/v1/partner/products"
response = requests.get(url, headers=headers, params={'limit': 1})

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print("=" * 60)
