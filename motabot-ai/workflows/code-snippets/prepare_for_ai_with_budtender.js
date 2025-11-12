// MotaBot v5.200: Enhanced with BUDTENDER DATA
// This code goes in the "Prepare for AI + CRM Data" node

const currentMessage = $input.item.json;
const phoneNumber = currentMessage.phone_number;
const incomingMessage = currentMessage.incoming_message;
const messageId = currentMessage.message_id;

const supabaseUrl = 'https://kiwmwoqrguyrcpjytgte.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0';

// Fetch conversation history (SMS messages)
let history = [];
try {
  const url = `${supabaseUrl}/rest/v1/messages?select=*&phone_number=eq.${phoneNumber}&order=timestamp.desc`;
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
  console.log('Could not fetch conversation history:', error);
}

// Fetch customer CRM data (basic profile)
let customerData = null;
let memberId = null;
try {
  const custUrl = `${supabaseUrl}/rest/v1/customers?phone=eq.${encodeURIComponent(phoneNumber)}&select=member_id,name,vip_status,total_visits,lifetime_value,last_visit_date&limit=1`;
  const custResponse = await fetch(custUrl, {
    method: 'GET',
    headers: {
      'apikey': supabaseKey,
      'Authorization': `Bearer ${supabaseKey}`,
      'Accept': 'application/json'
    }
  });
  
  if (custResponse.ok) {
    const custData = await custResponse.json();
    if (custData.length > 0) {
      customerData = custData[0];
      memberId = customerData.member_id;
    }
  }
} catch (error) {
  console.log('Could not fetch customer data:', error);
}

// NEW v5.200: Fetch BUDTENDER DATA
let budtenderData = null;
if (memberId) {
  try {
    // Get all transactions for this customer
    const txnUrl = `${supabaseUrl}/rest/v1/transactions?customer_id=eq.${memberId}&select=staff_name,total_amount`;
    const txnResponse = await fetch(txnUrl, {
      method: 'GET',
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Accept': 'application/json'
      }
    });
    
    if (txnResponse.ok) {
      const transactions = await txnResponse.json();
      
      // Count interactions with each budtender
      const budtenderStats = {};
      for (const txn of transactions) {
        const staffName = txn.staff_name;
        if (!staffName || staffName === 'Unknown' || staffName === '') {
          continue;
        }
        
        if (!budtenderStats[staffName]) {
          budtenderStats[staffName] = {
            name: staffName,
            transaction_count: 0,
            total_sales: 0.0
          };
        }
        
        budtenderStats[staffName].transaction_count += 1;
        budtenderStats[staffName].total_sales += parseFloat(txn.total_amount || 0);
      }
      
      // Find favorite budtender (most transactions)
      const budtenderList = Object.values(budtenderStats);
      if (budtenderList.length > 0) {
        budtenderList.sort((a, b) => b.transaction_count - a.transaction_count);
        const favoriteBudtender = budtenderList[0];
        const totalTransactions = transactions.length;
        const percentage = (favoriteBudtender.transaction_count / totalTransactions) * 100;
        
        budtenderData = {
          favorite: {
            name: favoriteBudtender.name,
            transaction_count: favoriteBudtender.transaction_count,
            percentage: Math.round(percentage * 10) / 10,
            total_sales: Math.round(favoriteBudtender.total_sales * 100) / 100
          },
          all: budtenderList.slice(0, 3) // Top 3 budtenders
        };
      }
    }
  } catch (error) {
    console.log('Could not fetch budtender data:', error);
  }
}

// Build conversation string with ALL context
let conversation = 'CONVERSATION HISTORY:\n\n';

if (history.length > 0) {
  history.reverse().forEach(msg => {
    const timestamp = new Date(msg.timestamp).toLocaleString();
    const role = msg.direction === 'inbound' ? 'Customer' : 'You (MotaBot)';
    conversation += `[${timestamp}] ${role}: ${msg.content}\n\n`;
  });
} else {
  conversation += 'No previous conversation history.\n\n';
}

// Add CRM context
if (customerData) {
  conversation += '\n=== CUSTOMER CRM DATA (from Supabase) ===\n';
  conversation += `Name: ${customerData.name || 'Unknown'}\n`;
  conversation += `VIP Status: ${customerData.vip_status || 'Regular'}\n`;
  conversation += `Total Visits: ${customerData.total_visits || 0}\n`;
  conversation += `Lifetime Value: $${customerData.lifetime_value || 0}\n`;
  conversation += `Last Visit: ${customerData.last_visit_date || 'N/A'}\n`;
  conversation += '\n';
}

// NEW v5.200: Add BUDTENDER context
if (budtenderData) {
  conversation += '\n=== FAVORITE BUDTENDER (from Transaction History) ===\n';
  const fav = budtenderData.favorite;
  conversation += `Name: ${fav.name}\n`;
  conversation += `Transactions: ${fav.transaction_count} (${fav.percentage}% of all visits)\n`;
  conversation += `Total Sales with ${fav.name}: $${fav.total_sales}\n`;
  
  if (budtenderData.all.length > 1) {
    conversation += `\nOther budtenders this customer has worked with:\n`;
    for (let i = 1; i < budtenderData.all.length; i++) {
      const bt = budtenderData.all[i];
      conversation += `  - ${bt.name} (${bt.transaction_count} visits)\n`;
    }
  }
  conversation += '\n';
}

conversation += '\nCURRENT MESSAGE (reply to this):\n';
conversation += `Customer: ${incomingMessage}\n\n`;
conversation += `Phone Number: ${phoneNumber}`;

return {
  json: {
    chatInput: conversation,
    phone_number: phoneNumber,
    message_id: messageId,
    customer_name: customerData?.name || null,
    vip_status: customerData?.vip_status || null,
    favorite_budtender: budtenderData?.favorite?.name || null,
    budtender_data: budtenderData || null
  }
};

