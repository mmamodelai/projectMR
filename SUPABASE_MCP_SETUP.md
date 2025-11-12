# Supabase MCP Setup for Cursor

## 🎯 What is MCP?

**MCP (Model Context Protocol)** allows Cursor AI to directly interact with your Supabase database:
- Query tables directly from chat
- Create/modify tables
- Run SQL queries
- Manage data without leaving Cursor

## 📦 Installation Steps

### Step 1: Install Python (if not already installed)

Check if Python 3.12+ is installed:
```powershell
python --version
```

If not installed, download from: https://www.python.org/downloads/

### Step 2: Install pipx

```powershell
pip install pipx
pipx ensurepath
```

Close and reopen PowerShell after this step.

### Step 3: Install Supabase MCP Server

```powershell
pipx install supabase-mcp-server
```

### Step 4: Verify Installation

```powershell
supabase-mcp-server --version
```

You should see the version number.

## ⚙️ Configuration

I've already updated your `C:\Users\Xbmc\.cursor\mcp.json` with:

```json
{
  "mcpServers": {
    "supabase": {
      "command": "supabase-mcp-server",
      "env": {
        "SUPABASE_PROJECT_REF": "kiwmwoqrguyrcpjytgte",
        "SUPABASE_DB_PASSWORD": "Llama34ever!",
        "SUPABASE_REGION": "us-east-2"
      }
    }
  }
}
```

## 🔄 Restart Cursor

After installation, restart Cursor completely:
1. Close all Cursor windows
2. Reopen Cursor
3. The MCP server will start automatically

## ✅ Test the Integration

In Cursor chat, try these commands:

### 1. List all tables
```
@supabase Show me all tables in my database
```

### 2. Query messages
```
@supabase Show me the last 10 unread messages from the messages table
```

### 3. Count messages
```
@supabase How many messages are in the messages table?
```

### 4. Run custom SQL
```
@supabase Run this query: SELECT status, COUNT(*) FROM messages GROUP BY status
```

## 🎨 What You Can Do with MCP

### Database Queries
- "Show me all unread inbound messages"
- "Count messages by status"
- "Find messages from +16199773020"

### Table Management
- "Create a new table called contacts"
- "Add a column 'tags' to the messages table"
- "Show me the schema of the messages table"

### Data Operations
- "Update message ID 150 to status 'read'"
- "Delete all messages older than 30 days"
- "Insert a test message"

### Analytics
- "Show me message statistics by day"
- "What's the average response time?"
- "Which phone number has the most messages?"

## 🔐 Security Notes

Your database password is stored in the MCP config file. This file is:
- ✅ Local to your machine
- ✅ Not committed to git
- ⚠️ Readable by any process on your machine

**Best Practice**: Use a read-only database user for MCP if you only need to query data.

## 🆘 Troubleshooting

### "supabase-mcp-server: command not found"
**Solution**: 
1. Run `pipx ensurepath`
2. Close and reopen PowerShell
3. Try again

### "Connection refused" or "Authentication failed"
**Solution**: 
1. Check your database password in `mcp.json`
2. Verify your project ref: `kiwmwoqrguyrcpjytgte`
3. Check Supabase project status

### MCP server not showing in Cursor
**Solution**:
1. Restart Cursor completely
2. Check Cursor logs: Help → Show Logs
3. Look for MCP-related errors

### Python version too old
**Solution**:
```powershell
# Install Python 3.12+
winget install Python.Python.3.12
```

## 📚 Advanced Configuration

### Multiple Supabase Projects

You can add multiple Supabase projects:

```json
{
  "mcpServers": {
    "supabase-prod": {
      "command": "supabase-mcp-server",
      "env": {
        "SUPABASE_PROJECT_REF": "kiwmwoqrguyrcpjytgte",
        "SUPABASE_DB_PASSWORD": "Llama34ever!",
        "SUPABASE_REGION": "us-east-2"
      }
    },
    "supabase-dev": {
      "command": "supabase-mcp-server",
      "env": {
        "SUPABASE_PROJECT_REF": "your-dev-project-ref",
        "SUPABASE_DB_PASSWORD": "your-dev-password",
        "SUPABASE_REGION": "us-east-2"
      }
    }
  }
}
```

Then use `@supabase-prod` or `@supabase-dev` in chat.

### Read-Only Access

For safety, create a read-only user in Supabase:

1. Go to Supabase Dashboard → Database → Roles
2. Create new role: `mcp_readonly`
3. Grant SELECT permissions only
4. Update `SUPABASE_DB_PASSWORD` with the new role's password

## 🎯 Example Workflow

### 1. Check unread messages
```
You: @supabase Show me unread inbound messages
AI: [Returns list of unread messages]
```

### 2. Analyze data
```
You: @supabase What's the distribution of message statuses?
AI: [Shows breakdown: 33 unread, 17 read, 96 sent, 4 failed]
```

### 3. Update data
```
You: @supabase Mark message 150 as read
AI: [Updates the message and confirms]
```

### 4. Create reports
```
You: @supabase Generate a daily message report for the last 7 days
AI: [Creates a table showing daily message counts]
```

## 🚀 Benefits Over Direct SQL

### Before (Manual SQL):
```sql
-- You have to write this yourself
SELECT 
  DATE(timestamp) as date,
  direction,
  COUNT(*) as count
FROM messages
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp), direction
ORDER BY date DESC;
```

### After (MCP in Cursor):
```
You: @supabase Show me message counts by direction for the last 7 days
AI: [Writes and executes the query for you]
```

## 📊 Integration with Your Conductor System

Now you can:

1. **Monitor in real-time**:
   ```
   @supabase How many messages have been processed in the last hour?
   ```

2. **Debug issues**:
   ```
   @supabase Show me all failed messages and their retry counts
   ```

3. **Analyze patterns**:
   ```
   @supabase What times of day do we receive the most messages?
   ```

4. **Manage data**:
   ```
   @supabase Clean up messages older than 90 days with status 'sent'
   ```

## 🎉 You're All Set!

Once you've installed `supabase-mcp-server` and restarted Cursor, you'll be able to interact with your Supabase database directly from Cursor chat using `@supabase`.

---

**Project**: smsconductor  
**Database**: https://kiwmwoqrguyrcpjytgte.supabase.co  
**Region**: us-east-2 (Ohio)  
**Status**: Ready ✅

