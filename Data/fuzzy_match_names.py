#!/usr/bin/env python3
"""
Fuzzy Name Matching - Match database customers with phone export by name

Process:
1. Get all customer names from Supabase (first_name, last_name)
2. Load export data with phone numbers
3. Fuzzy match by first + last name
4. Report matches found and save for import
"""

import csv
import re
from difflib import SequenceMatcher
from collections import defaultdict

def normalize_name(name):
    """Normalize names for matching: lowercase, remove extra spaces, remove special chars"""
    if not name:
        return ""
    # Lowercase
    name = name.lower().strip()
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name)
    # Remove common suffixes
    name = re.sub(r'\s+(jr|sr|ii|iii|iv|v)\.?$', '', name)
    return name

def similarity_score(name1, name2):
    """Calculate similarity between two names (0-1)"""
    if not name1 or not name2:
        return 0.0
    # Exact match is best
    if name1 == name2:
        return 1.0
    # Use SequenceMatcher for fuzzy matching
    return SequenceMatcher(None, name1, name2).ratio()

def load_db_customers():
    """Load customers from database - will use Supabase query"""
    print("[INFO] Loading customer names from Supabase database...")
    # This is a placeholder - we'll need to query the database
    # For now, show what we need
    print("[TODO] Need to query: SELECT member_id, name, phone FROM customers")
    return {}

def load_export_data():
    """Load phone export data"""
    print("[INFO] Loading phone export data...")
    export_data = {}
    try:
        with open('MemberDataExport_Mota_10_16_2025 - EXPORT_MEMBERS_Mota).csv', 'r', encoding='utf-8') as f:
            # Skip the timestamp header row
            next(f)
            reader = csv.DictReader(f)
            for row in reader:
                first_name = row.get('First Name', '').strip()
                last_name = row.get('Last Name', '').strip()
                phone = row.get('Primary Phone', '').strip()
                
                if first_name and last_name and phone:
                    full_name = f"{first_name} {last_name}"
                    normalized = normalize_name(full_name)
                    if normalized:
                        export_data[normalized] = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'phone': phone,
                            'email': row.get('Email Address', '').strip()
                        }
    except Exception as e:
        print(f"[ERROR] Loading export: {e}")
        return {}
    
    return export_data

def main():
    print("=" * 70)
    print("FUZZY NAME MATCHING - Database vs. Phone Export")
    print("=" * 70)
    
    # Load export first (we have this file)
    export_data = load_export_data()
    print(f"\n[OK] Loaded {len(export_data):,} phone export records with names")
    
    # Show sample
    if export_data:
        sample_names = list(export_data.items())[:5]
        print("\n[SAMPLE] Export data:")
        for norm_name, data in sample_names:
            print(f"  {norm_name:40} -> {data['phone']} ({data['email'][:20] if data['email'] else 'no email'}...)")
    
    print("\n" + "=" * 70)
    print("DATABASE EXTRACTION NEEDED")
    print("=" * 70)
    print("\nTo proceed, we need to export customer names from Supabase.")
    print("Running query to get all customer names...")
    
    return export_data

if __name__ == "__main__":
    export_data = main()
    
    # Save export names for reference
    with open('export_names_normalized.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['normalized_name', 'first_name', 'last_name', 'phone', 'email'])
        for norm_name, data in export_data.items():
            writer.writerow([norm_name, data['first_name'], data['last_name'], data['phone'], data['email']])
    
    print(f"\n[OK] Saved {len(export_data):,} normalized names to: export_names_normalized.csv")
    print("\nNEXT STEP: Query database to get customer names for matching")
