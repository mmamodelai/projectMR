#!/usr/bin/env python3
"""
Import Budtenders to Supabase Database
Part of Conductor SMS System

Usage: python import_budtenders_to_supabase.py
"""

import json
import os
from supabase import create_client, Client

# Supabase credentials (using your existing ones)
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def import_budtenders():
    """Import budtenders from JSON to Supabase"""
    
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Load JSON data
    json_file = "dispensary_budtender_clean.json"
    
    if not os.path.exists(json_file):
        print(f"ERROR: {json_file} not found!")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} dispensaries from JSON")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing budtender data...")
        supabase.table('budtenders').delete().neq('id', 0).execute()
        
        # Import budtenders
        total_imported = 0
        
        for dispensary_name, dispensary in data.items():
            print(f"Importing budtenders from {dispensary_name}...")
            
            for budtender in dispensary['budtenders']:
                budtender_data = {
                    'first_name': budtender['first_name'],
                    'last_name': budtender['last_name'],
                    'phone': budtender['phone'] if budtender['phone'] else None,
                    'email': budtender['email'] if budtender['email'] else None,
                    'dispensary_name': dispensary_name,
                    'points': 0  # Default points value
                }
                
                try:
                    supabase.table('budtenders').insert(budtender_data).execute()
                    total_imported += 1
                except Exception as e:
                    print(f"Error importing {budtender['first_name']} {budtender['last_name']}: {e}")
        
        print(f"\nImport complete! {total_imported} budtenders imported to Supabase.")
        
        # Verify import
        result = supabase.table('budtenders').select('*', count='exact').execute()
        print(f"Total budtenders in database: {result.count}")
        
        # Show sample data
        sample = supabase.table('budtenders').select('*').limit(5).execute()
        print("\nSample imported data:")
        for budtender in sample.data:
            print(f"  {budtender['first_name']} {budtender['last_name']} - {budtender['dispensary_name']} ({budtender['points']} points)")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    import_budtenders()
