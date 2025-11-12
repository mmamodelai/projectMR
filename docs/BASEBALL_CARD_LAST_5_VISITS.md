# Baseball Card - Last 5 Visits Feature

**Added**: November 7, 2025  
**Version**: v5.0.3

---

## 🎯 New Feature: Last 5 Visits

Added a comprehensive visit history section to the Baseball Card showing:

### **Columns Displayed**:
1. **Date** - Transaction date (YYYY-MM-DD)
2. **Day** - Day of week (Mon, Tue, Wed, etc.)
3. **Time** - Time of visit (12-hour format with AM/PM)
4. **Budtender** - Who served them (resolved name)
5. **Spend** - Total transaction amount
6. **MOTA%** - Percentage of spend on MOTA products

---

## 📊 Example Output

```
📅 LAST 5 VISITS
   
   Date       Day Time     Budtender    Spend    MOTA
   --------------------------------------------------
   2025-11-05 Tue 02:30 PM Jimmy Sliks  $124.50   85%
   2025-11-03 Sun 10:15 AM Devon Calend $45.00   100%
   2025-10-28 Mon 04:45 PM Jimmy Sliks  $87.23    42%
   2025-10-22 Tue 11:20 AM Kevin Calend $210.00   91%
   2025-10-15 Tue 03:00 PM Jimmy Sliks  $56.78    67%
```

---

## 🔧 How It Works

### **Data Sources**:
- `transactions_blaze` table → Date, time, amount, seller_id
- `employees_blaze` table → Budtender names (via `_get_seller_name`)
- `transaction_items_blaze` table → Item brands and prices (for MOTA %)

### **MOTA Percentage Calculation**:
```python
MOTA % = (MOTA product spend / Total transaction spend) × 100
```

**Example**:
- Transaction total: $100
- MOTA products: $85
- Other brands: $15
- **MOTA % = 85%**

### **Key Methods Added**:

1. **`_get_last_visits(member_id, limit=5)`**
   - Fetches last N transactions for customer
   - Formats date, day, time
   - Resolves budtender names
   - Calculates MOTA percentage
   - Returns formatted table string

2. **`_calculate_mota_percentage(transaction_id)`**
   - Gets all items for transaction
   - Sums total spend
   - Sums MOTA brand spend
   - Returns percentage (0-100)

---

## 💡 Business Insights

### **What This Tells You**:

1. **Visit Frequency**
   - Gaps between dates → Engagement level
   - Same day visits → Irregular pattern?

2. **Day/Time Patterns**
   - Weekday vs weekend shopper?
   - Morning vs evening preference?
   - Peak time visitor?

3. **Budtender Relationships**
   - Same budtender repeatedly → Personal connection
   - Different budtenders → No preference
   - Can target campaigns via preferred budtender

4. **Spending Patterns**
   - Consistent amounts → Budget-conscious
   - Variable amounts → Impulse/special occasion
   - Increasing trend → Growing loyalty

5. **MOTA Loyalty**
   - High % consistently → Brand loyal (great for MOTA!)
   - Low % → Explores other brands (upsell opportunity)
   - Increasing % → Successful brand building

### **Use Cases**:

**High MOTA Customer** (75%+ average):
- ✅ Feature in MOTA loyalty program
- ✅ Send MOTA new product alerts
- ✅ Offer MOTA-specific discounts

**Low MOTA Customer** (0-25%):
- 🎯 Target with MOTA sampling campaign
- 🎯 Educate on MOTA quality/pricing
- 🎯 Bundle MOTA with preferred brands

**Specific Budtender Relationship**:
- 💬 Have budtender reach out personally
- 💬 Send message "Jimmy says hi, come see us!"
- 💬 Schedule budtender for customer's preferred times

---

## 📍 Baseball Card Layout (Updated)

```
╔════════════════════════════════════════════════════════╗
║              ⚾ BASEBALL CARD                           ║
╚════════════════════════════════════════════════════════╝

👤 John Smith
   39 years old • 36-45 • Recreational

📊 KEY STATS
   
   💰 Lifetime Value:        $3,247.89
   🎯 Total Visits:          42
   💵 Avg Transaction:       $77.33
   📅 Visits/Month:          2.3
   
   🏆 VIP
   🟢 Active (14 days)

🛒 PURCHASE HABITS
   
   Items/Transaction:  3.2
   Top Category:       Flower (87)
   Favorite Brands:    MOTA (42), Kiva (18), Jeeter (12)

📞 CONTACT
   
   Phone:  (619) 555-1234
   Email:  john@email.com
   
   SMS:   📱 Yes   Email: 📧 Yes

📅 LAST 5 VISITS                                    ← NEW!
   
   Date       Day Time     Budtender    Spend    MOTA
   --------------------------------------------------
   2025-11-05 Tue 02:30 PM Jimmy Sliks  $124.50   85%
   2025-11-03 Sun 10:15 AM Devon Calend $45.00   100%
   2025-10-28 Mon 04:45 PM Jimmy Sliks  $87.23    42%
   2025-10-22 Tue 11:20 AM Kevin Calend $210.00   91%
   2025-10-15 Tue 03:00 PM Jimmy Sliks  $56.78    67%

📅 TIMELINE
   
   Member Since:  2019-06-25
   Last Visit:    2025-11-05
   
╚════════════════════════════════════════════════════════╝
```

