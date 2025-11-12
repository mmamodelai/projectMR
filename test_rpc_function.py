#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from supabase import create_client
import json
import sys

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

# Load config
with open('conductor-sms/config.json') as f:
    config = json.load(f)

# Init Supabase
supabase = create_client(
    config['database']['supabase_url'],
    config['database']['supabase_key']
)

print("Testing Supabase RPC function: increment_budtender_points")
print("="*60)

# Try to call the RPC function
try:
    response = supabase.rpc('increment_budtender_points', {
        'budtender_id': 1594,
        'points_to_add': 100
    }).execute()
    print("[SUCCESS] RPC Function EXISTS and was called!")
    print(f"Response: {response}")
except Exception as e:
    print(f"[ERROR] RPC Function ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
    print("\nThe RPC function 'increment_budtender_points' likely doesn't exist!")
    print("You need to create it in Supabase as a PostgreSQL function.")
