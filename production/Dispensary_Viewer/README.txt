===============================================
Dispensary & Budtender Viewer
===============================================
EXTERNAL DATABASE VIEWER - Safe for distribution

DESCRIPTION:
-----------
Database viewer for managing dispensary locations and budtender information.
Features:
- View all dispensaries and locations
- Budtender contact information
- Filter by dispensary
- Search by name, phone, or email
- Export capabilities (future feature)

QUICK START:
-----------
1. Double-click "start_viewer.bat"
2. Select a dispensary from the dropdown
3. Browse budtender information
4. Use search to find specific contacts

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
- **Dispensary Filter**: View budtenders by location
- **Search**: Find by name, phone, or email
- **Contact Info**: Phone numbers, emails, and roles
- **Clean UI**: Dark theme, easy-to-read interface
- **Cloud Sync**: Real-time data from Supabase

TECHNICAL INFO:
--------------
File: dispensary_viewer.py
Database: Supabase (budtenders table)
Updates: Real-time from cloud database
Version: 1.0 (2025)

TROUBLESHOOTING:
---------------
- If viewer won't load: Check internet connection
- If no data appears: Verify Supabase credentials
- If Python error: Reinstall requirements.txt
- If search doesn't work: Try refreshing the data

DATA STRUCTURE:
--------------
Budtenders table columns:
- name: Budtender full name
- dispensary: Location name
- phone: Contact phone number
- email: Contact email address
- role: Job title/position

SUPPORT:
-------
Contact: SMS Conductor support team
Documentation: See main repository

===============================================
Last Updated: November 10, 2025

