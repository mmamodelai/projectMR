#!/usr/bin/env python3
"""
Blaze API Minimal Test
Testing with exact credentials from screenshot
"""

import requests

print("Testing Blaze API with exact credentials from screenshot...")
print("=" * 60)

# Exact values from screenshot - BACK TO ORIGINAL
headers = {
    'partner_key': '30117b29cdcf44d7a7f4a766e8d398e7',
    'Authorization': '48f5dd5e57234145a233c79e66285925',
    'Content-Type': 'application/json'
}

url = "https://api.partners.blaze.me/api/v1/partner/products"

print(f"\nURL: {url}")
print(f"Headers: {headers}")
print("\n" + "=" * 60)

response = requests.get(url, headers=headers, params={'limit': 1})

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("\nSUCCESS! API is working!")
else:
    print(f"\nFAILED: Status {response.status_code}")
    print("Check if keys are properly activated in Blaze.")

print("=" * 60)
