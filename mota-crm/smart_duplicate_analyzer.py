#!/usr/bin/env python3
"""
Smart Duplicate Analyzer
Part of Conductor SMS System

Analyzes name duplicates with additional context to reduce false positives:
- Phone number matching
- Email matching  
- Address matching
- Purchase history similarity
- Lifetime value analysis

Helps make informed merge decisions
"""

import csv
import json
from datetime import datetime
from difflib import SequenceMatcher
from supabase import create_client, Client
import sys

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

class SmartDuplicateAnalyzer:
    def __init__(self):
        self.sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.customers = []
        self.name_duplicates = []
        self.analyzed_duplicates = []
        
    def load_customers(self):
        """Load all customers from database"""
        print("Loading customers from database...")
        
        try:
            # Load all customers with pagination
            all_customers = []
            page_size = 1000
            offset = 0
            
            while True:
                result = self.sb.table('customers').select('*').range(offset, offset + page_size - 1).execute()
                
                if not result.data:
                    break
                    
                all_customers.extend(result.data)
                offset += page_size
                
                if len(result.data) < page_size:
                    break
            
            self.customers = all_customers
            print(f"Loaded {len(self.customers)} customers")
            
        except Exception as e:
            print(f"Error loading customers: {e}")
            sys.exit(1)
    
    def normalize_phone(self, phone):
        """Normalize phone number for comparison"""
        if not phone:
            return ""
        
        # Remove all non-digits
        digits = ''.join(filter(str.isdigit, str(phone)))
        
        # Handle different formats
        if len(digits) == 10:
            return digits  # US format without country code
        elif len(digits) == 11 and digits.startswith('1'):
            return digits[1:]  # Remove US country code
        else:
            return digits
    
    def normalize_name(self, name):
        """Normalize name for comparison"""
        if not name:
            return ""
        
        # Convert to lowercase, remove extra spaces
        normalized = ' '.join(str(name).lower().split())
        
        # Remove common suffixes/prefixes
        suffixes = ['jr', 'sr', 'ii', 'iii', 'iv', 'v']
        for suffix in suffixes:
            if normalized.endswith(f' {suffix}'):
                normalized = normalized[:-len(f' {suffix}')]
        
        return normalized
    
    def name_similarity(self, name1, name2):
        """Calculate similarity between two names"""
        if not name1 or not name2:
            return 0
        
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_name_duplicates(self):
        """Find customers with similar names"""
        print("Finding name duplicates...")
        
        processed = set()
        name_duplicates = []
        
        for i, customer1 in enumerate(self.customers):
            if customer1.get('member_id') in processed:
                continue
                
            name1 = customer1.get('name', '')
            if not name1:
                continue
            
            similar_customers = [customer1]
            
            for j, customer2 in enumerate(self.customers[i+1:], i+1):
                if customer2.get('member_id') in processed:
                    continue
                    
                name2 = customer2.get('name', '')
                if not name2:
                    continue
                
                similarity = self.name_similarity(name1, name2)
                
                # Threshold for name similarity
                if similarity > 0.85:
                    similar_customers.append(customer2)
                    processed.add(customer2.get('member_id'))
            
            if len(similar_customers) > 1:
                name_duplicates.append({
                    'match_value': name1,
                    'customers': similar_customers,
                    'similarity': similarity
                })
                processed.add(customer1.get('member_id'))
        
        self.name_duplicates = name_duplicates
        print(f"Found {len(name_duplicates)} name duplicate groups")
    
    def analyze_duplicate_group(self, duplicate_group):
        """Analyze a duplicate group for merge confidence"""
        customers = duplicate_group['customers']
        
        if len(customers) < 2:
            return None
        
        analysis = {
            'group_id': f"GROUP_{len(self.analyzed_duplicates) + 1}",
            'match_name': duplicate_group['match_value'],
            'customer_count': len(customers),
            'customers': customers,
            'confidence_score': 0,
            'merge_recommendation': 'REVIEW',
            'risk_factors': [],
            'supporting_evidence': [],
            'merge_priority': 'LOW'
        }
        
        # Calculate confidence score (0-100)
        confidence_factors = []
        
        # 1. Phone number matching (40 points)
        phone_matches = 0
        phones = [self.normalize_phone(c.get('phone', '')) for c in customers]
        valid_phones = [p for p in phones if p and len(p) >= 10]
        
        if len(valid_phones) > 1:
            unique_phones = set(valid_phones)
            if len(unique_phones) == 1:
                phone_matches = 40
                analysis['supporting_evidence'].append("Same phone number")
            elif len(unique_phones) < len(valid_phones):
                phone_matches = 20
                analysis['supporting_evidence'].append("Some phone numbers match")
            else:
                analysis['risk_factors'].append("Different phone numbers")
        
        confidence_factors.append(phone_matches)
        
        # 2. Email matching (30 points)
        email_matches = 0
        emails = []
        for c in customers:
            email = c.get('email', '')
            if email and isinstance(email, str) and '@' in email:
                emails.append(email.lower().strip())
        
        if len(emails) > 1:
            unique_emails = set(emails)
            if len(unique_emails) == 1:
                email_matches = 30
                analysis['supporting_evidence'].append("Same email address")
            elif len(unique_emails) < len(emails):
                email_matches = 15
                analysis['supporting_evidence'].append("Some email addresses match")
            else:
                analysis['risk_factors'].append("Different email addresses")
        
        confidence_factors.append(email_matches)
        
        # 3. Address matching (20 points)
        address_matches = 0
        addresses = []
        for c in customers:
            street = c.get('street_address', '').lower().strip()
            city = c.get('city', '').lower().strip()
            zip_code = c.get('zip_code', '').strip()
            
            if street and city and zip_code:
                addresses.append(f"{street}|{city}|{zip_code}")
        
        if len(addresses) > 1:
            unique_addresses = set(addresses)
            if len(unique_addresses) == 1:
                address_matches = 20
                analysis['supporting_evidence'].append("Same address")
            elif len(unique_addresses) < len(addresses):
                address_matches = 10
                analysis['supporting_evidence'].append("Some addresses match")
            else:
                analysis['risk_factors'].append("Different addresses")
        
        confidence_factors.append(address_matches)
        
        # 4. Purchase pattern similarity (10 points)
        purchase_similarity = 0
        lifetime_values = [float(c.get('lifetime_value', 0)) for c in customers]
        total_visits = [int(c.get('total_visits', 0)) for c in customers]
        
        if len(lifetime_values) > 1:
            # Check if values are similar (within 20% of each other)
            max_val = max(lifetime_values)
            min_val = min(lifetime_values)
            
            if max_val > 0 and (max_val - min_val) / max_val < 0.2:
                purchase_similarity = 10
                analysis['supporting_evidence'].append("Similar purchase patterns")
            else:
                analysis['risk_factors'].append("Different purchase patterns")
        
        confidence_factors.append(purchase_similarity)
        
        # Calculate total confidence
        total_confidence = sum(confidence_factors)
        analysis['confidence_score'] = total_confidence
        
        # Determine merge recommendation
        if total_confidence >= 80:
            analysis['merge_recommendation'] = 'MERGE_HIGH_CONFIDENCE'
            analysis['merge_priority'] = 'HIGH'
        elif total_confidence >= 60:
            analysis['merge_recommendation'] = 'MERGE_MEDIUM_CONFIDENCE'
            analysis['merge_priority'] = 'MEDIUM'
        elif total_confidence >= 40:
            analysis['merge_recommendation'] = 'REVIEW_CAREFULLY'
            analysis['merge_priority'] = 'LOW'
        else:
            analysis['merge_recommendation'] = 'DO_NOT_MERGE'
            analysis['merge_priority'] = 'LOW'
            analysis['risk_factors'].append("Low confidence - likely different people")
        
        # Additional risk assessment
        if len(customers) > 2:
            analysis['risk_factors'].append(f"Multiple customers ({len(customers)}) - higher merge risk")
        
        # Check for high-value customers
        high_value_customers = [c for c in customers if float(c.get('lifetime_value', 0)) > 1000]
        if len(high_value_customers) > 1:
            analysis['risk_factors'].append("Multiple high-value customers - verify carefully")
            analysis['merge_priority'] = 'HIGH'
        
        return analysis
    
    def analyze_all_duplicates(self):
        """Analyze all name duplicate groups"""
        print("Analyzing duplicate groups for merge confidence...")
        
        for i, duplicate_group in enumerate(self.name_duplicates):
            if i % 100 == 0:
                print(f"Analyzed {i}/{len(self.name_duplicates)} groups...")
            
            analysis = self.analyze_duplicate_group(duplicate_group)
            if analysis:
                self.analyzed_duplicates.append(analysis)
        
        print(f"Completed analysis of {len(self.analyzed_duplicates)} duplicate groups")
    
    def export_smart_analysis(self, filename=None):
        """Export smart analysis to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"smart_duplicate_analysis_{timestamp}.csv"
        
        print(f"Exporting smart analysis to {filename}...")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Group_ID',
                'Match_Name',
                'Customer_Count',
                'Confidence_Score',
                'Merge_Recommendation',
                'Merge_Priority',
                'Risk_Factors',
                'Supporting_Evidence',
                'Customer_1_ID',
                'Customer_1_Name',
                'Customer_1_Phone',
                'Customer_1_Email',
                'Customer_1_Lifetime_Value',
                'Customer_1_Visits',
                'Customer_2_ID',
                'Customer_2_Name',
                'Customer_2_Phone',
                'Customer_2_Email',
                'Customer_2_Lifetime_Value',
                'Customer_2_Visits',
                'Customer_3_ID',
                'Customer_3_Name',
                'Customer_3_Phone',
                'Customer_3_Email',
                'Customer_3_Lifetime_Value',
                'Customer_3_Visits',
                'Action_Required'
            ])
            
            # Data rows
            for analysis in self.analyzed_duplicates:
                customers = analysis['customers']
                
                # Create row
                row = [
                    analysis['group_id'],
                    analysis['match_name'],
                    analysis['customer_count'],
                    analysis['confidence_score'],
                    analysis['merge_recommendation'],
                    analysis['merge_priority'],
                    '; '.join(analysis['risk_factors']),
                    '; '.join(analysis['supporting_evidence'])
                ]
                
                # Add customer data (up to 3)
                for i in range(3):
                    if i < len(customers):
                        customer = customers[i]
                        row.extend([
                            customer.get('member_id', ''),
                            customer.get('name', ''),
                            customer.get('phone', ''),
                            customer.get('email', ''),
                            customer.get('lifetime_value', 0),
                            customer.get('total_visits', 0)
                        ])
                    else:
                        row.extend(['', '', '', '', '', ''])
                
                # Action required
                if analysis['merge_recommendation'] == 'MERGE_HIGH_CONFIDENCE':
                    action = 'MERGE - High confidence'
                elif analysis['merge_recommendation'] == 'MERGE_MEDIUM_CONFIDENCE':
                    action = 'MERGE - Medium confidence'
                elif analysis['merge_recommendation'] == 'REVIEW_CAREFULLY':
                    action = 'REVIEW - Low confidence'
                else:
                    action = 'DO NOT MERGE - Different people'
                
                row.append(action)
                writer.writerow(row)
        
        print(f"Exported smart analysis to {filename}")
        return filename
    
    def print_summary(self):
        """Print summary of smart analysis"""
        print("\n" + "="*80)
        print("SMART DUPLICATE ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"Total duplicate groups analyzed: {len(self.analyzed_duplicates)}")
        
        # Count by recommendation
        recommendations = {}
        priorities = {}
        
        for analysis in self.analyzed_duplicates:
            rec = analysis['merge_recommendation']
            pri = analysis['merge_priority']
            
            recommendations[rec] = recommendations.get(rec, 0) + 1
            priorities[pri] = priorities.get(pri, 0) + 1
        
        print("\nMerge Recommendations:")
        for rec, count in recommendations.items():
            print(f"  {rec}: {count} groups")
        
        print("\nPriority Levels:")
        for pri, count in priorities.items():
            print(f"  {pri}: {count} groups")
        
        # Show high-confidence merges
        high_conf = [a for a in self.analyzed_duplicates if a['merge_recommendation'] == 'MERGE_HIGH_CONFIDENCE']
        print(f"\n🏆 HIGH CONFIDENCE MERGES ({len(high_conf)} groups):")
        for analysis in high_conf[:5]:
            customers = analysis['customers']
            print(f"\n  {analysis['group_id']}: {analysis['match_name']}")
            print(f"    Confidence: {analysis['confidence_score']}/100")
            print(f"    Evidence: {'; '.join(analysis['supporting_evidence'])}")
            for customer in customers:
                print(f"      - {customer.get('name', 'N/A')} (ID: {customer.get('member_id', 'N/A')})")
                print(f"        Phone: {customer.get('phone', 'N/A')}")
                print(f"        Lifetime Value: ${customer.get('lifetime_value', 0):.2f}")
        
        # Show risky cases
        risky = [a for a in self.analyzed_duplicates if a['merge_recommendation'] == 'DO_NOT_MERGE']
        print(f"\n⚠️  DO NOT MERGE ({len(risky)} groups):")
        for analysis in risky[:3]:
            customers = analysis['customers']
            print(f"\n  {analysis['group_id']}: {analysis['match_name']}")
            print(f"    Confidence: {analysis['confidence_score']}/100")
            print(f"    Risks: {'; '.join(analysis['risk_factors'])}")
            for customer in customers:
                print(f"      - {customer.get('name', 'N/A')} (ID: {customer.get('member_id', 'N/A')})")
                print(f"        Phone: {customer.get('phone', 'N/A')}")
                print(f"        Lifetime Value: ${customer.get('lifetime_value', 0):.2f}")

def main():
    """Main function"""
    print("Smart Duplicate Analyzer")
    print("="*40)
    
    analyzer = SmartDuplicateAnalyzer()
    
    # Load customers
    analyzer.load_customers()
    
    # Find name duplicates
    analyzer.find_name_duplicates()
    
    # Analyze duplicates
    analyzer.analyze_all_duplicates()
    
    # Print summary
    analyzer.print_summary()
    
    # Export results
    csv_file = analyzer.export_smart_analysis()
    
    print(f"\n✅ Smart analysis complete!")
    print(f"📊 Analysis file: {csv_file}")
    print(f"\nReview the file and focus on HIGH/MEDIUM confidence merges first.")

if __name__ == "__main__":
    main()
