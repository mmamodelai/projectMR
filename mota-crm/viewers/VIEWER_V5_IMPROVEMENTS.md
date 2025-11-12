# IC Viewer v5 - Improvements Plan

## Changes Requested:

### 1. Remove "Latest Transactions" Button ✅
- Line 333: Delete the "💰 Latest Transactions" button
- User doesn't need it

### 2. Add "Display" Dropdown Menu ✅
- New dropdown with checkboxes to show/hide:
  - ☑ Transactions Panel
  - ☑ Items Panel  
  - ☑ Baseball Card
  - ☑ Revenue by Brand Panel
  - ☑ Customers Panel

### 3. Move "Revenue by Brand" Into Baseball Card ✅
- Currently separate panel on the right
- Integrate the top brands INTO the baseball card display
- Show it as part of "PURCHASE HABITS" section
- Keep the panel toggleable via Display menu

### 4. Better Use of Transactions Panel Space
- Add more data points:
  - Transaction count for selected customer
  - Total spent
  - Average per transaction
  - Payment method breakdown
  - Budtender breakdown

## Implementation:

### File to Edit:
`mota-crm/viewers/crm_integrated_blaze_v5.py`

### Changes:
1. Line 333: Remove Latest Transactions button
2. Line 333: Add Display dropdown menu
3. Lines 895-936: Update baseball card to include brand revenue inline
4. Add panel visibility toggles

### Brand Data to Show in Baseball Card:
```
📊 FAVORITE BRANDS
   Top 3:    MOTA (43%), Raw Garden (27%), Lost Farm (17%)
   Revenue:  $2,160 MOTA | $890 Raw Garden | $560 Lost Farm
```

This replaces the separate "REVENUE BY BRAND" panel or complements it.

