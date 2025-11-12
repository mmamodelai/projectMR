#!/usr/bin/env python3
"""
Quick Duplicate Finder - SQL Based
Part of Conductor SMS System

Uses direct SQL queries to find duplicates efficiently
"""

import csv
from datetime import datetime
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def find_duplicates():
    """Find duplicates using SQL queries"""
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("🔍 Finding duplicates using SQL queries...")
    
    all_duplicates = []
    
    # 1. Phone number duplicates
    print("📞 Checking phone duplicates...")
    try:
        phone_query = """
        SELECT 
            REGEXP_REPLACE(phone, '[^0-9]', '', 'g') as clean_phone,
            COUNT(*) as count,
            STRING_AGG(member_id, ', ') as member_ids,
            STRING_AGG(name, ' | ') as names,
            STRING_AGG(COALESCE(email, ''), ' | ') as emails,
            STRING_AGG(CAST(lifetime_value AS TEXT), ' | ') as lifetime_values
        FROM customers 
        WHERE phone IS NOT NULL 
        AND LENGTH(REGEXP_REPLACE(phone, '[^0-9]', '', 'g')) >= 10
        GROUP BY clean_phone
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC
        """
        
        result = sb.rpc('execute_sql', {'query': phone_query}).execute()
        phone_duplicates = result.data if result.data else []
        
        for dup in phone_duplicates:
            all_duplicates.append({
                'type': 'phone',
                'match_value': dup['clean_phone'],
                'count': dup['count'],
                'member_ids': dup['member_ids'],
                'names': dup['names'],
                'emails': dup['emails'],
                'lifetime_values': dup['lifetime_values'],
                'confidence': 'HIGH'
            })
        
        print(f"   Found {len(phone_duplicates)} phone duplicate groups")
        
    except Exception as e:
        print(f"   Error with phone query: {e}")
    
    # 2. Email duplicates
    print("📧 Checking email duplicates...")
    try:
        email_query = """
        SELECT 
            LOWER(TRIM(email)) as clean_email,
            COUNT(*) as count,
            STRING_AGG(member_id, ', ') as member_ids,
            STRING_AGG(name, ' | ') as names,
            STRING_AGG(COALESCE(phone, ''), ' | ') as phones,
            STRING_AGG(CAST(lifetime_value AS TEXT), ' | ') as lifetime_values
        FROM customers 
        WHERE email IS NOT NULL 
        AND email != ''
        AND email LIKE '%@%'
        GROUP BY clean_email
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC
        """
        
        result = sb.rpc('execute_sql', {'query': email_query}).execute()
        email_duplicates = result.data if result.data else []
        
        for dup in email_duplicates:
            all_duplicates.append({
                'type': 'email',
                'match_value': dup['clean_email'],
                'count': dup['count'],
                'member_ids': dup['member_ids'],
                'names': dup['names'],
                'phones': dup['phones'],
                'lifetime_values': dup['lifetime_values'],
                'confidence': 'HIGH'
            })
        
        print(f"   Found {len(email_duplicates)} email duplicate groups")
        
    except Exception as e:
        print(f"   Error with email query: {e}")
    
    # 3. Name duplicates (exact matches)
    print("👤 Checking exact name duplicates...")
    try:
        name_query = """
        SELECT 
            LOWER(TRIM(name)) as clean_name,
            COUNT(*) as count,
            STRING_AGG(member_id, ', ') as member_ids,
            STRING_AGG(name, ' | ') as names,
            STRING_AGG(COALESCE(phone, ''), ' | ') as phones,
            STRING_AGG(COALESCE(email, ''), ' | ') as emails,
            STRING_AGG(CAST(lifetime_value AS TEXT), ' | ') as lifetime_values
        FROM customers 
        WHERE name IS NOT NULL 
        AND name != ''
        GROUP BY clean_name
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC
        LIMIT 50
        """
        
        result = sb.rpc('execute_sql', {'query': name_query}).execute()
        name_duplicates = result.data if result.data else []
        
        for dup in name_duplicates:
            all_duplicates.append({
                'type': 'name_exact',
                'match_value': dup['clean_name'],
                'count': dup['count'],
                'member_ids': dup['member_ids'],
                'names': dup['names'],
                'phones': dup['phones'],
                'emails': dup['emails'],
                'lifetime_values': dup['lifetime_values'],
                'confidence': 'MEDIUM'
            })
        
        print(f"   Found {len(name_duplicates)} exact name duplicate groups")
        
    except Exception as e:
        print(f"   Error with name query: {e}")
    
    return all_duplicates

def export_to_csv(duplicates, filename=None):
    """Export duplicates to CSV"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quick_duplicates_{timestamp}.csv"
    
    print(f"📊 Exporting to {filename}...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow([
            'Type',
            'Match_Value',
            'Count',
            'Confidence',
            'Member_IDs',
            'Names',
            'Phones',
            'Emails',
            'Lifetime_Values',
            'Merge_Recommendation'
        ])
        
        # Data rows
        for dup in duplicates:
            # Determine merge recommendation
            if dup['confidence'] == 'HIGH':
                recommendation = 'MERGE - High confidence'
            elif dup['confidence'] == 'MEDIUM':
                recommendation = 'REVIEW - Check details'
            else:
                recommendation = 'REVIEW - Low confidence'
            
            writer.writerow([
                dup['type'],
                dup['match_value'],
                dup['count'],
                dup['confidence'],
                dup.get('member_ids', ''),
                dup.get('names', ''),
                dup.get('phones', ''),
                dup.get('emails', ''),
                dup.get('lifetime_values', ''),
                recommendation
            ])
    
    print(f"✅ Exported {len(duplicates)} duplicate groups to {filename}")
    return filename

def print_summary(duplicates):
    """Print summary"""
    print("\n" + "="*60)
    print("QUICK DUPLICATE FINDER - RESULTS")
    print("="*60)
    
    print(f"Total duplicate groups found: {len(duplicates)}")
    
    # Count by type
    type_counts = {}
    confidence_counts = {}
    
    for dup in duplicates:
        dup_type = dup['type']
        confidence = dup['confidence']
        
        type_counts[dup_type] = type_counts.get(dup_type, 0) + 1
        confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1
    
    print("\nBy Type:")
    for dup_type, count in type_counts.items():
        print(f"  {dup_type}: {count} groups")
    
    print("\nBy Confidence:")
    for confidence, count in confidence_counts.items():
        print(f"  {confidence}: {count} groups")
    
    # Show top duplicates
    print("\n🏆 TOP DUPLICATES:")
    sorted_dups = sorted(duplicates, key=lambda x: x['count'], reverse=True)
    
    for i, dup in enumerate(sorted_dups[:10], 1):
        print(f"\n{i}. {dup['type'].upper()} - {dup['match_value']}")
        print(f"   Count: {dup['count']} customers")
        print(f"   Confidence: {dup['confidence']}")
        print(f"   Names: {dup.get('names', 'N/A')}")
        print(f"   Lifetime Values: {dup.get('lifetime_values', 'N/A')}")

def main():
    """Main function"""
    print("Quick Duplicate Finder")
    print("="*30)
    
    try:
        # Find duplicates
        duplicates = find_duplicates()
        
        # Print summary
        print_summary(duplicates)
        
        # Export to CSV
        csv_file = export_to_csv(duplicates)
        
        print(f"\n🎉 Analysis complete!")
        print(f"📁 Results saved to: {csv_file}")
        print(f"\n💡 Focus on HIGH confidence duplicates first!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This might be due to Supabase RPC function not being available.")
        print("Let me try a different approach...")

if __name__ == "__main__":
    main()
