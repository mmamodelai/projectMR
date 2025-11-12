# MotaBot Training Mode Instructions

## 🎯 Overview

This is a **training/testing version** of the MotaBot workflow that allows you to manually test the AI with different phone numbers without needing real SMS messages.

## 🔧 How to Use

### 1. Set Phone Number for Testing

1. Open the workflow in n8n
2. Find the **"Manual Phone Number Input"** node
3. Double-click to edit it
4. Change the phone number on this line:
   ```javascript
   const phoneNumber = '+16199773020'; // CHANGE THIS TO TEST DIFFERENT CUSTOMERS
   ```
5. Use any phone number from your database, for example:
   - `'+16199773020'` (default)
   - `'+16193683370'` (Stephen Clare)
   - `'+1234567890'` (any test number)

### 2. Trigger the Workflow

1. Use the **"When chat message received"** node (Chat Trigger)
2. Type any message you want to test with, for example:
   - "What are my points?"
   - "What did I buy last time?"
   - "What do you recommend?"
   - "Hello, I need help"

### 3. View Results

The workflow will:
1. Use your manually set phone number
2. Extract your test message from the chat
3. Format it with conversation context
4. Process through the AI with all available tools
5. Generate a personalized response
6. **Log the response to console** (instead of sending SMS)

### 4. Check the Logs

Look at the n8n execution logs to see:
- **"Log Training Response"** node output
- AI response for the customer
- Database queries performed
- Any errors or issues

## 🔄 Workflow Changes Made

### Original Flow:
```
SMS Poll → Filter → Prepare → AI → Queue SMS → Mark Read
```

### Training Flow:
```
Chat Trigger → Manual Phone Input → Format Context → AI → Log Response → Skip Mark Read
```

## 🎛️ Key Nodes

1. **"When chat message received"** - Chat trigger (enter test messages here)
2. **"Manual Phone Number Input"** - Set the phone number to test with (edit the code to change it)
3. **"Format Conversation Context"** - Prepares data for AI with proper chatInput
4. **"MotaBot AI"** - The AI agent with all Supabase tools
5. **"Log Training Response"** - Shows AI response in logs
6. **"Skip Mark as Read (Training)"** - Skips SMS database operations

## 🧪 Testing Different Scenarios

### Test Customer Data Lookup:
- Set phone to `'+16193683370'` (Stephen Clare)
- Ask: "What are my points?"
- Should return real customer data

### Test Product Recommendations:
- Set phone to any customer
- Ask: "What do you recommend?"
- Should query products database

### Test Transaction History:
- Set phone to customer with purchase history
- Ask: "What did I buy last time?"
- Should query transactions

## 📝 Recent Fixes (Oct 2025)

### Fixed chatInput Parsing Error
- **Issue**: "Failed to parse tool arguments from chat model response" 
- **Cause**: Chat trigger output wasn't being properly formatted into `chatInput` for the AI
- **Fix**: Updated Manual Phone Number Input to extract message correctly and Format Conversation Context to ensure `chatInput` is created properly

### Workflow Flow
The data now flows correctly:
```
Chat Input → Manual Phone Input (creates phone_number, incoming_message, all_messages) 
  → Format Conversation Context (creates chatInput from the data) 
  → MotaBot AI (receives chatInput expression: {{ $json.chatInput }})
```

## 🔄 Converting Back to Production

When you're ready to go back to production:

1. **Revert the connections**:
   - Chat Trigger → Filter Unread Messages (instead of Manual Phone Input)
   
2. **Change the response handling**:
   - Log Training Response → Queue Full Message (Supabase)
   - Skip Mark as Read → Mark as Read (Supabase)

3. **Enable SMS polling**:
   - Reconnect the "Poll Every 30s" trigger

## 📝 Notes

- **No real SMS sent** - All responses are logged only
- **Database queries work** - All customer/product lookups function normally
- **Easy to iterate** - Change phone number and test different scenarios
- **Safe testing** - No risk of sending unwanted SMS messages

## 🎯 Benefits

✅ **Fast iteration** - Test different customers instantly  
✅ **No SMS costs** - Test without sending real messages  
✅ **Easy debugging** - See all AI responses in logs  
✅ **Safe development** - No risk of customer confusion  
✅ **Real data** - Uses actual customer database  
✅ **Tool calling works** - Full access to all Supabase query tools

---

**Ready to test!** Just change the phone number in the "Manual Phone Number Input" node and trigger the chat!
