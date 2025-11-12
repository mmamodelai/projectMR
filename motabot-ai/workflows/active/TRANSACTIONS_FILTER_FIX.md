# Transaction Filter Fix - Customer-Specific Queries

## Problem
The "Get many rows in Supabase Transactions" node was pulling ALL transactions instead of filtering by the specific customer who sent the text message.

## Root Cause
- The `transactions` table has `customer_id` field but not direct `phone_number`, `name`, or `email` fields
- The workflow needs to first identify the customer, then filter transactions by their `customer_id`

## Solution Implemented

### 1. Added Customer ID Filtering
Updated the "Get many rows in Supabase Transactions" node to filter by `customer_id`:

```json
{
  "parameters": {
    "operation": "getAll",
    "tableId": "transactions",
    "filterType": "manual",
    "filters": {
      "conditions": [
        {
          "keyName": "customer_id",
          "condition": "equals",
          "keyValue": "={{ $json.customer_id }}"
        }
      ],
      "combineOperation": "any"
    }
  }
}
```

### 2. Required Workflow Sequence
Luis must now follow this sequence:

1. **Get Customer Info**: Use "Get many rows in Supabase Customers" with phone number
2. **Extract Customer ID**: Get the `customer_id` from the customer lookup
3. **Filter Transactions**: Use "Get many rows in Supabase Transactions" which now filters by `customer_id`
4. **Combine Data**: Merge customer info + their specific transactions

### 3. Updated System Prompt
The system prompt should include:

```
TOOLS & PROCESS (ALWAYS DO THIS FIRST):
When ANY customer texts you:
1. Use 'Customers Data Points' → Get name, points, email, visit history
2. Use 'Get many rows in Supabase Customers' → Find customer_id by phone number
3. Use 'Get many rows in Supabase Transactions' → Filter by customer_id from step 2
4. Combine all data for personalized response

IMPORTANT: The Transactions tool now filters by customer_id automatically. 
You must first get the customer_id from the Customers tool, then use that ID 
to get their specific transactions.
```

## Expected Behavior Now

**Before Fix:**
- Transactions node returned random transactions from all customers
- No way to connect transactions to the specific customer texting

**After Fix:**
- Transactions node only returns transactions for the specific customer
- Luis can provide personalized responses based on actual purchase history
- Customer gets relevant, specific information about their own transactions

## Example Flow

1. **Customer texts**: "+16199773020" → "What have I bought?"
2. **Luis uses Customers tool**: Searches by phone "+16199773020"
3. **Gets customer_id**: "68d5a09cc42d0732f14bcd67"
4. **Uses Transactions tool**: Filters by customer_id "68d5a09cc42d0732f14bcd67"
5. **Gets specific transactions**: Only Stephen's purchases
6. **Luis responds**: "Hey Stephen! You've bought OG Kush ($18.84) and Blue Dream ($56.89) recently. Want more of either?"

## Files Modified
- `motabot-ai/workflows/active/supabaseimport_LEAFLY_ENHANCED.json`
  - Added filtering parameters to "Get many rows in Supabase Transactions" node
  - Updated system prompt instructions

## Testing
1. Re-import the workflow
2. Send a test message from a known customer phone number
3. Verify that Luis only gets transactions for that specific customer
4. Confirm responses are personalized and relevant


