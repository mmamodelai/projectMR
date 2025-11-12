#!/usr/bin/env python3
"""
Find the budtender campaign table with t-shirt/sweatshirt data
"""

from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("SEARCHING FOR BUDTENDER CAMPAIGN TABLE")
print("=" * 80)
print()

# List all tables
print("1. ALL TABLES IN DATABASE:")
print("-" * 80)
try:
    result = supabase.table('pg_tables').select('schemaname, tablename').eq('schemaname', 'public').execute()
    tables = result.data if result.data else []
    
    # Filter for campaign/budtender related tables
    relevant_tables = []
    for t in tables:
        name = t.get('tablename', '')
        if 'campaign' in name.lower() or 'budtender' in name.lower() or 'bud' in name.lower() or 'merch' in name.lower():
            relevant_tables.append(name)
            print(f"   -> {name}")
    
    print(f"\nFound {len(relevant_tables)} relevant tables")
    print()
    
except Exception as e:
    print(f"Error listing tables: {e}")
    print()

# Check specific table names
print("2. CHECKING SPECIFIC TABLES:")
print("-" * 80)

tables_to_check = [
    'campaign_messages',
    'budtenders',
    'budtender_campaigns',
    'budtender_merch',
    'tshirt_campaigns',
    'sweatshirt_campaigns',
    'bt_campaigns',
    'external_campaigns'
]

for table_name in tables_to_check:
    try:
        result = supabase.table(table_name).select('*', count='exact').limit(1).execute()
        count = result.count
        print(f"   {table_name}: EXISTS ({count:,} rows)")
        
        # If found, show sample record
        if result.data and len(result.data) > 0:
            sample = result.data[0]
            print(f"      Sample columns: {', '.join(sample.keys())}")
    except Exception as e:
        error_msg = str(e)
        if 'does not exist' in error_msg or '42P01' in error_msg:
            print(f"   {table_name}: NOT FOUND")
        else:
            print(f"   {table_name}: ERROR - {error_msg[:50]}")

print()
print("=" * 80)
print("3. CHECKING CAMPAIGN_MESSAGES IN DETAIL:")
print("=" * 80)

try:
    # Get sample records
    result = supabase.table('campaign_messages').select('*').limit(5).execute()
    
    if result.data:
        print(f"\nFound {len(result.data)} sample records")
        print()
        
        for i, record in enumerate(result.data, 1):
            print(f"Record {i}:")
            print(f"   ID: {record.get('id')}")
            print(f"   Phone: {record.get('phone_number')}")
            print(f"   Customer: {record.get('customer_name')}")
            print(f"   Status: {record.get('status')}")
            print(f"   Strategy: {record.get('strategy_type')}")
            
            # Check if it has t-shirt/sweatshirt data
            reasoning = record.get('reasoning', '')
            message = record.get('message_content', '')
            
            if 'shirt' in str(reasoning).lower() or 'shirt' in str(message).lower():
                print(f"   HAS T-SHIRT DATA!")
                print(f"   Message preview: {str(message)[:80]}...")
            print()
    else:
        print("No records found in campaign_messages")
        
except Exception as e:
    print(f"Error checking campaign_messages: {e}")

print("=" * 80)

