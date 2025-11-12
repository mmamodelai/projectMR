# Supabase MCP Integration - Support Request

## TL;DR (Do This Now)

1. Add your QUERY API key at thequery.dev and update mcp.json like this:

```json
{
  "mcpServers": {
    "supabase": {
      "command": "supabase-mcp-server",
      "env": {
        "QUERY_API_KEY": "PASTE_YOUR_QUERY_API_KEY",
        "SUPABASE_PROJECT_REF": "kiwmwoqrguyrcpjytgte",
        "SUPABASE_DB_PASSWORD": "********",
        "SUPABASE_REGION": "us-east-2"
      }
    }
  }
}
```

2. Remove SUPABASE_DB_HOST from mcp.json (server derives pooler DSN automatically).
3. Restart Cursor or toggle the Supabase MCP off/on.
4. Test in chat:
   - `@supabase get_tables`
   - `@supabase Execute SQL: SELECT id, phone_number, content FROM public.messages ORDER BY id DESC LIMIT 5;`

Logs (for troubleshooting):
- Windows: `%USERPROFILE%\.local\share\supabase-mcp\mcp_server.log`
- macOS/Linux: `~/.local/share/supabase-mcp/mcp_server.log`

## Context
- Goal: Use supabase-mcp-server in Cursor to query our Supabase project from chat
- Project: `smsconductor` (ref: `kiwmwoqrguyrcpjytgte`)
- Region shown in dashboard: `us-east-2` (AWS Ohio)
- Cursor shows MCP server: `supabase-mcp-server` (green), 12 tools available
- Table `public.messages` created and seeded via Supabase SQL Editor (works)

## Current MCP Config (masked)
```json
{
  "mcpServers": {
    "supabase": {
      "command": "supabase-mcp-server",
      "env": {
        "SUPABASE_PROJECT_REF": "kiwmwoqrguyrcpjytgte",
        "SUPABASE_DB_PASSWORD": "********",
        "SUPABASE_REGION": "us-east-2"
      }
    }
  }
}
```

## Symptoms
- All MCP calls fail with: "CONNECTION ERROR: Region mismatch detected! Could not connect to Supabase project 'kiwmwoqrguyrcpjytgte'"
- Error repeats even after Cursor restart and toggling the MCP
- Error persists across region values tried: `us-east-2`, `us-east-1`, `aws-us-east-2`, and with REGION removed entirely
- SQL Editor operations succeed; only MCP-server connection fails

## What We Tried
1. Installed supabase-mcp-server via pipx; server visible in Cursor (green)
2. Set env vars in `mcp.json`: PROJECT_REF, DB_PASSWORD, REGION, DB_HOST
3. Toggled MCP off/on and fully restarted Cursor after each change
4. Removed REGION to allow auto-detection; still reports mismatch
5. Verified project region in dashboard (us-east-2) and that DB host resolves

## Hypotheses / Unknowns
- The server may expect additional DB connection env vars (e.g., `SUPABASE_DB_USER=postgres`, `SUPABASE_DB_PORT=5432`, `SUPABASE_DB_NAME=postgres`)
- REGION canonical value may differ (e.g., `aws-us-east-2` vs `us-east-2`) or not be required when DB_HOST is set
- The MCP server may require a management token (`SUPABASE_ACCESS_TOKEN`) to resolve region/connection metadata
- Version expectations (Python 3.13 OK? specific supabase-mcp-server version constraints?)
- Server could be defaulting to `us-east-1` due to missing/ignored region, causing the mismatch

## Questions for Supabase MCP Expert
1. What is the minimal, correct env set for Postgres connectivity?
   - Example for ref `kiwmwoqrguyrcpjytgte` in `us-east-2`
   - Required keys: `SUPABASE_DB_HOST`, `SUPABASE_DB_USER`, `SUPABASE_DB_PASSWORD`, `SUPABASE_DB_PORT`, `SUPABASE_DB_NAME`?
2. Is `SUPABASE_REGION` required? If yes, what are the accepted values for AWS us-east-2?
3. Does the server use the Management API? If so, do we need `SUPABASE_ACCESS_TOKEN` and which scopes?
4. Can the server operate in "DB-only" mode with just Postgres creds (no region)? If so, how to configure?
5. How to enable verbose logging from the MCP server within Cursor to diagnose connection resolution?
6. Is there a CLI to test the same connection (e.g., `supabase-mcp-inspector`) and sample usage?
7. Any known issues with Python 3.13 or Windows PATH/encoding peculiarities?

## Reproduction Steps
1. Install: `pipx install supabase-mcp-server`
2. Configure `C:\\Users\\<USER>\\.cursor\\mcp.json` (as above)
3. Restart Cursor → Tools & MCP → Supabase shows green
4. Run any tool (e.g., get_tables) → region mismatch error

