================================================================================
  PRODUCTION PACKAGES - CLIENT DEPLOYMENT
================================================================================

This folder contains production-ready packages for client deployment.

Each subfolder is a complete, standalone application ready to ship.

================================================================================
  PACKAGES INCLUDED
================================================================================

1. SMS_Conductor_DB_Windows/
   --------------------------
   SMS Campaign Management System - WINDOWS VERSION
   - View, reply, approve, and schedule SMS campaigns
   - Live Mode with auto-refresh
   - Human-in-the-loop approval system
   - Always displays Pacific Time
   - Windows 10/11 compatible
   - Includes standalone EXE (no Python needed!)
   
   See: SMS_Conductor_DB_Windows/README.txt

2. SMS_Conductor_DB_Mac/
   ----------------------
   SMS Campaign Management System - MAC VERSION
   - View, reply, approve, and schedule SMS campaigns
   - Live Mode with auto-refresh
   - Human-in-the-loop approval system
   - Always displays Pacific Time
   - macOS 10.14+ compatible
   - Auto-installing launcher script
   
   See: SMS_Conductor_DB_Mac/README.txt

3. MOTA_CRM_Viewer/
   -----------------
   Internal Customer Management System
   - View customer profiles (baseball cards)
   - Purchase history and analytics
   - Product affinity tracking
   - Visit patterns
   
   See: MOTA_CRM_Viewer/README.txt

4. Dispensary_Viewer/
   ------------------
   Dispensary & Budtender Management
   - View dispensary information
   - Budtender profiles and points
   - Store-level analytics
   
   See: Dispensary_Viewer/README.txt

================================================================================
  DEPLOYMENT PROCESS
================================================================================

1. Select the package you want to deploy (Windows or Mac)
2. Review the README.txt in that folder
3. Package the entire folder as ZIP
4. Send to client with installation instructions
5. Client extracts and follows README.txt

================================================================================
  QUICK DEPLOYMENT CHECKLIST
================================================================================

For SMS_Conductor_DB_Windows:
[ ] Verify all files are in SMS_Conductor_DB_Windows/ folder
[ ] Check that CRITICAL_SQL_SETUP.md is included
[ ] Test START_SMS_VIEWER.bat
[ ] Test SMSConductorDB_v1.1.exe (standalone)
[ ] Verify requirements.txt is present
[ ] Create ZIP: SMS_Conductor_DB_Windows_v1.0.zip
[ ] Send to client with Windows installation guide

For SMS_Conductor_DB_Mac:
[ ] Verify all files are in SMS_Conductor_DB_Mac/ folder
[ ] Check that CRITICAL_SQL_SETUP.md is included
[ ] Test START_SMS_VIEWER.sh
[ ] Verify requirements.txt is present
[ ] Verify MAC_INSTALLATION_GUIDE.md is included
[ ] Create ZIP: SMS_Conductor_DB_Mac_v1.0.zip
[ ] Send to client with Mac installation guide

For MOTA_CRM_Viewer:
[ ] Verify all files are in MOTA_CRM_Viewer/ folder
[ ] Test start_viewer.bat
[ ] Verify requirements.txt is present
[ ] Create ZIP: MOTA_CRM_Viewer_v5.5.zip
[ ] Send to client

For Dispensary_Viewer:
[ ] Verify all files are in Dispensary_Viewer/ folder
[ ] Test start_viewer.bat
[ ] Verify requirements.txt is present
[ ] Create ZIP: Dispensary_Viewer_v1.0.zip
[ ] Send to client

================================================================================
  FILE STRUCTURE
================================================================================

production/
├── SMS_Conductor_DB_Windows/
│   ├── SMSconductor_DB.py
│   ├── START_SMS_VIEWER.bat
│   ├── SMSConductorDB_v1.1.exe (standalone)
│   ├── requirements.txt
│   ├── README.txt
│   ├── CRITICAL_SQL_SETUP.md
│   └── [Windows-specific files]
│
├── SMS_Conductor_DB_Mac/
│   ├── SMSconductor_DB.py
│   ├── START_SMS_VIEWER.sh
│   ├── START_VIEWER_MAC.command
│   ├── requirements.txt
│   ├── README.txt
│   ├── CRITICAL_SQL_SETUP.md
│   ├── MAC_INSTALLATION_GUIDE.md
│   └── [Mac-specific files]
│
├── MOTA_CRM_Viewer/
│   ├── crm_integrated_blaze_v5_5.py
│   ├── start_viewer.bat
│   ├── requirements.txt
│   └── README.txt
│
├── Dispensary_Viewer/
│   ├── dispensary_viewer.py
│   ├── start_viewer.bat
│   ├── requirements.txt
│   └── README.txt
│
└── README.txt (this file)

================================================================================
  NOTES
================================================================================

- Each package is self-contained and platform-specific
- Windows package includes standalone EXE (no Python needed)
- Mac package includes auto-installing launcher script
- All dependencies listed in requirements.txt
- Installation instructions in each README.txt
- Tested and production-ready
- Version controlled in Git

================================================================================

Last Updated: November 11, 2025
