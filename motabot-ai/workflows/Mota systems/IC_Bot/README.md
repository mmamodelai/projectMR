# IC Bot - Internal Customers (Silverlake CRM)

**Purpose**: Customer service bot for MOTA Silverlake customers  
**Status**: Production Ready  
**Last Updated**: October 23, 2025

---

## 🎯 Overview

**IC Bot** is an intelligent customer service bot specifically designed for MOTA Silverlake customers. It provides personalized assistance by accessing customer purchase history, product recommendations, and inventory information.

### Key Features:
- ✅ **Customer Profile Lookup** - Instant customer data by phone number
- ✅ **Transaction History** - Complete purchase history from Supabase CRM
- ✅ **Product Recommendations** - Personalized suggestions based on past purchases
- ✅ **Inventory Checking** - Real-time product availability
- ✅ **Purchase Analysis** - Detailed transaction breakdowns

---

## 🚀 Quick Start

### 1. Import Workflow
1. Open n8n
2. Go to **Workflows** → **Import from File**
3. Select: `motabot-ai/workflows/Mota systems/IC_Bot/ICworking1_v2.0.json`
4. Configure Supabase credentials
5. Activate workflow

### 2. Test the Bot
Send SMS to your modem with a customer phone number, and the bot will:
1. Look up customer profile
2. Retrieve transaction history
3. Provide personalized recommendations
4. Check product availability

---

## 🔧 How It Works

### Customer Lookup Flow:
1. **Get Customer Profile** - Lookup by phone number
2. **Extract Customer ID** - Get UUID for further queries
3. **Get Transaction History** - Fetch all Silverlake purchases
4. **Get Transaction Items** - Detailed purchase breakdowns
5. **Product Recommendations** - Suggest similar products

### Tools Available:
- **Get Customer Profile** - Customer data lookup
- **Get Customer Transactions Silverlake** - Purchase history
- **Get Transaction Items** - Detailed line items
- **Get Product Details** - Specific product information
- **Get Available Products Silverlake** - Current inventory

---

## 📊 Database Integration

### Supabase CRM Tables:
- **`customers`** - Customer profiles (10,047 records)
- **`transactions`** - Purchase history (36,463 records)
- **`transaction_items`** - Line items (57,568 records)
- **`products`** - Product catalog (39,555 records)

### Key Data Points:
- Customer name, phone, email
- Loyalty points, VIP status
- Total visits, lifetime value
- Purchase patterns and preferences
- Favorite products and budtenders

---

## 🎛️ Configuration

### AI Model:
- **Default**: `anthropic/claude-3.5-haiku`
- **Provider**: OpenRouter
- **Purpose**: Fast, accurate customer service responses

### Response Guidelines:
- Always provide helpful, friendly responses
- Use purchase history for personalized recommendations
- Maintain professional, educational tone
- Focus on cannabis education and responsible use
- Verify phone numbers if customer not found

---

## 🧪 Testing

### Test Scenarios:
1. **Existing Customer**: Send SMS with known customer phone
2. **Product Inquiry**: Ask about specific products
3. **Purchase History**: Request transaction details
4. **Inventory Check**: Ask what's available
5. **New Customer**: Test with unknown phone number

### Expected Responses:
- Personalized greetings using customer name
- Relevant product suggestions based on history
- Accurate inventory information
- Professional, helpful tone throughout

---

## 🔗 Integration

### With Conductor SMS:
- Receives SMS messages via Conductor
- Processes customer inquiries
- Sends responses back through Conductor

### With Supabase CRM:
- Queries customer data in real-time
- Accesses complete transaction history
- Provides up-to-date product information

---

## 📁 File Structure

```
motabot-ai/workflows/Mota systems/IC_Bot/
├── ICworking1_v2.0.json          # Current production workflow
├── ICworking1.json               # Previous version
└── README.md                     # This file
```

---

## 🆘 Support

**GitHub**: https://github.com/mmamodelai/ConductorV4.1/issues  
**Documentation**: See main README.md for system overview

---

**🎉 IC Bot is production-ready! Intelligent customer service for MOTA Silverlake customers.**
