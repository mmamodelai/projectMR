# Supabase Integration - Quick Start Guide

## 🎯 What You Have Now

Your Supabase project **`smsconductor`** is ready at:
- **URL**: `https://kiwmwoqrguyrcpjytgte.supabase.co`
- **Region**: East US (Ohio)
- **Status**: Active ✅

## 📋 Quick Start (5 Steps)

### Step 1: Create the Database Table (2 minutes)

1. Go to Supabase Dashboard: https://supabase.com/dashboard/project/kiwmwoqrguyrcpjytgte
2. Click **SQL Editor** (left sidebar)
3. Click **New Query**
4. Open `Olive/supabase_setup.sql` in this project
5. Copy the entire file and paste into Supabase SQL Editor
6. Click **Run** (or Ctrl+Enter)
7. You should see: ✅ **Success. No rows returned**

### Step 2: Get Your Service Role Key (1 minute)

1. In Supabase Dashboard, click **Settings** (gear icon, bottom left)
2. Click **API** in the left menu
3. Scroll to **Project API keys**
4. Find **`service_role`** and click **Reveal** then **Copy**
5. Open `Olive/supabase_config.json`
6. Replace `"YOUR_SERVICE_ROLE_KEY_HERE"` with your copied key
7. Save the file

### Step 3: Install Python Package (1 minute)

```powershell
cd C:\Dev\conductor\Olive
pip install supabase
```

### Step 4: Test the Connection (1 minute)

```powershell
cd C:\Dev\conductor\Olive
.\test_supabase.bat
```

You should see:
```
✅ Configuration loaded
✅ Supabase client initialized
✅ Messages table exists
✅ Test message inserted
✅ All Tests Passed!
```

### Step 5: Migrate Your Existing Messages (Optional, 1 minute)

If you want to keep your 150 existing messages:

```powershell
cd C:\Dev\conductor\Olive
.\migrate_supabase.bat
```

## 🎉 What This Gives You

### Before (Current System):
```
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌────────┐
│ n8n.io  │────▶│ Cloudflare│────▶│  Flask  │────▶│ SQLite │
│ (cloud) │     │  Tunnel   │     │   API   │     │ (local)│
└─────────┘     └──────────┘     └─────────┘     └────────┘
```
**Issues**:
- Cloudflare tunnel can disconnect
- Flask API server must run 24/7
- SQLite limited to 1 connection
- No real-time updates
- Manual backups

### After (Supabase):
```
┌─────────┐     ┌──────────┐
│ n8n.io  │────▶│ Supabase │
│ (cloud) │     │  (cloud) │
└─────────┘     └──────────┘
       ▲               ▲
       │               │
┌──────┴──────┐        │
│  Conductor  │────────┘
│   (local)   │
└─────────────┘
```
**Benefits**:
- ✅ No tunnel needed
- ✅ No API server needed
- ✅ Direct n8n connection
- ✅ Real-time updates
- ✅ Automatic backups
- ✅ 100+ concurrent connections
- ✅ Better performance (50-150ms vs 200-500ms)

## 📊 What You Can Do in Supabase Dashboard

### Table Editor
View all your SMS messages in real-time:
1. Click **Table Editor** (left sidebar)
2. Select **messages** table
3. See all messages with filters and search

### SQL Editor
Run custom queries:
```sql
-- Get all unread messages
SELECT * FROM messages 
WHERE status = 'unread' 
AND direction = 'inbound'
ORDER BY timestamp DESC;

-- Count messages by status
SELECT status, COUNT(*) as count 
FROM messages 
GROUP BY status;

-- Find messages from a specific phone
SELECT * FROM messages 
WHERE phone_number = '+16199773020'
ORDER BY timestamp DESC;
```

### API Docs
Auto-generated REST API documentation:
1. Click **API Docs** (left sidebar)
2. See all available endpoints
3. Copy example code for Python, JavaScript, etc.

## 🔧 Next Steps

### Option A: Test with Dual-Write (Recommended)
Keep SQLite and add Supabase - safest for testing:

1. Update `Olive/config.json` - add this to the `database` section:
```json
{
  "database": {
    "path": "database/olive_sms.db",
    "use_supabase": true,
    "supabase_config": "supabase_config.json"
  }
}
```

2. Restart conductor:
```powershell
# Stop current conductor (Ctrl+C)
cd C:\Dev\conductor\Olive
.\start_conductor.bat
```

3. Send a test message and check both:
   - SQLite: `.\start_db_viewer.bat`
   - Supabase: Table Editor in dashboard

### Option B: Supabase Only (Production)
Once you're confident it works:

1. Update `Olive/config.json`:
```json
{
  "database": {
    "use_supabase_only": true,
    "supabase_config": "supabase_config.json"
  }
}
```

2. Stop old services:
```powershell
# Stop API server
Get-Process | Where-Object {$_.CommandLine -like "*api_server*"} | Stop-Process

# Stop Cloudflare tunnel
Get-Process | Where-Object {$_.ProcessName -eq "cloudflared"} | Stop-Process
```

3. Update n8n workflows to use Supabase nodes (see `SUPABASE_INTEGRATION_GUIDE.md`)

## 📚 Documentation

- **Full Guide**: `Olive/SUPABASE_INTEGRATION_GUIDE.md`
- **SQL Schema**: `Olive/supabase_setup.sql`
- **Test Script**: `Olive/test_supabase_connection.py`
- **Migration Script**: `Olive/migrate_to_supabase.py`

## 🆘 Troubleshooting

### "Failed to load configuration"
- Check that `Olive/supabase_config.json` exists
- Make sure you updated the `service_role_key`

### "Messages table not found"
- Run `supabase_setup.sql` in Supabase SQL Editor
- Check that you're in the correct project

### "Authentication failed"
- Verify your `service_role_key` is correct
- Go to Project Settings > API and copy it again

### "pip install supabase" fails
- Try: `pip install --upgrade pip`
- Then: `pip install supabase`

## 💡 Pro Tips

1. **Bookmark your Supabase dashboard**: https://supabase.com/dashboard/project/kiwmwoqrguyrcpjytgte
2. **Use Table Editor for quick checks** - faster than SQL queries
3. **Enable real-time in n8n** - Supabase can push updates to n8n automatically
4. **Set up database backups** - Supabase Settings > Database > Backups
5. **Monitor API usage** - Project Settings > Usage

## 🎊 Ready to Go!

Your Supabase database is configured and ready. Follow the 5 steps above and you'll have a cloud-powered SMS system in under 10 minutes!

---

**Project**: smsconductor  
**Region**: East US (Ohio)  
**Database**: PostgreSQL 15  
**Status**: Ready ✅

