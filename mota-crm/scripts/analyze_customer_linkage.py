#!/usr/bin/env python3
"""
Analyze how to link ALL customer data from a phone number.
Shows the complete data linkage chain.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env')
load_dotenv(env_path)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def analyze_customer_data_linkage(phone_number):
    """
    Show the complete data linkage chain from phone number.
    """
    print(f"{'='*80}")
    print(f"🔍 ANALYZING CUSTOMER DATA LINKAGE FOR: {phone_number}")
    print(f"{'='*80}\n")
    
    # Step 1: Get Customer from phone number
    print("STEP 1: customers table (by phone) →")
    customers = supabase.table('customers').select('*').eq('phone', phone_number).execute()
    
    if not customers.data:
        print(f"❌ No customer found with phone {phone_number}")
        return
    
    customer = customers.data[0]
    customer_id = customer['customer_id']
    
    print(f"✅ Found customer_id: {customer_id}")
    print(f"   Name: {customer.get('first_name')} {customer.get('last_name')}")
    print(f"   Email: {customer.get('email')}")
    print(f"   Phone: {customer.get('phone')}")
    print(f"   VIP Status: {customer.get('vip_status')}")
    print(f"   Lifetime Value: ${customer.get('lifetime_value')}")
    print(f"   Total Visits: {customer.get('total_visits')}")
    print(f"   Last Visit: {customer.get('last_visit_date')}")
    print(f"   Churn Risk: {customer.get('churn_risk')}")
    
    # Step 2: Get Transactions for customer_id
    print(f"\nSTEP 2: transactions table (by customer_id={customer_id}) →")
    transactions = supabase.table('transactions').select('*').eq('customer_id', customer_id).order('date', desc=True).limit(5).execute()
    
    print(f"✅ Found {len(transactions.data)} transactions")
    
    transaction_ids = []
    for i, tx in enumerate(transactions.data[:3], 1):
        tx_id = tx['transaction_id']
        transaction_ids.append(tx_id)
        print(f"\n   Transaction {i}:")
        print(f"   - transaction_id: {tx_id}")
        print(f"   - date: {tx.get('date')}")
        print(f"   - total: ${tx.get('total')}")
        print(f"   - store_name: {tx.get('store_name')}")
        print(f"   - staff_name: {tx.get('staff_name')}")
        print(f"   - staff_id: {tx.get('staff_id')}")
        print(f"   - payment_method: {tx.get('payment_method')}")
    
    # Step 3: Get Transaction Items for each transaction_id
    if transaction_ids:
        print(f"\nSTEP 3: transaction_items table (by transaction_id) →")
        
        for tx_id in transaction_ids[:2]:  # Show first 2 transactions
            items = supabase.table('transaction_items').select('*').eq('transaction_id', tx_id).execute()
            print(f"\n   Transaction {tx_id} has {len(items.data)} items:")
            
            product_skus = []
            for item in items.data[:5]:  # Show first 5 items
                product_sku = item.get('product_sku')
                product_skus.append(product_sku)
                print(f"   - {item.get('product_name')}")
                print(f"     SKU: {product_sku}, Price: ${item.get('price')}, Qty: {item.get('quantity')}")
            
            # Step 4: Get Product details for product_sku
            if product_skus:
                print(f"\n   STEP 4: products table (by product_sku) →")
                for sku in product_skus[:2]:  # Show first 2 products
                    products = supabase.table('products').select('*').eq('sku', sku).execute()
                    if products.data:
                        p = products.data[0]
                        print(f"      Product SKU {sku}:")
                        print(f"      - product_name: {p.get('product_name')}")
                        print(f"      - category: {p.get('category')}")
                        print(f"      - brand: {p.get('brand')}")
                        print(f"      - cost: ${p.get('cost')}")
                        print(f"      - in_stock: {p.get('in_stock')}")
                        print(f"      - stock_age_days: {p.get('stock_age_days')}")
    
    # Step 5: Check staff table
    if transactions.data and transactions.data[0].get('staff_id'):
        print(f"\nSTEP 5: staff table (by staff_id) →")
        staff_id = transactions.data[0].get('staff_id')
        staff = supabase.table('staff').select('*').eq('staff_id', staff_id).execute()
        if staff.data:
            s = staff.data[0]
            print(f"✅ Staff details for {s.get('staff_name')}:")
            print(f"   - role: {s.get('role')}")
            print(f"   - store_name: {s.get('store_name')}")
            print(f"   - performance_tier: {s.get('performance_tier')}")
    
    # Summary: The Complete Chain
    print(f"\n{'='*80}")
    print(f"📊 COMPLETE DATA LINKAGE CHAIN")
    print(f"{'='*80}\n")
    print(f"phone_number ({phone_number})")
    print(f"    ↓")
    print(f"customers table → customer_id ({customer_id})")
    print(f"    ↓")
    print(f"transactions table → transaction_id (e.g., {transaction_ids[0] if transaction_ids else 'N/A'})")
    print(f"    ↓")
    print(f"transaction_items table → product_sku")
    print(f"    ↓")
    print(f"products table → full product details")
    print(f"\nALSO:")
    print(f"transactions table → staff_id")
    print(f"    ↓")
    print(f"staff table → staff details")
    
    print(f"\n{'='*80}")
    print(f"🎯 FOR AI AGENT: Query Strategy")
    print(f"{'='*80}\n")
    print(f"1. START: Phone number from SMS")
    print(f"2. LOOKUP: customers table → get customer_id, name, email, LTV, visits")
    print(f"3. QUERY: transactions table (by customer_id) → get recent transactions")
    print(f"4. FOR EACH transaction_id:")
    print(f"   - QUERY: transaction_items table → get all items purchased")
    print(f"   - FOR EACH product_sku:")
    print(f"     - QUERY: products table → get full product details")
    print(f"5. QUERY: staff table (by staff_id) → get budtender info")
    print(f"\n✅ This gives AI the COMPLETE customer dataset!")

if __name__ == "__main__":
    phone = sys.argv[1] if len(sys.argv) > 1 else "+16199773020"
    analyze_customer_data_linkage(phone)

