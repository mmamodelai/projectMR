# MotaBot v5.300: Database Query Agent Setup

## 🎯 **Goal**

Create an AI agent that can **actively query the Supabase database** to answer customer questions about their transaction history, purchases, spending, etc.

**Customer asks:** "What did I buy last time?"
**AI:** [Queries database] → "On Oct 9th you got Blue Dream 3.5g, LA Kush Cake vape, and a pre-roll!"

---

## 📋 **Architecture Overview**

```
SMS → Conductor → Supabase → n8n → AI Agent with Tools → Response → SMS
                                      ↓
                              [Tool: Query Transactions]
                              [Tool: Query Items]
                              [Tool: Search Products]
                              [Tool: Calculate Spending]
```

The AI now has **4 database query tools** it can use on-demand.

---

## 🔧 **How to Set Up in n8n**

### **Step 1: Create the AI Tools (Code Nodes)**

You need to create **4 separate Code nodes** that act as tools:

#### **Tool 1: Get Customer Transactions**

1. Add a **Code node**
2. Name it: `Get Customer Transactions Tool`
3. Set mode to: **"Define Tool"** (AI Agent tool mode)
4. Tool name: `get_customer_transactions`
5. Tool description: `Query customer transaction history by phone number`
6. Add parameters:
   - `phoneNumber` (string, required) - "Customer phone in E.164 format"
   - `limit` (number, optional, default 10) - "Max transactions to return"
7. Paste code from: `motabot-ai/workflows/code-snippets/supabase_query_tools.js` (lines 1-70)

#### **Tool 2: Get Transaction Items**

1. Add a **Code node**
2. Name it: `Get Transaction Items Tool`
3. Mode: **"Define Tool"**
4. Tool name: `get_transaction_items`
5. Description: `Get items purchased in a specific transaction`
6. Parameters:
   - `transactionId` (string, required) - "Transaction ID to look up"
7. Paste code from: `supabase_query_tools.js` (lines 72-145)

#### **Tool 3: Search Products Purchased**

1. Add a **Code node**
2. Name it: `Search Products Purchased Tool`
3. Mode: **"Define Tool"**
4. Tool name: `search_products_purchased`
5. Description: `Search what products a customer has purchased`
6. Parameters:
   - `phoneNumber` (string, required)
   - `searchTerm` (string, optional) - "Product name to search"
   - `category` (string, optional) - "Filter by category"
7. Paste code from: `supabase_query_tools.js` (lines 147-228)

#### **Tool 4: Calculate Spending**

1. Add a **Code node**
2. Name it: `Calculate Spending Tool`
3. Mode: **"Define Tool"**
4. Tool name: `calculate_spending`
5. Description: `Calculate total spending with optional date filtering`
6. Parameters:
   - `phoneNumber` (string, required)
   - `startDate` (string, optional) - "Start date YYYY-MM-DD"
   - `endDate` (string, optional) - "End date YYYY-MM-DD"
7. Paste code from: `supabase_query_tools.js` (lines 230-315)

---

### **Step 2: Update the AI Agent Node**

1. **Open your AI Agent node** (e.g., "MotaBot AI v5.300")
2. **Connect all 4 tool nodes** as inputs to the AI Agent
3. **Update system message** with content from `system_prompt_v5.300.txt`
4. **Ensure AI model** is set to a working model (e.g., `google/gemini-flash-1.5`)

---

### **Step 3: Simplify the "Prepare for AI" Node**

Since the AI now has tools to query data, you don't need to pre-fetch everything. Simplify:

```javascript
// v5.300: Simplified - AI uses tools for data lookup
const currentMessage = $input.item.json;
const phoneNumber = currentMessage.phone_number;
const incomingMessage = currentMessage.incoming_message;
const messageId = currentMessage.message_id;

const supabaseUrl = 'https://kiwmwoqrguyrcpjytgte.supabase.co';
const supabaseKey = 'YOUR_KEY_HERE';

// Fetch conversation history (still useful for context)
let history = [];
try {
  const url = `${supabaseUrl}/rest/v1/messages?select=*&phone_number=eq.${phoneNumber}&order=timestamp.desc&limit=20`;
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'apikey': supabaseKey,
      'Authorization': `Bearer ${supabaseKey}`,
      'Accept': 'application/json'
    }
  });
  
  if (response.ok) {
    history = await response.json();
  }
} catch (error) {
  console.log('Could not fetch history:', error);
}

// Build simple context
let conversation = 'CONVERSATION HISTORY:\n\n';
if (history.length > 0) {
  history.reverse().forEach(msg => {
    const timestamp = new Date(msg.timestamp).toLocaleString();
    const role = msg.direction === 'inbound' ? 'Customer' : 'You';
    conversation += `[${timestamp}] ${role}: ${msg.content}\n\n`;
  });
}

conversation += '\nCURRENT MESSAGE (use your tools to answer):\n';
conversation += `Customer: ${incomingMessage}\n`;
conversation += `Phone: ${phoneNumber}`;

return {
  json: {
    chatInput: conversation,
    phone_number: phoneNumber,
    message_id: messageId
  }
};
```

