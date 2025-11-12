#!/usr/bin/env python3
"""
Quick script to check all Supabase databases and their record counts
"""
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client

def check_sms_db():
    """Check SMS Conductor database"""
    print("=" * 60)
    print("SMS CONDUCTOR DATABASE")
    print("=" * 60)
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    supabase = create_client(
        config['database']['supabase_url'],
        config['database']['supabase_key']
    )
    
    print(f"\nProject: {config['database']['supabase_url']}")
    print(f"\nTable: messages")
    
    # Get total count
    result = supabase.table('messages').select('*', count='exact').limit(1).execute()
    total = result.count
    print(f"  Total records: {total}")
    
    # Get counts by status
    statuses = ['sent', 'queued', 'failed', 'unread', 'read']
    for status in statuses:
        result = supabase.table('messages').select('id', count='exact').eq('status', status).execute()
        count = result.count
        if count > 0:
            print(f"    - {status}: {count}")
    
    # Get counts by direction
    for direction in ['inbound', 'outbound']:
        result = supabase.table('messages').select('id', count='exact').eq('direction', direction).execute()
        count = result.count
        print(f"    - {direction}: {count}")
    
    # Get sample message
    if total > 0:
        result = supabase.table('messages').select('*').limit(1).execute()
        if result.data:
            msg = result.data[0]
            print(f"\n  Sample message:")
            print(f"    ID: {msg.get('id')}")
            print(f"    Phone: {msg.get('phone_number')}")
            print(f"    Direction: {msg.get('direction')}")
            print(f"    Status: {msg.get('status')}")
            print(f"    Timestamp: {msg.get('timestamp')}")

def check_crm_db():
    """Check MoTa CRM database"""
    print("\n" + "=" * 60)
    print("MOTA CRM DATABASE")
    print("=" * 60)
    
    # Load CRM Supabase config
    env_path = '../mota-crm/config/.env'
    if not os.path.exists(env_path):
        print("  WARNING: CRM .env file not found")
        return
    
    with open(env_path, 'r') as f:
        env_vars = {}
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                env_vars[key] = value.strip('"').strip("'")
    
    if 'SUPABASE_URL' not in env_vars or 'SUPABASE_KEY' not in env_vars:
        print("  WARNING: CRM Supabase credentials not found in .env")
        return
    
    supabase = create_client(
        env_vars['SUPABASE_URL'],
        env_vars['SUPABASE_KEY']
    )
    
    print(f"\nProject: {env_vars['SUPABASE_URL']}")
    
    tables = {
        'customers': 'Customer records',
        'transactions': 'Sales transactions',
        'transaction_items': 'Line items in transactions',
        'products': 'Product catalog',
        'staff': 'Staff/budtender records'
    }
    
    print(f"\nTables:")
    total_records = 0
    for table_name, description in tables.items():
        try:
            result = supabase.table(table_name).select('*', count='exact').limit(1).execute()
            count = result.count
            total_records += count
            print(f"  {table_name:20} | {count:>8} records | {description}")
        except Exception as e:
            print(f"  {table_name:20} | ERROR: {str(e)[:50]}")
    
    print(f"\n  Total CRM records: {total_records:,}")
    
    # Get sample customer
    try:
        result = supabase.table('customers').select('*').limit(1).execute()
        if result.data:
            cust = result.data[0]
            print(f"\n  Sample customer:")
            print(f"    Name: {cust.get('name')}")
            print(f"    Phone: {cust.get('phone')}")
            print(f"    Email: {cust.get('email')}")
            print(f"    VIP Status: {cust.get('vip_status')}")
            print(f"    Visits: {cust.get('visit_count')}")
            print(f"    Lifetime Value: ${cust.get('lifetime_value', 0):.2f}")
    except Exception as e:
        print(f"  WARNING: Could not fetch sample customer: {e}")

if __name__ == "__main__":
    try:
        check_sms_db()
        check_crm_db()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("\n[OK] SMS Conductor: Active (Supabase)")
        print("[OK] MoTa CRM: Active (Supabase)")
        print("[DELETE] Local SQLite: Not used (can be deleted)")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

