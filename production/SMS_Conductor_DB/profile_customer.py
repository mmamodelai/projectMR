#!/usr/bin/env python3
"""
Deep customer profiling using ONLY Supabase data
Identifies data gaps and derivative insights
"""
import json
import sys
import io
from supabase import create_client
from datetime import datetime, timedelta
from collections import Counter

# Force UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load SMS Supabase config
with open('config.json', 'r') as f:
    config = json.load(f)

sms_supabase = create_client(
    config['database']['supabase_url'],
    config['database']['supabase_key']
)

# CRM Supabase config (hardcoded, same as viewers)
CRM_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
CRM_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

crm_supabase = create_client(CRM_URL, CRM_KEY)

# Target phone number
PHONE = "+16199773020"

print("=" * 80)
print(f"CUSTOMER PROFILE: {PHONE}")
print("=" * 80)

# 1. Get customer from CRM
print("\n[1] LOOKING UP CUSTOMER IN CRM...")
customer_result = crm_supabase.table('customers').select('*').eq('phone', PHONE).execute()

if not customer_result.data:
    print(f"❌ Customer not found in CRM database")
    print(f"\n[CHECKING SMS DATABASE...]")
    sms_result = sms_supabase.table('messages').select('*').eq('phone_number', PHONE).execute()
    if sms_result.data:
        print(f"✅ Found {len(sms_result.data)} SMS messages from this number")
        print(f"\n🔍 DATA GAP: Customer is texting us but not in CRM!")
        print(f"   - They have {len(sms_result.data)} message(s)")
        print(f"   - But no purchase history in the system")
        print(f"   - Action: Import this customer or create new profile")
    else:
        print(f"❌ Not found in SMS database either")
    exit()

customer = customer_result.data[0]
customer_id = customer['id']

print(f"✅ FOUND: {customer.get('name', 'N/A')}")
print(f"   Email: {customer.get('email', 'N/A')}")
print(f"   Phone: {customer.get('phone', 'N/A')}")
print(f"   VIP Status: {customer.get('vip_status', 'N/A')}")
print(f"   Total Visits: {customer.get('visit_count', customer.get('visits', 'N/A'))}")
print(f"   Lifetime Value: ${customer.get('lifetime_value', 0):.2f}")
print(f"   Last Visit: {customer.get('last_visit_date', customer.get('last_visit', 'N/A'))}")
print(f"   Churn Risk: {customer.get('churn_risk', 'N/A')}")

# 2. Get all transactions
print(f"\n[2] LOADING TRANSACTION HISTORY...")
transactions_result = crm_supabase.table('transactions').select('*').eq('customer_id', customer_id).order('date', desc=True).execute()
transactions = transactions_result.data

if not transactions:
    print(f"❌ No transactions found")
    exit()

print(f"✅ Found {len(transactions)} transactions")

# Calculate derivative data
total_spend = sum(t['total'] for t in transactions)
avg_transaction = total_spend / len(transactions)
first_purchase = min(t['date'] for t in transactions)
last_purchase = max(t['date'] for t in transactions)
first_date = datetime.strptime(first_purchase, '%Y-%m-%d')
last_date = datetime.strptime(last_purchase, '%Y-%m-%d')
customer_lifetime_days = (last_date - first_date).days
days_since_last = (datetime.now() - last_date).days

print(f"\n   📊 TRANSACTION ANALYTICS:")
print(f"   - Total Spend: ${total_spend:.2f}")
print(f"   - Average Transaction: ${avg_transaction:.2f}")
print(f"   - First Purchase: {first_purchase}")
print(f"   - Last Purchase: {last_purchase}")
print(f"   - Customer Lifetime: {customer_lifetime_days} days")
print(f"   - Days Since Last Purchase: {days_since_last}")

# Payment method preferences
payment_methods = Counter(t['payment_method'] for t in transactions if t.get('payment_method'))
print(f"\n   💳 PAYMENT PREFERENCES:")
for method, count in payment_methods.most_common():
    pct = (count / len(transactions)) * 100
    print(f"   - {method}: {count} times ({pct:.1f}%)")

# Location preferences
locations = Counter(t['location'] for t in transactions if t.get('location'))
print(f"\n   📍 LOCATION PREFERENCES:")
for loc, count in locations.most_common():
    pct = (count / len(transactions)) * 100
    print(f"   - {loc}: {count} visits ({pct:.1f}%)")

