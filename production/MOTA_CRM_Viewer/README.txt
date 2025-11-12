===============================================
MOTA CRM - Customer Viewer v5.5
===============================================
INTERNAL USE ONLY - Do NOT distribute externally

DESCRIPTION:
-----------
Advanced customer analytics and performance dashboard for MOTA dispensaries.
Features:
- Customer "baseball cards" with lifetime stats
- Visit frequency analytics
- Budtender performance tracking
- Category spending breakdowns
- Top brands and items analysis
- Real-time transaction viewing

QUICK START:
-----------
1. Double-click "start_viewer.bat"
2. Wait for window to load (may take 10-15 seconds)
3. Select a customer from the list
4. View their complete profile and history

REQUIREMENTS:
------------
- Python 3.8+
- Internet connection (connects to Supabase cloud database)
- Supabase credentials (embedded in script)

FIRST-TIME SETUP:
----------------
1. Install Python dependencies:
   pip install -r requirements.txt

2. Run the viewer:
   start_viewer.bat

FEATURES:
---------
- **Customer List**: Sortable by name, last visit, lifetime value
- **Baseball Card**: Complete customer overview with stats
- **Visit Analytics**: Monthly visit frequency and patterns
- **Budtender Dashboard**: Live performance metrics (last 30 days)
- **Transaction Details**: Clickable transactions show items
- **Display Options**: Toggle columns on/off as needed

TECHNICAL INFO:
--------------
File: crm_integrated_blaze_v5_5.py
Database: Supabase (customers_blaze, transactions_blaze, transaction_items_blaze)
Updates: Real-time from cloud database
Version: 5.5 (November 2025)

TROUBLESHOOTING:
---------------
- If viewer won't load: Check internet connection
- If data looks old: Click "Refresh" button
- If Python error: Reinstall requirements.txt
- If slow loading: Initial load fetches last 100 visitors (normal)

SUPPORT:
-------
Contact: Internal IT / Development team
Documentation: See WORKLOG.md in main repository

===============================================
Last Updated: November 10, 2025

