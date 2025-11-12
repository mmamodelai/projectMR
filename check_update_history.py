#!/usr/bin/env python3
from supabase import create_client
import json
from datetime import datetime

# Load config
with open('conductor-sms/config.json') as f:
    config = json.load(f)

# Init Supabase
supabase = create_client(
    config['database']['supabase_url'],
    config['database']['supabase_key']
)

print("Checking budtender record update history...")
print("="*70)

# Get all budtenders with their timestamps
response = supabase.table('budtenders').select('*').order('updated_at', desc=True).limit(20).execute()

if response.data:
    now = datetime.utcnow()
    
    for bt in response.data:
        print()
        print(f"ID: {bt.get('id')} | {bt.get('first_name')} {bt.get('last_name')} @ {bt.get('dispensary_name')}")
        print(f"  Points: {bt.get('points')}")
        
        try:
            updated = datetime.fromisoformat(str(bt.get('updated_at', '')).replace('+00:00', ''))
            updated_ago = (now - updated).total_seconds() / 60
            
            if updated_ago < 5:
                print(f"  [ALERT] Updated {updated_ago:.1f} min ago - VERY RECENT!")
            elif updated_ago < 60:
                print(f"  Updated {updated_ago:.1f} minutes ago")
            else:
                hours_ago = updated_ago / 60
                print(f"  Updated {hours_ago:.1f} hours ago")
        except:
            print(f"  Updated: {bt.get('updated_at')}")



