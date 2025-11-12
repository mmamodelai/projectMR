# Blaze API Integration Guide for AI Agents

## 🎯 **Purpose**
This guide helps AI agents understand how to work with the Blaze API for CRM data integration. The Blaze API provides real-time access to customer, transaction, and product data.

## 📁 **File Structure**
```
docs/BLAZEAPI/
├── blaze_api_summary.md     # This file - AI agent guide
├── swagger.json            # Complete API specification (23,874 lines)
└── README.md               # Quick reference for developers
```

## 🚨 **Important Notes for AI Agents**

### **Swagger.json Usage**
- **File size**: 23,874 lines - MASSIVE!
- **Purpose**: Complete API specification with all data models
- **When to use**: Only when you need detailed schema information
- **When NOT to use**: For quick endpoint lookups or basic integration

### **Search Strategy**
1. **Start with `blaze_api_summary.md`** for overview and key endpoints
2. **Use `swagger.json`** only when you need specific data model details
3. **Search patterns**: Look for endpoint paths, data models, or specific field definitions

## 🔑 **Key Integration Points**

### **Authentication**
```http
Headers Required:
- partner_key: Your Partner API key
- Authorization: Your Dispensary API key
```

### **Critical Endpoints for CRM**
- **Members**: `/api/v1/members` - Customer data
- **Orders**: `/api/v1/orders` - Transaction data  
- **Products**: `/api/v1/products` - Product catalog
- **Loyalty**: `/api/v1/loyalty` - Points and rewards

## 🔄 **Current System Integration**

### **Database Issues We're Solving**
- **Stale calculated fields** (days_since_last_visit, lifetime_value)
- **Data inconsistencies** (customer summaries vs transaction data)
- **Manual CSV imports** (not real-time)

### **Migration Strategy**
1. **Hybrid Approach**: Keep historical data, use API for new data
2. **Gradual Migration**: Update calculated fields from API data
3. **Real-time Updates**: Replace CSV imports with API sync

## 🛠️ **AI Agent Tasks**

### **When Working with Blaze API**
1. **Check `blaze_api_summary.md` first** for endpoint overview
2. **Use `swagger.json`** only for detailed schema information
3. **Focus on CRM-relevant endpoints** (members, orders, products)
4. **Consider data mapping** to existing Supabase schema

### **Common Tasks**
- **Data Discovery**: Map Blaze data structure to Supabase
- **Sync Scripts**: Build incremental update processes
- **Error Handling**: Handle API rate limits and authentication
- **Data Validation**: Ensure data consistency between systems

## 📊 **Data Mapping Considerations**

### **Blaze → Supabase Mapping**
- **Members** → `customers` table
- **Orders** → `transactions` table
- **Order Items** → `transaction_items` table
- **Products** → `products` table

### **Key Fields to Map**
- **Customer**: name, phone, email, vip_status, loyalty_points
- **Transaction**: date, total_amount, payment_type, staff_name
- **Product**: sku, name, brand, category, price

## 🚀 **Implementation Phases**

### **Phase 1: Discovery**
- [ ] Test API authentication
- [ ] Map data structures
- [ ] Identify data gaps

### **Phase 2: Hybrid Integration**
- [ ] Keep existing historical data
- [ ] Use API for new transactions
- [ ] Update calculated fields

### **Phase 3: Full Migration**
- [ ] Replace CSV imports
- [ ] Implement real-time updates
- [ ] Deprecate old processes

## 🔍 **Search Tips for AI Agents**

### **In swagger.json, look for:**
- **Endpoint paths**: Search for `/api/v1/` patterns
- **Data models**: Search for specific field names
- **Response schemas**: Look for `$ref` references
- **Parameter definitions**: Check required fields

### **Common Search Patterns**
```bash
# Find member endpoints
grep -i "member" docs/BLAZEAPI/swagger.json

# Find order endpoints  
grep -i "order" docs/BLAZEAPI/swagger.json

# Find specific data models
grep -i "Member" docs/BLAZEAPI/swagger.json
```

## ⚠️ **Important Warnings**

1. **Don't load entire swagger.json** into context unless absolutely necessary
2. **Use summary file first** for quick reference
3. **Focus on CRM-relevant endpoints** only
4. **Consider API rate limits** when building sync scripts
5. **Handle authentication errors** gracefully

## 📞 **Support Resources**

- **Blaze Support**: integrations@blaze.me
- **API Documentation**: Complete spec in `swagger.json`
- **Quick Reference**: `blaze_api_summary.md`

---

**Remember**: The swagger.json is comprehensive but massive. Use it strategically, not as your first reference point!
