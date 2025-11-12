@echo off
REM Install Supabase MCP Server for Cursor
REM This enables direct database access from Cursor AI

echo ========================================
echo  Supabase MCP Server Installation
echo ========================================
echo.

echo Step 1: Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.12+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

echo Step 2: Installing pipx...
pip install pipx
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install pipx
    pause
    exit /b 1
)
echo.

echo Step 3: Ensuring pipx is in PATH...
pipx ensurepath
echo.

echo Step 4: Installing supabase-mcp-server...
pipx install supabase-mcp-server
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install supabase-mcp-server
    pause
    exit /b 1
)
echo.

echo Step 5: Verifying installation...
supabase-mcp-server --version
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: supabase-mcp-server not found in PATH
    echo You may need to close and reopen PowerShell
)
echo.

echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo Your MCP config has been updated at:
echo   C:\Users\Xbmc\.cursor\mcp.json
echo.
echo Next steps:
echo   1. Close ALL Cursor windows
echo   2. Reopen Cursor
echo   3. In Cursor chat, type: @supabase Show me all tables
echo.
echo See SUPABASE_MCP_SETUP.md for full documentation
echo.
pause

