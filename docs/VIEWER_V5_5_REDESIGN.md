# IC Viewer v5.5 - Major Redesign

## Overview
Complete UI redesign based on user feedback. Version 5.5 features a dramatically improved layout with emphasis on the baseball card and better analytics.

## Launch
```bash
cd mota-crm/viewers
start_crm_blaze_v5_5.bat
```

## Major Changes from v5

### 1. Layout Redesign

#### Before (v5):
- Transactions: 350px height
- Baseball Card: 400px width
- Revenue by Brand: 400px width panel

#### After (v5.5):
- **Transactions: 200px height** (narrower - less vertical space)
- **Baseball Card: 700px width** (75% wider - star of the show!)
- **Visit Analytics: 400px width** (replaces brand panel)

### 2. Baseball Card Enhancements

**Now Includes**:
- All original customer info
- **TOP 5 BRANDS BY REVENUE** (with purchase counts!)
  ```
  💰 TOP BRANDS BY REVENUE
     1. MOTA                 $2,160.00 (23 purchases)
     2. Raw Garden            $890.00 (12 purchases)
     3. Lost Farm             $560.00 (8 purchases)
     4. Pax                   $420.00 (6 purchases)
     5. Stiiizy               $380.00 (11 purchases)
  ```
- Larger, more readable font
- Full height display

### 3. Visit Frequency Analytics (NEW!)

Replaces "Revenue by Brand" panel with rich analytics:

```
╔══════════════════════════════════════════╗
   VISIT FREQUENCY ANALYSIS
╚══════════════════════════════════════════╝

📊 OVERVIEW
   Total Visits:        45
   Days Active:         287 days
   Avg Visits/Month:    4.7
   First Visit:         2024-02-15
   Last Visit:          2025-11-09

📈 MONTHLY BREAKDOWN (Last 12 Months)

   2025-11    7 visits  ███████████████████████████████
   2025-10    5 visits  █████████████████████████
   2025-09    3 visits  ███████████████
   2025-08    4 visits  ████████████████████
   2025-07    6 visits  ████████████████████████████
   2025-06    2 visits  ██████████
   2025-05    5 visits  █████████████████████████
   2025-04    3 visits  ███████████████
   2025-03    4 visits  ████████████████████
   2025-02    4 visits  ████████████████████
   2025-01    1 visits  ████
   2024-12    1 visits  ████
```

**Features**:
- Visual bar chart (text-based)
- Monthly visit breakdown
- Days active calculation
- Average visits per month
- First and last visit dates

### 4. Display Menu (Column Toggle)

**Changed from panel toggle to column toggle**:
- ☑ First Name
- ☑ Last Name
- ☑ Date of Birth
- ☑ Phone
- ☑ Email
- ☑ SMS Opt-In
- ☑ Email Opt-In

**Features**:
- Instant column hide/show
- Saved per-user in `viewer_config_v5_5.json`
- Independent settings for each viewer version

### 5. Brand Revenue Fixes

**Fixed calculation bugs**:
- Now correctly calculates from `unit_price * quantity` if `total_price` is NULL
- Tracks COUNT of purchases per brand
- Top 5 instead of Top 3
- Shows both revenue AND purchase count

## File Structure

```
mota-crm/viewers/
├── crm_integrated_blaze_v5.py           # Original v5 (SAFE)
├── crm_integrated_blaze_v5_5.py         # NEW v5.5 (Redesigned)
├── start_crm_blaze_v5.bat               # Launch v5
├── start_crm_blaze_v5_5.bat             # Launch v5.5 (NEW)
├── viewer_config.json                   # v5 settings
└── viewer_config_v5_5.json              # v5.5 settings (NEW)
```

## Configuration

### v5.5 Config File
`viewer_config_v5_5.json` stores:
- Filter preferences (email, phone, date range)
- Visible columns (per Display menu)
- Column widths
- Window dimensions (future)

**Independent from v5**:
- Each version has its own config
- Changing columns in v5.5 doesn't affect v5
- Safe to run both simultaneously

## Comparison Chart

| Feature | v5 | v5.5 |
|---------|-----|------|
| **Transactions Height** | 350px | 200px (narrower) |
| **Baseball Card Width** | 400px | 700px (75% wider) |
| **Right Panel** | Revenue by Brand | Visit Frequency Analytics |
| **Brand Data Location** | Separate panel | IN baseball card |
| **Brand Count** | Top 3 | Top 5 with purchase counts |
| **Display Menu** | Panel toggle | Column toggle |
| **Config File** | viewer_config.json | viewer_config_v5_5.json |

## Benefits

### 1. Better Space Utilization
- Transactions panel doesn't need to be tall
- Baseball card gets most of the screen real estate
- Focus on customer insights, not just transactions

