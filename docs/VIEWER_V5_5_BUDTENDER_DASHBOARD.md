# IC Viewer v5.5 - Live Budtender Dashboard

## 🎯 Overview
A real-time performance tracking system for budtenders, designed to drive the right behaviors: **more SKUs per transaction** and **higher % MOTA products**.

## 📊 Features

### Tab 1: Customers (Existing)
- All existing customer view functionality
- Transaction history
- Baseball card
- Visit analytics

### Tab 2: Live Budtender Dashboard (NEW!)

#### Real-Time Metrics (Last 30 Days)
For each budtender, the dashboard shows:

1. **Transaction Count** - Total completed transactions
2. **Avg $ Value** - Average transaction amount
3. **Items/Trans** - Average SKUs (unique products) per transaction
4. **% MOTA** - Percentage of revenue from MOTA products
5. **VS Store Avg** - Performance compared to team average
6. **Shift Status** - Active (🟢) if transaction in last 30 mins, or "Idle (Xm)"

#### Color Coding
- **🔵 Cyan (Active)** - Currently active (transaction in last 30 mins)
- **🟢 Green (Above Avg)** - Both items/trans AND MOTA% above store average
- **🔴 Red (Below Avg)** - Either items/trans OR MOTA% below store average
- **⚪ Normal** - Meets store average

#### Store Statistics
Bottom of dashboard shows:
- Total transactions (30d)
- Total revenue (30d)
- Store average transaction value
- Store average items per transaction
- Store average MOTA percentage

## 🔴 Live Updates
- **Auto-refresh**: Updates every 60 seconds (toggleable)
- **Manual refresh**: Click "🔄 REFRESH NOW" button
- **Live indicator**: Shows "● LIVE" (green) when auto-refresh is on

## 💡 Business Intelligence

### What Makes a Good Budtender?
1. **High Items/Trans** - Upselling multiple products
2. **High % MOTA** - Pushing house brand
3. **Above Store Avg** - Outperforming the team

### Example Scenarios

**Scenario 1: Star Performer**
- 50 transactions
- $75 avg value
- 3.5 items/trans (store avg: 2.8)
- 45% MOTA (store avg: 30%)
- **Result**: GREEN (above avg)

**Scenario 2: Needs Coaching**
- 30 transactions
- $60 avg value
- 2.1 items/trans (store avg: 2.8)
- 15% MOTA (store avg: 30%)
- **Result**: RED (below avg)

**Scenario 3: Currently Working**
- 15 transactions
- Last transaction: 10 minutes ago
- **Result**: CYAN (active)

## 🎓 Training Opportunities

### Use Dashboard to Identify:
1. **Low Items/Trans** → Train on upselling and cross-selling
2. **Low % MOTA** → Emphasize house brand benefits
3. **Low Transaction Count** → Check efficiency or shift coverage
4. **Inconsistent Performance** → Compare active vs. idle periods

### Coaching Metrics:
- Compare budtender to store average
- Track improvement over time (run reports daily/weekly)
- Celebrate top performers (green)
- Support underperformers (red)

## 🔧 Technical Details

### Data Sources
- `transactions_blaze` - Transaction history, amounts, budtender IDs
- `transaction_items_blaze` - Items, brands, prices, quantities
- `employees_blaze` - Budtender names

### Calculations
- **Items/Trans**: Count of unique `product_name` per transaction (SKUs, not quantity)
- **% MOTA**: `(MOTA revenue / total revenue) * 100`
- **Active Status**: Transaction within last 30 minutes
- **Store Avg**: Mean of all budtenders' metrics

### Performance
- Batch queries (500 transactions at a time)
- Caches budtender names
- Efficient set operations for unique SKU counting
- ~3-5 seconds to load 30 days of data

## 📈 Recommended Usage

### Daily
- Check at start of day to see previous day's performance
- Monitor during shifts to see who's active
- Identify coaching opportunities in real-time

### Weekly
- Compare weekly averages
- Track improvement trends
- Recognize top performers

### Monthly
- Full 30-day view shows comprehensive performance
- Identify consistent patterns
- Set goals for next month

## 🚀 Future Enhancements (Ideas)
- Export to CSV
- Historical comparison (this month vs. last month)
- Individual budtender drill-down
- Customer satisfaction correlation
- Hourly performance breakdown
- Goal setting and progress tracking

---

**Created**: 2025-11-10
**Version**: 5.5
**Author**: Cursor AI + Luis (Owner)

