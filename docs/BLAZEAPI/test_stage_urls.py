#!/usr/bin/env python3
"""
Blaze API - Try Different STAGE URLs
"""

import requests

PARTNER_KEY = "30117b29cdcf44d7a7f4a766e8d398e7"
KEY = "48f5dd5e57234145a233c79e66285925"

headers = {
    'partner_key': PARTNER_KEY,
    'Authorization': KEY,
    'Content-Type': 'application/json'
}

# Try different STAGE URLs
urls_to_try = [
    "https://stage.blaze.me/api/v1/partner/products",
    "https://api.stage.blaze.me/api/v1/partner/products",
    "https://stage.partners.blaze.me/api/v1/partner/products",
    "https://stage.blaze.me/api/partner/products",
]

for url in urls_to_try:
    print(f"\nTrying: {url}")
    response = requests.get(url, headers=headers, params={'limit': 1})
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if 'application/json' in response.headers.get('Content-Type', ''):
        print("*** GOT JSON! ***")
        print(response.text[:200])
        break
    else:
        print("Got HTML, not JSON")