---

### **Step 4: Workflow Structure**

```
[Poll Supabase] 
  → [Filter Unread] 
    → [Prepare for AI] 
      → [AI Agent with 4 Tools]
        → [Prepare Response]
          → [Split Chunks]
            → [Delay]
              → [Send SMS]
                → [Mark Read]
```

---

## 🧪 **Testing**

### **Test Message 1: Transaction History**
```
What did I buy last time?
```

**Expected:**
- AI uses `get_customer_transactions` (limit=1)
- Then uses `get_transaction_items` for that transaction ID
- Responds: "On Oct 9th you got Blue Dream 3.5g, LA Kush Cake vape, and a pre-roll for $53!"

### **Test Message 2: Spending Query**
```
How much have I spent this year?
```

**Expected:**
- AI uses `calculate_spending` (startDate=2025-01-01)
- Responds: "You've spent $140.76 across 3 visits this year!"

### **Test Message 3: Product Search**
```
Have I bought Blue Dream before?
```

**Expected:**
- AI uses `search_products_purchased` (searchTerm="Blue Dream")
- Responds: "Yes! You bought Blue Dream 3.5g on Oct 9th!"

### **Test Message 4: History List**
```
Show me my last 5 purchases
```

**Expected:**
- AI uses `get_customer_transactions` (limit=5)
- Responds: "Your last 5 visits: Oct 9 ($53), Sept 22 ($87), Aug 15 ($42)..."

---

## 🎉 **Benefits of This Approach**

### **✅ Pros:**
1. **Dynamic queries** - AI fetches exactly what it needs
2. **No data overload** - Don't pre-fetch everything
3. **Accurate answers** - Real data, not hallucinations
4. **Scalable** - Works with 10,000+ customers
5. **Flexible** - AI decides which tool to use based on question

### **⚠️ Challenges:**
1. **Latency** - Multiple tool calls = slower response
2. **Token usage** - Each tool call costs tokens
3. **Error handling** - Tools can fail, AI needs to handle gracefully

---

## 📊 **Tool Usage Examples**

### **Scenario 1: Simple Question**
```
Customer: "What's my status?"
AI thinks: "No need for tools, I'll ask them to provide more context"
Response: "Hi! I can look up your visit history, spending, or purchases. What would you like to know?"
```

### **Scenario 2: Specific Query**
```
Customer: "How many times have I visited?"
AI: [Uses calculate_spending tool]
Response: "You've visited 3 times and spent $140.76 total!"
```

### **Scenario 3: Complex Query**
```
Customer: "What did I buy on my last 3 visits?"
AI: [Uses get_customer_transactions with limit=3]
AI: [Uses get_transaction_items for each transaction]
Response: "Visit 1 (Oct 9): Blue Dream, LA Kush vape. Visit 2 (Sept 22): Gorilla Glue, gummies. Visit 3 (Aug 15): Pre-rolls!"
```

---

## 🚀 **Next Steps**

1. **Create the 4 tool nodes** in n8n
2. **Test each tool individually** with manual inputs
3. **Connect tools to AI Agent**
4. **Update system prompt**
5. **Test with real SMS messages**
6. **Monitor for errors and latency**

---

## 📁 **File References**

- Tool code: `motabot-ai/workflows/code-snippets/supabase_query_tools.js`
- System prompt: `motabot-ai/workflows/code-snippets/system_prompt_v5.300.txt`
- This guide: `motabot-ai/docs/DATABASE_QUERY_AGENT_SETUP.md`

---

## 💡 **Pro Tips**

1. **Start simple** - Test with one tool first (get_customer_transactions)
2. **Monitor AI decisions** - Watch which tools it chooses to use
3. **Optimize later** - Once working, you can cache common queries
4. **Handle failures** - Make sure tools return useful error messages
5. **Keep responses brief** - AI should summarize, not dump raw data

---

**This is the real database-powered AI you wanted!** 🎊

