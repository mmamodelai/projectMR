# Blaze API Sync - Final Structure Recommendation

## Decision: Keep in Main Project (Nested)

**Reasoning**: Blaze sync FILLS the database, other projects READ from it. Keep together for simplicity.

## Recommended Structure

```
c:\Dev\conductor\
├── blaze-api-sync/              # NEW: Implementation (top-level folder)
│   ├── src/
│   │   ├── api_client.py        # Blaze API client
│   │   ├── rate_limiter.py      # Rate limit enforcement
│   │   ├── sync_members.py      # Sync customers_blaze table
│   │   ├── sync_transactions.py # Sync transactions_blaze table
│   │   ├── sync_products.py     # Sync products_blaze table
│   │   └── sync_state.py        # Track sync progress
│   ├── scripts/
│   │   ├── test_small_batch.py  # Test script (10 records)
│   │   └── sync_overnight.py    # Overnight sync script
│   ├── config/
│   │   └── config.json          # References shared Supabase config
│   ├── requirements.txt
│   └── README.md
│
├── conductor-sms/               # READS from customers_blaze, transactions_blaze
├── mota-crm/                    # READS from customers_blaze, transactions_blaze
├── motabot-ai/                  # READS from customers_blaze, transactions_blaze
│
├── docs/
│   └── BLAZEAPI/                # PRODUCTION DOCS ONLY (no sandbox)
│       ├── README.md
│       ├── migration_strategy.md
│       ├── safe_migration_plan.md
│       ├── data_mapping_audit.md
│       ├── next_steps.md
│       └── swagger.json
│
└── [other main project files...]
```

## Why This Works

1. **Shared Database**: All projects use same Supabase instance
   - `blaze-api-sync` WRITES to `*_blaze` tables
   - `conductor-sms`, `mota-crm`, `motabot-ai` READ from `*_blaze` tables

2. **Simple Model**: 
   - Blaze sync runs nightly → fills database
   - Other projects pull from database → done

3. **Shared Configs**: Can reference same Supabase credentials

4. **Easy to Find**: Top-level folder, not buried

5. **Independent Enough**: Can still open `blaze-api-sync/` as separate workspace if needed

## Clean Up Needed

**Remove sandbox stuff** (production only now):
- Delete `docs/BLAZEAPI/sandbox/` folder
- Delete `docs/BLAZEAPI/test_*.py` files (keep only docs)
- Keep only production documentation and swagger.json

**Keep in docs/BLAZEAPI/**:
- ✅ README.md
- ✅ migration_strategy.md
- ✅ safe_migration_plan.md
- ✅ data_mapping_audit.md
- ✅ next_steps.md
- ✅ swagger.json
- ✅ rules from blaze.md
- ✅ best_practices.md

**Move to blaze-api-sync/**:
- ✅ All Python implementation code
- ✅ All test scripts
- ✅ Config files

## Workflow

```
blaze-api-sync/          → WRITES to Supabase (*_blaze tables)
      ↓
Supabase Database        → Stores customer/transaction/product data
      ↓
conductor-sms/          → READS from Supabase
mota-crm/               → READS from Supabase  
motabot-ai/             → READS from Supabase
```

Simple, clean, organized. ✅



