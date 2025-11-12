# Blaze API Best Practices & Efficiency Guide

## 🎯 **Goal: Light Touch, Maximum Efficiency**

This guide ensures we use the Blaze API with the **lightest possible hand** while maintaining data accuracy and staying within rate limits.

## 📊 **Current Data Issues We're Solving**

### **Problems with CSV Import System**
- **Stale calculated fields**: `days_since_last_visit`, `lifetime_value`, `total_visits`
- **Data inconsistencies**: Customer summaries don't match transaction data
- **Manual processes**: CSV imports require human intervention
- **Delayed updates**: Data can be days/weeks old

### **Example: Arpine Tevanyan Data Conflict**
- **Customer table**: 3 visits, $2,010.75 lifetime value, 309 days since last visit
- **Transaction data**: 50 transactions, $1,016.79 total revenue, 111 days since last visit
- **Root cause**: Customer table calculated fields are stale

## 🔥 **Blaze API Solution Strategy**

### **Phase 1: Hybrid Approach (Recommended)**
**Keep existing data + Use API for new data**

#### **What We Keep**
- ✅ **22,509 customers** (historical data)
- ✅ **186,394 transactions** (historical data)
- ✅ **114,136 transaction items** (historical data)
- ✅ **All existing workflows** (IC Viewer, MotaBot, etc.)

#### **What We Replace**
- 🔄 **New transactions** → Blaze API sync
- 🔄 **Customer updates** → Blaze API sync
- 🔄 **Calculated fields** → Real-time calculation from API data
- 🔄 **Manual CSV imports** → Automated API sync

### **Phase 2: Optimization Strategy**

#### **API Call Optimization**
```python
# ✅ GOOD - Use modified dates for incremental sync
def sync_customers(last_sync_time):
    response = api.get_members(modified_after=last_sync_time)
    return response.data

# ❌ BAD - Fetch all customers every time
def sync_customers():
    response = api.get_members()  # Downloads 22K+ records!
    return response.data
```

#### **Sync Schedule (Following Blaze Rules)**
- **Customers**: Every hour (use `modified` date)
- **Transactions**: Every hour (batch processing)
- **Products**: Every 5 minutes (incremental updates)
- **Rate limit**: Max 10,000 calls per 5 minutes

#### **Data Mapping Strategy**
```python
# Map Blaze data to existing Supabase schema
BLAZE_TO_SUPABASE = {
    'members': 'customers',
    'orders': 'transactions', 
    'order_items': 'transaction_items',
    'products': 'products'
}

# Update calculated fields from API data
def update_customer_metrics(customer_id):
    transactions = get_transactions(customer_id)
    lifetime_value = sum(t['total_amount'] for t in transactions)
    last_visit = max(t['date'] for t in transactions)
    days_since = (datetime.now() - last_visit).days
    
    update_customer(customer_id, {
        'lifetime_value': lifetime_value,
        'days_since_last_visit': days_since,
        'total_visits': len(transactions)
    })
```

## 🚀 **Implementation Plan**

### **Step 1: API Discovery** (Current)
- [ ] Test authentication with Blaze credentials
- [ ] Map Blaze data structure to Supabase schema
- [ ] Identify data gaps and inconsistencies
- [ ] Test rate limits with sample calls

### **Step 2: Hybrid Sync Script**
- [ ] Build incremental sync for customers (hourly)
- [ ] Build batch sync for transactions (hourly)
- [ ] Build incremental sync for products (every 5 minutes)
- [ ] Update calculated fields from API data

### **Step 3: IC Viewer Updates**
- [ ] Modify IC Viewer to use live calculated fields
- [ ] Add API data freshness indicators
- [ ] Implement fallback to cached data if API unavailable

### **Step 4: Full Migration**
- [ ] Replace CSV import processes
- [ ] Implement real-time webhooks (if available)
- [ ] Deprecate old import scripts
- [ ] Monitor API usage and optimize

## 💰 **Cost Optimization**

### **Start Conservative**
- **Tier 1**: $100/month, 250K calls
- **Monitor usage** for first 90 days (no overage fees)
- **Optimize calls** before upgrading tiers

### **Call Volume Estimation**
```
Daily API calls needed:
- Customers (hourly): 24 calls
- Transactions (hourly): 24 calls  
- Products (every 5 min): 288 calls
- Total: ~336 calls/day = ~10K calls/month

Tier 1 (250K calls) = 25x headroom! ✅
```

## 🔧 **Technical Implementation**

### **Authentication**
```python
import requests

headers = {
    'partner_key': 'your_partner_key',
    'Authorization': 'your_dispensary_key',
    'Content-Type': 'application/json'
}
```

### **Incremental Sync Pattern**
```python
def sync_incremental(endpoint, last_sync_time):
    """Sync only records modified since last sync"""
    params = {
        'modified_after': last_sync_time.isoformat(),
        'limit': 1000  # Batch size
    }
    
    response = requests.get(f"{BASE_URL}/{endpoint}", 
                           headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"API call failed: {response.status_code}")
        return None
```

### **Error Handling**
```python
def safe_api_call(func, *args, **kwargs):
    """Handle rate limits and API errors gracefully"""
    try:
        return func(*args, **kwargs)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:  # Rate limited
            time.sleep(60)  # Wait 1 minute
            return func(*args, **kwargs)
        else:
            logger.error(f"API error: {e}")
            return None
```

## 📈 **Success Metrics**

### **Data Accuracy**
- ✅ **Calculated fields match transaction data**
- ✅ **Days since last visit accurate**
- ✅ **Lifetime value correct**
- ✅ **Customer preferences up-to-date**

### **System Performance**
- ✅ **API calls under rate limits**
- ✅ **Sync completes within time windows**
- ✅ **IC Viewer loads faster with live data**
- ✅ **No data inconsistencies**

### **Cost Efficiency**
- ✅ **Stay within Tier 1 limits**
- ✅ **Minimize API calls through optimization**
- ✅ **No overage fees**

## 🚨 **Important Warnings**

1. **Don't exceed rate limits** (10K calls per 5 minutes)
2. **Use modified dates** to avoid re-fetching unchanged data
3. **Batch API calls** efficiently
4. **Handle API errors** gracefully
5. **Monitor usage** to stay within tier limits
6. **Test thoroughly** before production deployment

## 📞 **Support Resources**

- **Blaze Support**: integrations@blaze.me
- **API Documentation**: `docs/BLAZEAPI/swagger.json`
- **Usage Rules**: `docs/BLAZEAPI/rules from blaze.md`
- **Quick Reference**: `docs/BLAZEAPI/blaze_api_summary.md`

---

**Remember**: The goal is **light touch, maximum efficiency**. We want to solve the data inconsistency problems while using the API as efficiently as possible!