### 2. Richer Analytics
- Visit frequency chart shows patterns
- Monthly breakdown visualizes trends
- Days active shows customer longevity
- Replaces redundant brand panel

### 3. Cleaner Baseball Card
- Top 5 brands with purchase counts
- All key data in one place
- No need to scroll to brand panel
- Wider = more readable

### 4. User Customization
- Hide/show columns as needed
- Settings saved locally
- Independent config per version

## Technical Implementation

### Layout Changes
```python
# Transactions: height reduced from 350 to 200
parent.add(self.trans_frame, height=200)

# Baseball Card: width increased from 400 to 700
parent.add(self.detail_frame, width=700)

# Visit Frequency replaces Brand panel
self._create_visit_frequency_panel(bottom_paned)
```

### Brand Revenue Calculation Fix
```python
# Calculate from unit_price * quantity if total_price is NULL
price = item.get('total_price')
if price is None or price == 0:
    unit_price = item.get('unit_price', 0) or 0
    quantity = item.get('quantity', 1) or 1
    price = unit_price * quantity
```

### Visit Frequency Method
```python
def _load_visit_frequency(self, member_id):
    # Get transactions by date
    # Parse dates and group by month
    # Generate text-based bar chart
    # Show in new analytics panel
```

### Column Toggle System
```python
def _toggle_column(self, column_name):
    # Add/remove from visible_columns list
    # Save to config file
    # Refresh tree columns
    # Reload customer data
```

## Database Tables

**No changes from v5**:
- `customers_blaze`
- `transactions_blaze`
- `transaction_items_blaze`
- `products_blaze`

**Same Supabase connection**, just better UI.

## Performance

**v5.5 is FASTER than v5**:
- Fewer brand panel updates (data in baseball card now)
- Visit frequency uses simple date queries
- No change to customer/transaction loading

## Testing Checklist

### Visual Layout
- [ ] Transactions panel is narrower (200px height)
- [ ] Baseball card is wider (700px width)
- [ ] Visit analytics shows in right panel
- [ ] All panels visible on launch

### Baseball Card
- [ ] Shows top 5 brands with revenue
- [ ] Shows purchase counts per brand
- [ ] Brand totals are non-zero
- [ ] All original customer info still visible

### Visit Analytics
- [ ] Shows monthly bar chart
- [ ] Bars scale correctly
- [ ] Overview metrics accurate
- [ ] Last 12 months displayed

### Display Menu
- [ ] Purple "Display" button visible
- [ ] Checkboxes for all columns
- [ ] Toggling hides/shows columns
- [ ] Settings persist after restart

### Column Toggle
- [ ] Can hide First Name
- [ ] Can hide DOB
- [ ] Can hide Phone/Email
- [ ] Can hide Opt-ins
- [ ] Changes save to config_v5_5.json

## Known Issues

**None yet** - this is a fresh build!

## Future Enhancements

### Phase 1 (Near-term)
- [ ] Color-coded visit frequency (green = high, yellow = medium, red = low)
- [ ] Percentage of total spend per brand
- [ ] Save window dimensions
- [ ] Remember panel sizes

### Phase 2 (Mid-term)
- [ ] Export visit frequency chart as image
- [ ] Compare customers side-by-side
- [ ] Category breakdown (flower, edibles, vapes)
- [ ] Payment method analytics

### Phase 3 (Long-term)
- [ ] Interactive visit frequency chart (click month to see transactions)
- [ ] Predictive analytics (when will they visit next?)
- [ ] Cohort analysis (compare customer groups)
- [ ] Real-time updates (auto-refresh)

## Migration from v5

**No migration needed!**

v5.5 uses the same database, so:
1. Just launch `start_crm_blaze_v5_5.bat`
2. All your data is already there
3. Set your column preferences
4. Done!

**v5 stays intact** - run it anytime you want the old layout.

## User Feedback

Requested by user:
> "The transactions window doesn't need to be that wide. Make the baseball card the full length and full height. We need an awesome baseball card. Let's do revenue by brand on the baseball card. Let's explore making visit frequency chart or something better in that window."

**Result**: All requests implemented! 🎉

## Screenshots

[User to add screenshots showing new layout]

## Support

Having issues? Check:
1. **Config file**: Delete `viewer_config_v5_5.json` to reset
2. **Database**: Ensure Supabase credentials are correct
3. **v5 still works?**: If yes, v5.5 should work too
4. **Linter errors**: Run `read_lints` on crm_integrated_blaze_v5_5.py

---

**Created**: November 9, 2025  
**Version**: 5.5.0  
**Status**: Ready for Testing  
**Base**: v5 (kept safe)  
**Next**: User testing and feedback