# 3. Get transaction items (what they buy)
print(f"\n[3] LOADING PURCHASE DETAILS...")
transaction_ids = [t['transaction_id'] for t in transactions]

# Get items in batches
all_items = []
batch_size = 100
for i in range(0, len(transaction_ids), batch_size):
    batch = transaction_ids[i:i+batch_size]
    items_result = crm_supabase.table('transaction_items').select('*').in_('transaction_id', batch).execute()
    all_items.extend(items_result.data)

print(f"✅ Found {len(all_items)} items purchased")

# Product preferences
product_skus = [item['product_sku'] for item in all_items]
sku_counts = Counter(product_skus)

print(f"\n   🛍️ MOST PURCHASED PRODUCTS:")
for sku, count in sku_counts.most_common(5):
    print(f"   - {sku}: {count} times")

# 4. Get product details
print(f"\n[4] ANALYZING PRODUCT PREFERENCES...")
unique_skus = list(sku_counts.keys())[:10]  # Top 10 products
products_result = crm_supabase.table('products').select('*').in_('sku', unique_skus).execute()
products = {p['sku']: p for p in products_result.data}

print(f"\n   🌿 TOP PRODUCTS DETAIL:")
for sku, count in sku_counts.most_common(5):
    if sku in products:
        p = products[sku]
        print(f"\n   [{count}x purchased] {p['name']}")
        print(f"      Category: {p.get('category', 'N/A')}")
        print(f"      Brand: {p.get('brand', 'N/A')}")
        print(f"      THC: {p.get('thc_content', 'N/A')} | CBD: {p.get('cbd_content', 'N/A')}")
        print(f"      Strain: {p.get('strain_type', 'N/A')}")
    else:
        print(f"   {sku}: {count} times (product details not found)")

# Category preferences
categories = Counter()
for item in all_items:
    if item['product_sku'] in products:
        cat = products[item['product_sku']].get('category', 'Unknown')
        categories[cat] += 1

print(f"\n   📦 CATEGORY PREFERENCES:")
for cat, count in categories.most_common():
    pct = (count / len(all_items)) * 100
    print(f"   - {cat}: {count} items ({pct:.1f}%)")

# 5. Check SMS history
print(f"\n[5] CHECKING SMS COMMUNICATION HISTORY...")
sms_result = sms_supabase.table('messages').select('*').eq('phone_number', PHONE).order('timestamp', desc=True).execute()
messages = sms_result.data

if messages:
    print(f"✅ Found {len(messages)} SMS messages")
    inbound = [m for m in messages if m['direction'] == 'inbound']
    outbound = [m for m in messages if m['direction'] == 'outbound']
    print(f"   - Inbound: {len(inbound)}")
    print(f"   - Outbound: {len(outbound)}")
    
    print(f"\n   💬 RECENT MESSAGES:")
    for msg in messages[:3]:
        direction = "←" if msg['direction'] == 'inbound' else "→"
        content = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
        print(f"   {direction} [{msg['timestamp'][:10]}] {content}")
else:
    print(f"❌ No SMS history found")

# 6. IDENTIFY DATA GAPS
print("\n" + "=" * 80)
print("🔍 DATA GAPS & MISSING INSIGHTS")
print("=" * 80)

gaps = []

# Gap 1: Purchase frequency patterns
if len(transactions) > 1:
    transaction_dates = sorted([datetime.strptime(t['date'], '%Y-%m-%d') for t in transactions])
    intervals = [(transaction_dates[i+1] - transaction_dates[i]).days for i in range(len(transaction_dates)-1)]
    avg_interval = sum(intervals) / len(intervals) if intervals else 0
    print(f"\n✅ DERIVED: Average days between visits: {avg_interval:.1f}")
    print(f"   → Could predict: Next expected visit date: {last_date + timedelta(days=avg_interval)}")
else:
    gaps.append("Not enough transactions to calculate visit frequency")

# Gap 2: Time-of-day preferences
print(f"\n❌ MISSING: Time of day preferences")
print(f"   → Transaction table has 'date' but no 'time'")
print(f"   → Can't determine: Morning shopper? Evening shopper?")
gaps.append("Transaction timestamp (hour/minute)")

# Gap 3: Basket size
total_items = len(all_items)
items_per_transaction = total_items / len(transactions)
print(f"\n✅ DERIVED: Average items per visit: {items_per_transaction:.1f}")

# Gap 4: Price sensitivity
if all_items:
    avg_unit_price = sum(item.get('unit_price', 0) for item in all_items) / len(all_items)
    print(f"\n✅ DERIVED: Average price point: ${avg_unit_price:.2f} per item")
    print(f"   → Insight: {'Premium' if avg_unit_price > 30 else 'Value'} shopper")

