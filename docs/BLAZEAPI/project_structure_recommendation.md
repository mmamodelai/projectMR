# Blaze API Sync - Project Structure

## Recommended Structure

```
c:\Dev\conductor\
├── blaze-api-sync/              # NEW: Main project folder
│   ├── src/
│   │   ├── __init__.py
│   │   ├── api_client.py        # Blaze API client
│   │   ├── rate_limiter.py      # Rate limit enforcement
│   │   ├── sync_members.py
│   │   ├── sync_transactions.py
│   │   ├── sync_products.py
│   │   └── sync_state.py        # Track sync progress
│   ├── scripts/
│   │   ├── test_small_batch.py  # Test script (10 records)
│   │   └── sync_overnight.py    # Overnight sync script
│   ├── config/
│   │   ├── .env.example         # Template for credentials
│   │   └── config.json          # Supabase + Blaze config
│   ├── requirements.txt
│   ├── README.md
│   └── .gitignore
│
├── docs/
│   └── BLAZEAPI/                # KEEP: All documentation
│       ├── README.md
│       ├── migration_strategy.md
│       ├── safe_migration_plan.md
│       ├── data_mapping_audit.md
│       └── swagger.json
│
└── [other projects...]
```

## Why This Structure?

1. **Consistent with existing projects**: Like `conductor-sms/`, `mota-crm/`
2. **Self-contained**: Has own `requirements.txt`, config, README
3. **Easy to find**: Top-level folder, not buried in docs
4. **Separate workspace possible**: Can open `blaze-api-sync/` as its own Cursor project
5. **Shared resources**: Can still reference `docs/BLAZEAPI/` for documentation

## Alternative: Keep in docs but make it a proper project

If you prefer to keep docs together:

```
docs/BLAZEAPI/
├── sync/                        # Implementation code
│   ├── src/
│   ├── scripts/
│   ├── config/
│   ├── requirements.txt
│   └── README.md
├── [documentation files...]
└── swagger.json
```

## My Recommendation

**Go with Option 1** (`blaze-api-sync/` at root level):
- ✅ Matches your existing project structure
- ✅ Easier to navigate
- ✅ Can have dedicated Cursor workspace if needed
- ✅ Still shares database configs from main repo
- ✅ Docs stay organized in `docs/BLAZEAPI/`

## Next Steps

1. **Create folder structure** above
2. **Move implementation code** from `docs/BLAZEAPI/sandbox/` to `blaze-api-sync/src/`
3. **Create `requirements.txt`** with dependencies
4. **Create config** (can reference existing Supabase configs)
5. **Update docs** to reference new location

Want me to create this structure and move the existing code?



