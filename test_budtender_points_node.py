#!/usr/bin/env python3
import requests
import json

print("Testing the 'Update Budtender Points' n8n node")
print("="*70)

# The exact configuration from the RC1.json node
url = "https://kiwmwoqrguyrcpjytgte.supabase.co/rest/v1/rpc/increment_budtender_points"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

headers = {
    "apikey": api_key,
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Test data - simulate what would come from the node
test_data = {
    "budtender_id": 1594,  # Jocelyn Cruz
    "points_to_add": 50
}

print(f"URL: {url}")
print(f"Headers: Content-Type: application/json, Authorization: Bearer [REDACTED]")
print(f"Body: {json.dumps(test_data, indent=2)}")
print()

try:
    response = requests.post(url, json=test_data, headers=headers)
    print(f"HTTP Status: {response.status_code}")
    print(f"Response: {response.text}")
    print()
    
    if response.status_code == 200:
        print("[SUCCESS] Node WORKS! Points were added!")
        result = response.json()
        if result:
            print(f"Budtender after update: {result}")
    else:
        print(f"[ERROR] Node FAILED! Status code: {response.status_code}")
        
except Exception as e:
    print(f"[ERROR] Request failed: {e}")