# Gap 5: Discount usage
discount_items = [item for item in all_items if item.get('discount', 0) > 0]
if discount_items:
    total_saved = sum(item['discount'] for item in discount_items)
    print(f"\n✅ DERIVED: Discount usage: {len(discount_items)}/{len(all_items)} items ({(len(discount_items)/len(all_items)*100):.1f}%)")
    print(f"   → Total saved: ${total_saved:.2f}")
else:
    print(f"\n⚠️ LIMITED: No discount data or customer doesn't use discounts")

# Gap 6: Staff relationships
staff_ids = [t['staff_id'] for t in transactions if t.get('staff_id')]
if staff_ids:
    staff_counts = Counter(staff_ids)
    print(f"\n✅ DERIVED: Works with {len(staff_counts)} different budtenders")
    print(f"   → Most frequent: {customer.get('preferred_budtender', 'Not calculated')}")
else:
    print(f"\n❌ MISSING: Staff interaction data")
    gaps.append("Staff names/details linked to transactions")

# Gap 7: Product effects preferences
effects = []
for item in all_items:
    if item['product_sku'] in products:
        product_effects = products[item['product_sku']].get('effects', '')
        if product_effects:
            effects.extend(product_effects.split(','))

if effects:
    effect_counts = Counter(e.strip() for e in effects)
    print(f"\n✅ DERIVED: Desired effects preferences:")
    for effect, count in effect_counts.most_common(3):
        print(f"   - {effect}: {count} times")
else:
    print(f"\n❌ MISSING: Product effects data incomplete")
    gaps.append("Comprehensive product effects tagging")

# Gap 8: Seasonal patterns
if len(transactions) >= 12:
    months = Counter(datetime.strptime(t['date'], '%Y-%m-%d').month for t in transactions)
    print(f"\n✅ DERIVED: Seasonal patterns:")
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    for month, count in sorted(months.items()):
        print(f"   - {month_names[month-1]}: {count} visits")
else:
    print(f"\n⚠️ LIMITED: Not enough data for seasonal analysis (need 12+ transactions)")

# Gap 9: Referral source
print(f"\n❌ MISSING: How did customer find us?")
gaps.append("Referral source / acquisition channel")

# Gap 10: Customer feedback/ratings
print(f"\n❌ MISSING: Product ratings or feedback")
gaps.append("Product ratings/reviews from customer")

# Gap 11: Cart abandonment
print(f"\n❌ MISSING: Shopping behavior before purchase")
gaps.append("Website/app browsing history, cart abandonment")

# Gap 12: Cross-sell opportunities
print(f"\n🔮 DERIVATIVE INSIGHT: Cross-sell opportunities")
if len(categories) > 1:
    print(f"   → Customer buys {len(categories)} different categories")
    print(f"   → Opportunity: Recommend products from less-purchased categories")
else:
    print(f"   → Customer very focused on one category")
    print(f"   → Opportunity: Introduce variety, bundles")

# Summary
print("\n" + "=" * 80)
print("📋 SUMMARY: WHAT WE KNOW vs. WHAT WE'RE MISSING")
print("=" * 80)

print("\n✅ STRONG DATA:")
print("   - Purchase history (transactions, items, products)")
print("   - Spending patterns (lifetime value, average transaction)")
print("   - Location preferences")
print("   - Payment method preferences")
print("   - Product category preferences")
print("   - SMS communication history")
print("   - VIP status & churn risk (auto-calculated)")

print("\n❌ MISSING DATA (would improve insights):")
for i, gap in enumerate(gaps, 1):
    print(f"   {i}. {gap}")

print("\n🔮 DERIVATIVE DATA WE COULD ADD:")
print("   1. Purchase frequency score (days between visits)")
print("   2. Price sensitivity score (avg $ per item)")
print("   3. Discount affinity score (% of discounted purchases)")
print("   4. Product diversity score (# of unique categories)")
print("   5. Loyalty momentum (trend: increasing or decreasing visits)")
print("   6. Predicted next visit date (based on avg interval)")
print("   7. Upsell propensity (based on avg transaction growth)")
print("   8. Cross-sell opportunities (categories not yet purchased)")
print("   9. Communication responsiveness (SMS reply rate)")
print("   10. Staff preference strength (% visits with preferred budtender)")

print("\n" + "=" * 80)

