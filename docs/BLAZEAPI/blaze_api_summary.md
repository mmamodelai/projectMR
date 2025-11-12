# Blaze API - Key Endpoints Summary

## 🚨 **ISSUE: Original swagger.json is 23,874 lines!**

The full swagger file is **MASSIVE** because it contains hundreds of detailed data model definitions. This summary focuses on the key endpoints we need for CRM integration.

**📁 File Location**: `docs/BLAZEAPI/swagger.json` (complete specification)
**🤖 AI Agent Guide**: `docs/BLAZEAPI/README.md` (how to use this documentation)

## 🔑 **Authentication**
```http
Headers:
- partner_key: Your Partner API key
- Authorization: Your Dispensary API key
```

## 📊 **Key Endpoints We Need**

### **Customer/Member Management**
- `GET /api/v1/members` - Get all members
- `GET /api/v1/members/{id}` - Get specific member
- `POST /api/v1/members` - Create new member
- `PUT /api/v1/members/{id}` - Update member

### **Transaction/Order Data**
- `GET /api/v1/orders` - Get all orders
- `GET /api/v1/orders/{id}` - Get specific order
- `GET /api/v1/orders/member/{memberId}` - Get orders for member

### **Product/Inventory**
- `GET /api/v1/products` - Get all products
- `GET /api/v1/products/{id}` - Get specific product
- `GET /api/v1/inventory` - Get inventory levels

### **Loyalty/Points**
- `GET /api/v1/loyalty/member/{memberId}` - Get loyalty points
- `POST /api/v1/loyalty/points` - Add/remove points

## 🎯 **What We Need to Extract**

1. **Customer Data**: Name, phone, email, VIP status, loyalty points
2. **Transaction Data**: Date, amount, items, payment method, staff
3. **Product Data**: SKU, name, brand, category, price
4. **Real-time Updates**: Webhooks or polling for new transactions

## 🔄 **Migration Strategy**

### **Phase 1: Data Discovery**
- [ ] Test API authentication
- [ ] Map Blaze data structure to our Supabase schema
- [ ] Identify data gaps/inconsistencies

### **Phase 2: Hybrid Approach**
- [ ] Keep existing historical data
- [ ] Use Blaze API for new transactions going forward
- [ ] Update customer calculated fields from API data

### **Phase 3: Full Migration**
- [ ] Replace CSV imports with API sync
- [ ] Implement real-time updates
- [ ] Deprecate old import processes

## 📋 **Next Steps**

1. **Get API credentials** from Blaze
2. **Test authentication** with sample requests
3. **Map data structure** to our current schema
4. **Build sync script** for incremental updates
5. **Update IC Viewer** to use live data

## 🚨 **Current Database Issues**

- **Stale calculated fields** (days_since_last_visit, lifetime_value)
- **Data inconsistencies** (customer summaries vs transaction data)
- **Manual import process** (not real-time)

**Blaze API will solve these issues with live, accurate data!**

---

*Note: This is a summary of the 23,874-line swagger.json file. The full file contains hundreds of detailed data models and endpoints.*
