# Database Directory

This directory is intentionally kept empty.

## Why This Folder Exists

The `database/` directory is referenced in `config.json` and the conductor code for **SQLite fallback support**:

```json
{
  "database": {
    "path": "database/olive_sms.db",  ← Points to this directory
    "use_supabase": true
  }
}
```

## Current Database: Supabase ☁️

The Conductor SMS system is currently configured to use **Supabase** (cloud database), not local SQLite.

See `SUPABASE_DATABASES_OVERVIEW.md` in the project root for complete database documentation.

## SQLite Fallback (Not Currently Used)

If `use_supabase` is set to `false` in `config.json`, the system will fall back to a local SQLite database in this directory.

**When would you use SQLite?**
- Supabase is down or unreachable
- Testing without internet connection
- Local development without cloud access

## Archive

The previous SQLite database (`olive_sms.db` with 151 old messages) was archived on **October 12, 2025** to:

```
project cleanup/archive/sqlite_backup_2025-10-12/
```

It can be restored if needed, but it contains stale data from October 7, 2025.

## Summary

- ✅ Keep this folder (code expects it)
- ❌ No database file needed (using Supabase)
- 🔄 SQLite support remains in code (good for fallback)
- ☁️ All production data is in Supabase

**Last Updated**: October 12, 2025

