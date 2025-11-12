Supabase MCP in Cursor (no The Query)
What you’ll use

Official Supabase MCP server (hosted by Supabase). Cursor connects via HTTP + OAuth; no third-party tokens. 
GitHub

Optionally, if you run Supabase locally, the MCP is exposed on your local dev stack. 
GitHub

1) Pick your mode
A) Cloud projects (recommended)

Use Supabase’s remote MCP at:

https://mcp.supabase.com/mcp


Cursor will pop a browser window for Supabase OAuth; you choose the org/project and you’re in. 
GitHub

B) Local dev (Supabase CLI)

If you’re running supabase start, the MCP is available at:

http://localhost:54321/mcp


(Subset of tools; great for local prototyping.) 
GitHub

2) Minimal Cursor config

Create or edit C:\Users\<you>\.cursor\mcp.json (Windows) and add one server:

Project-scoped, read-only (safe default)

{
  "mcpServers": {
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=kiwmwoqrguyrcpjytgte&read_only=true"
    }
  }
}


project_ref locks the MCP to just that project. 
GitHub

read_only=true disables mutating tools and runs SQL as a read-only user. Highly recommended to start. 
GitHub

Local dev example

{
  "mcpServers": {
    "supabase": {
      "type": "http",
      "url": "http://localhost:54321/mcp?read_only=true"
    }
  }
}


Toggle the MCP on in Cursor; you’ll be prompted to sign in to Supabase and pick the org/project. 
GitHub

3) (Optional) Feature control

You can expose only specific tool families to the agent:

https://mcp.supabase.com/mcp?project_ref=...&read_only=true&features=database,docs


Available groups: account, docs, database, debugging, development, functions, storage, branching. If unset, a safe default set is enabled. 
GitHub

4) What tools you get

The server provides tool groups (database, docs, etc.) the agent can call. If you project-scope it, account-level tools like list_projects are hidden. 
GitHub

Typical database tasks that work out-of-the-box:

List schemas/tables

Introspect columns

Run SQL (read-only if you set read_only=true)
All via MCP—no DB password pasted into Cursor needed. 
GitHub

5) Quick smoke test in Cursor

Ask the agent something like:

“Use the Supabase MCP to list tables in the public schema.”

Then:

“Run this SQL and return rows:
SELECT * FROM public.messages ORDER BY id DESC LIMIT 5;”

(With read_only=true, writes are blocked by design.) 
GitHub

6) Troubleshooting (no third-party service involved)
A) OAuth popup didn’t appear / wrong org

Re-toggle the MCP in Cursor.

It will open a browser to log you into Supabase and grant access to the MCP client; pick the org containing your project. You can re-run and pick again if needed. 
GitHub

B) It connects but SQL fails with pooler issues

Supabase’s MCP ultimately talks to Postgres behind the scenes using the pooler (Supavisor). If you want to validate DB connectivity yourself, test with psql:

Direct (raw instance, 5432, IPv6 by default):

psql "host=db.<project_ref>.supabase.co port=5432 dbname=postgres user=postgres password=YOUR_DB_PASSWORD sslmode=require"


Pooler (transaction), 6543 (common for serverless/agents):

psql "host=aws-0-<region>.pooler.supabase.com port=6543 dbname=postgres user=postgres.<project_ref> password=YOUR_DB_PASSWORD sslmode=require"


Replace <region> (e.g. us-east-2) and <project_ref>. Supabase docs explain direct vs pooler endpoints and when to use each. 
Supabase
+2
Supabase
+2

Common fixes:

Reset DB password in Supabase → Settings → Database, then retry.

Ensure the region code is exact (e.g., us-east-2).

If direct works but pooler doesn’t, check you used 6543 for transaction mode (or 5432 for session mode). 
Supabase
+1

C) I want read-write

Remove read_only=true (or point to a dev branch/environment). You can also keep features tight to just what you need. 
GitHub

7) Why this is simpler than DB-password MCPs

The new, official Supabase MCP is remote over HTTP with Supabase OAuth and project scoping—no copying DB passwords into Cursor, and you can limit tools + read/write capability from the URL flags. It’s the path Supabase documents and maintains now. 
Supabase
+2
Supabase
+2

8) If you really want a bare “DB-only” MCP

You can build or use a community MCP that talks straight to Postgres with host/port/user/pass, but you’ll be taking on auth, safety, and schema management yourself. Supabase’s official guidance for DB connectivity (pooler vs direct, region hosts, etc.) is here if you go that route. 
Supabase
+1

Bottom line

Use this URL in Cursor:

https://mcp.supabase.com/mcp?project_ref=kiwmwoqrguyrcpjytgte&read_only=true


Toggle it on, sign in via the popup, and the Supabase tools should be available immediately—no The Query, no extra keys. 
GitHub

If anything still trips up, tell me exactly what Cursor shows (or paste the first 20 lines of the MCP console output), and I'll zero in on it.

## 9) Success! What you should see

After successful connection, you can test with these commands in Cursor:

**List tables:**
```
Use Supabase MCP to list tables in the public schema
```

**Query data:**
```
Run this SQL: SELECT * FROM public.messages ORDER BY id DESC LIMIT 5;
```

**Expected output:**
- Table listing shows your `messages` table with correct schema
- SQL queries return data without errors
- No authentication or connection errors

## 10) Troubleshooting Checklist

If connection fails, check these in order:

- [ ] MCP server toggled OFF and ON in Cursor
- [ ] Browser popup appeared for Supabase OAuth
- [ ] Correct org/project selected in OAuth
- [ ] Project reference matches your Supabase project
- [ ] Supabase project is active (not paused)

## 11) Next Steps for Production

Once MCP is working:

1. **Remove read_only=true** for write access
2. **Add specific features** if needed: `&features=database,functions`
3. **Update your conductor system** to use Supabase instead of SQLite
4. **Migrate existing data** from local database to Supabase
5. **Update n8n workflows** to read directly from Supabase