---

## 🎨 Formatting Details

### **Column Widths**:
- Date: 10 chars (YYYY-MM-DD)
- Day: 3 chars (Mon, Tue, etc.)
- Time: 8 chars (HH:MM AM/PM)
- Budtender: 12 chars (truncated if longer)
- Spend: 7 chars ($XXX.XX)
- MOTA%: 4 chars (XXX%)

### **Alignment**:
- Date: Left aligned
- Day: Right aligned (3 chars)
- Time: Right aligned (8 chars)
- Budtender: Left aligned (12 chars)
- Spend: Right aligned ($XXX.XX)
- MOTA%: Right aligned (XXX%)

### **Special Cases**:
- No visits: Shows "No visits recorded"
- Date parsing error: Shows "???" for day, "??:??" for time
- No items in transaction: Shows 0% MOTA
- Empty brand field: Doesn't count as MOTA

---

## 🚀 Performance Considerations

### **Database Queries**:
Per customer load:
1. Get last 5 transactions (1 query)
2. For each transaction, get items for MOTA % (5 queries max)

**Total**: ~6 queries per customer load

### **Optimization**:
- MOTA % calculated per-transaction (not per-item)
- Budtender names cached after first lookup
- Date parsing handles both ISO8601 and simple formats
- Efficient string formatting (no regex)

### **Typical Load Time**:
- Last 5 visits: ~0.5-1 second
- Acceptable for real-time display

---

## 🐛 Error Handling

### **Graceful Failures**:
- No transactions → "No visits recorded"
- Date parsing error → Shows raw date with "???" placeholders
- Budtender lookup fails → Shows seller_id
- Items query fails → Shows 0% MOTA
- Any exception → Shows error message in panel

**Philosophy**: Never crash, always show something useful!

---

## 📈 Future Enhancements

### **Possible Additions**:
- [ ] Expand to 10 visits (configurable)
- [ ] Color code MOTA % (green >75%, yellow 25-75%, red <25%)
- [ ] Add "Items" column (SKU count)
- [ ] Add "Payment" column (Cash/Credit)
- [ ] Click visit → load that transaction's items
- [ ] Chart MOTA % trend over time
- [ ] Compare to store average MOTA %
- [ ] Highlight unusual patterns (large spend, rare visit, etc.)

### **Analytics Possibilities**:
- Average MOTA % across all visits
- MOTA % trend (increasing/decreasing)
- Preferred shopping day/time
- Favorite budtender (most visits)
- Average basket size by day of week
- Spending velocity ($/day since join)

---

## ✅ Testing Checklist

- [x] Last 5 visits display correctly
- [x] Date formats properly (YYYY-MM-DD)
- [x] Day of week shows correctly (Mon-Sun)
- [x] Time shows 12-hour format with AM/PM
- [x] Budtender names resolve correctly
- [x] Spend amounts format with $ and 2 decimals
- [x] MOTA % calculates correctly (0-100%)
- [x] Table alignment is clean
- [x] No crashes on customers with < 5 visits
- [x] No crashes on customers with 0 visits
- [x] Performance acceptable (< 2 seconds)

---

## 📚 Code Reference

### **Main Function**:
```python
def _get_last_visits(self, member_id, limit=5):
    """Get last N visits with formatted details"""
    # 1. Query transactions (latest first)
    # 2. For each transaction:
    #    - Parse date/time
    #    - Resolve budtender name
    #    - Calculate MOTA %
    #    - Format line
    # 3. Return formatted table string
```

### **Helper Function**:
```python
def _calculate_mota_percentage(self, transaction_id):
    """Calculate % of transaction that was MOTA products"""
    # 1. Get all items for transaction
    # 2. Sum total spend
    # 3. Sum MOTA brand spend
    # 4. Return percentage
```

---

## 🎓 Key Takeaways

1. **Last 5 Visits = Mini Story**
   - Who, when, where, how much, what brands
   - Reveals patterns and relationships
   - Actionable insights for marketing

2. **MOTA % = Brand Loyalty Metric**
   - Quantifies brand preference
   - Identifies brand ambassadors
   - Highlights upsell opportunities

3. **Budtender Relationship Tracking**
   - Personal connections matter
   - Can personalize outreach
   - Scheduling optimization

4. **Day/Time Intelligence**
   - Shopping habit patterns
   - Campaign timing optimization
   - Staffing insights

**Result**: Complete customer intelligence at a glance! ⚾

---

**Status**: ✅ Implemented and Working  
**Version**: v5.0.3  
**Last Updated**: November 7, 2025


