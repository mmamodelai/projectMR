# Project Reorganization - Questions Worksheet
**Fill this out BEFORE starting the reorganization**

---

## 🔧 Section 1: Conductor SMS

### Q1.1: API Server
**File**: `Olive/api_server.py`  
**What it does**: HTTP API for sending SMS  
**Currently used?**: Unknown  
**Decision**: 
- [ ] KEEP in conductor-sms (it's SMS-related)
- [ ] MOVE to separate `conductor-api` project
- [ ] DELETE (not needed, use Supabase directly)

**Your Answer**: _______________

---

### Q1.2: Cloudflare Tunnel Files
**Files**: `cloudflare_*.py`, `cloudflaretunnels/`, `start_tunnel.bat`  
**What they do**: Expose local services to internet  
**Currently used?**: For n8n webhooks?  
**Decision**:
- [ ] KEEP in conductor-sms
- [ ] MOVE to separate `infrastructure` project
- [ ] DELETE (using Supabase webhooks instead)

**Your Answer**: _______________

---

### Q1.3: Database Viewer in Conductor
**File**: `Olive/db_viewer.py`  
**What it does**: Views SMS messages from olive_sms.db  
**Decision**:
- [ ] KEEP in conductor-sms (views SMS messages)
- [ ] MOVE to mota-crm (consolidate all viewers)
- [ ] DELETE (use Supabase viewer instead)

**Your Answer**: _______________

---

### Q1.4: Flash SMS Tool
**Files**: Flash SMS sender scripts  
**What it does**: Sends flash SMS (appears on screen)  
**Currently used?**: Occasionally?  
**Decision**:
- [ ] KEEP in conductor-sms (it's SMS functionality)
- [ ] MOVE to separate `sms-tools` project
- [ ] DELETE (not used)

**Your Answer**: _______________

---

### Q1.5: Test and Demo Files
**Files**: `send_api_demo.py`, `test_*.py`  
**What they do**: Testing and demos  
**Decision**:
- [ ] KEEP in conductor-sms/tests/
- [ ] ARCHIVE (not needed in production)
- [ ] DELETE

**Your Answer**: _______________

---

## 📊 Section 2: MoTa CRM

### Q2.1: CSV Data Files
**Files**: `total_sales_products.csv` (93K rows), `MEMBER_PERFORMANCE.csv`, etc.  
**Size**: ~50MB total  
**Decision**:
- [ ] KEEP in repo (for re-imports)
- [ ] MOVE to external storage (too large)
- [ ] DELETE (already imported to Supabase)

**Your Answer**: _______________

---

### Q2.2: Import Scripts
**Files**: `import_*.py` in mota finance  
**What they do**: Import CSV → Supabase (one-time)  
**Decision**:
- [ ] KEEP in mota-crm/import_tools/ (for future imports)
- [ ] ARCHIVE (import complete, only for reference)
- [ ] DELETE (never needed again)

**Your Answer**: _______________

---

### Q2.3: Viewer Deployment
**Files**: `crm_integrated.py`, `inventory_viewer_fixed.py`, etc.  
**How to deploy?**:
- [ ] Keep as Python scripts (current)
- [ ] Create .exe with PyInstaller
- [ ] Create shortcuts only

**Your Answer**: _______________

---

### Q2.4: Desktop Shortcuts
**Want desktop shortcuts for viewers?**:
- [ ] YES - create shortcuts to batch files
- [ ] NO - launch from command line

**Your Answer**: _______________

---

### Q2.5: Diagnostic Scripts
**Files**: `check_*.py`, `diagnose_*.py`, `analyze_*.py`  
**What they do**: One-time debugging scripts  
**Decision**:
- [ ] KEEP in mota-crm/tools/
- [ ] ARCHIVE (for reference)
- [ ] DELETE (no longer needed)

**Your Answer**: _______________

---

## 🤖 Section 3: MotaBot AI

### Q3.1: Old Workflow Versions
**Files**: `MotaBot v4.3`, `MarketSuite v4.203`, etc.  
**Decision**:
- [ ] KEEP all versions (for history)
- [ ] KEEP last 3 versions only
- [ ] DELETE all except current (v5.100)

**Your Answer**: _______________

---

### Q3.2: Workflow Versioning
**Going forward, how to version?**:
- [ ] Semantic versioning in filename (v5.100, v5.101, etc.)
- [ ] Date-based (MotaBot_2025-10-11.json)
- [ ] Git commits only (single filename, track in git)

**Your Answer**: _______________

---

### Q3.3: n8n Setup Documentation
**Should we include n8n install/setup docs?**:
- [ ] YES - include full setup guide
- [ ] YES - link to official docs only
- [ ] NO - assume n8n is already set up

**Your Answer**: _______________

---

### Q3.4: n8n Local Data
**n8n Data Tables, credentials, etc.**:
- [ ] Document how to export/import
- [ ] Include exports in repo
- [ ] Not needed (cloud-based)

**Your Answer**: _______________

---

### Q3.5: Data Tables
**n8n Data Table Tool data**:
- [ ] KEEP using Data Tables
- [ ] MIGRATE to Supabase entirely
- [ ] Hybrid (some in Data Tables, some in Supabase)

**Your Answer**: _______________

---

## 🔗 Section 4: Shared Resources

### Q4.1: Supabase Credentials
**Where to store URL and API keys?**:
- [ ] In each project's config file (duplicated)
- [ ] In shared `config/` folder (single source)
- [ ] Environment variables only
- [ ] Git-ignored `.env` files in each project

**Your Answer**: _______________

---

### Q4.2: Shared Utilities
**Common code like `supabase_helpers.py`**:
- [ ] Duplicate in each project (copy)
- [ ] Create shared/ folder (import from common location)
- [ ] Publish as internal package
- [ ] Keep separate (small enough)

**Your Answer**: _______________

---

### Q4.3: Archive Folder
**Current `archive/` folder with old files**:
- [ ] KEEP as-is (reference for migration)
- [ ] MOVE to `project cleanup/archive/`
- [ ] DELETE (no longer needed)

**Your Answer**: _______________

---

### Q4.4: Master README
**Do we want one master README linking all projects?**:
- [ ] YES - create in root
- [ ] NO - each project standalone

**Your Answer**: _______________

---

### Q4.5: Repository Structure
**Git strategy**:
- [ ] Monorepo - 3 projects in subfolders
- [ ] Separate repos - 3 independent git repos
- [ ] Haven't decided yet

**Your Answer**: _______________

---

## 🔄 Section 5: Dependencies

### Q5.1: Conductor → CRM Schema Knowledge
**Does Conductor need to know about CRM database structure?**:
- [ ] YES - Conductor writes to both `messages` AND CRM tables
- [ ] NO - Conductor only writes to `messages` table

**Current Reality**: _______________

---

### Q5.2: MotaBot Local Dependencies
**Does MotaBot need local files/scripts?**:
- [ ] YES - needs local scripts
- [ ] NO - pure n8n workflow (cloud-based)

**Your Answer**: _______________

---

### Q5.3: Independent Operation
**Can each project run without the others?**:
- [ ] Conductor can run alone: YES / NO
- [ ] CRM viewers can run alone: YES / NO
- [ ] MotaBot can run alone: YES / NO

**Your Answers**: _______________

---

### Q5.4: Deployment Automation
**Do we want a "setup all" script?**:
- [ ] YES - one script sets up all 3
- [ ] NO - set up manually
- [ ] Maybe later

**Your Answer**: _______________

---

### Q5.5: Startup Order
**Does startup order matter?**:
- [ ] YES - must start in specific order
- [ ] NO - can start in any order
- [ ] Depends on use case

**If YES, what order**: _______________

---

## ✅ Completion Checklist

Before proceeding with reorganization:
- [ ] All 25 questions answered
- [ ] Answers reviewed and confirmed
- [ ] Decision makers have approved
- [ ] Backup plan in place
- [ ] Ready to execute Phase 1

---

## 📝 Notes / Additional Considerations

(Add any thoughts, concerns, or questions here)

_______________________________________________
_______________________________________________
_______________________________________________
_______________________________________________

---

**Completed By**: _______________  
**Date**: _______________  
**Status**: [ ] Draft [ ] Ready for Review [ ] Approved

