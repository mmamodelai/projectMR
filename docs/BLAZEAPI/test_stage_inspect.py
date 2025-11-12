#!/usr/bin/env python3
"""
Blaze API - Inspect STAGE Response
"""

import requests

PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
KEY = "48f5dd5e57234145a233c79e66285925"
STAGE_URL = "https://stage.blaze.me"

headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': KEY,
    'Content-Type': 'application/json'
}

url = f"{STAGE_URL}/api/v1/partner/products"
response = requests.get(url, headers=headers, params={'limit': 1})

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"\nFirst 500 chars of response:")
print(response.text[:500])