## Desired End State
- MCP tools run successfully:
  - List schemas/tables
  - Execute SQL: `SELECT * FROM public.messages ORDER BY id DESC LIMIT 5;`

## Next Actions We Can Try (pending guidance)
- Add: `SUPABASE_DB_USER=postgres`, `SUPABASE_DB_PORT=5432`, `SUPABASE_DB_NAME=postgres`
- Remove REGION completely and rely on DB_* only
- Provide a `SUPABASE_ACCESS_TOKEN` (Management API) if required
- Upgrade/downgrade supabase-mcp-server version if a compatibility issue is known

## References
- Project URL: https://kiwmwoqrguyrcpjytgte.supabase.co
- Table confirmed via SQL Editor: `public.messages`
- Host used: `db.kiwmwoqrguyrcpjytgte.supabase.co`

---

Please advise on the exact env contract for supabase-mcp-server and the correct REGION semantics for AWS us-east-2.



-----------response-----------
Great write-up — this is super close. The snag is your env contract doesn’t match what the supabase-mcp-server (the Python one on PyPI) actually expects.

Here’s the short version of what fixes it:

✅ Minimal working env for the Python supabase-mcp-server

For a hosted Supabase project you need exactly these (plus one new required key):

QUERY_API_KEY (required since v0.4) → get a free one at thequery.dev

SUPABASE_PROJECT_REF → kiwmwoqrguyrcpjytgte

SUPABASE_DB_PASSWORD → your database password (from Project Settings → Database)

SUPABASE_REGION → us-east-2 (Ohio)

Nothing else is required for “DB-only” querying. Don’t set SUPABASE_DB_HOST — the server builds the pooler DSN from PROJECT_REF + REGION for you. (It connects to the transaction pooler: aws-0-<region>.pooler.supabase.com:6543.) 
PyPI

Example mcp.json
{
  "mcpServers": {
    "supabase": {
      "command": "supabase-mcp-server",
      "env": {
        "QUERY_API_KEY": "YOUR_QUERY_API_KEY",          // required (v0.4+)
        "SUPABASE_PROJECT_REF": "kiwmwoqrguyrcpjytgte", // required
        "SUPABASE_DB_PASSWORD": "********",             // required
        "SUPABASE_REGION": "us-east-2"                  // required for remote
      }
    }
  }
}


Notes
- SUPABASE_REGION must be the AWS code only (`us-east-2`).
- Do not set `SUPABASE_DB_HOST`, `SUPABASE_DB_USER`, `SUPABASE_DB_PORT`, `SUPABASE_DB_NAME`; the server derives them.

Optional (only if you need these tool families):
- Management API tools → add `SUPABASE_ACCESS_TOKEN` (personal access token)
- Auth Admin SDK tools → add `SUPABASE_SERVICE_ROLE_KEY` (keep secret)

Why you saw “Region mismatch”

The Python server validates/constructs a pooler host like:

postgresql://postgres.<PROJECT_REF>:<DB_PASSWORD>@aws-0-<REGION>.pooler.supabase.com:6543/postgres


If REGION is missing or not a plain AWS code, it won’t match your project’s real location (Ohio = us-east-2) and you’ll get the mismatch error. 
PyPI

Turn on logs / inspect

The server writes verbose logs to a file by default:

Windows: %USERPROFILE%\.local\share\supabase-mcp\mcp_server.log

macOS/Linux: ~/.local/share/supabase-mcp/mcp_server.log 
PyPI

You can also run it directly in a terminal (`supabase-mcp-server`) to see startup checks and config echoes. There’s also an MCP Inspector utility (install from source): `supabase-mcp-inspector`.

CLI / sanity test without Cursor

If you want to sanity-check connectivity outside Cursor, try any Postgres client against the transaction pooler using the same pieces the server will use (host pattern and port 6543).

Version / platform notes

The package is published and tested for Python 3.12+; it uses asyncpg and doesn’t list known 3.13 issues in its docs. If you do hit something odd, check the log path above. 
PyPI

TL;DR do this now

Remove SUPABASE_DB_HOST.

Set SUPABASE_REGION to us-east-2 (exactly).

Add the missing QUERY_API_KEY.

Keep SUPABASE_PROJECT_REF + SUPABASE_DB_PASSWORD as you have them.

Restart Cursor (or just toggle the MCP).

After that, tools like get_tables and:

SELECT * FROM public.messages ORDER BY id DESC LIMIT 5;


should work.

If anything still barks, open the log file and paste the top 30 lines here — we can decode it quickly.
