@echo off
REM Create desktop shortcuts for Conductor tools
REM Part of Conductor SMS System

echo Creating desktop shortcuts...

set "DESKTOP=%USERPROFILE%\Desktop"
set "PROJECT_DIR=C:\Dev\conductor\Olive"

REM 1. Conductor System
echo Creating Conductor shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Conductor SMS System.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = 'conductor_system.py'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.Description = 'Conductor SMS System - Main SMS processing engine'; $Shortcut.Save()"

REM 2. Database Manager GUI
echo Creating DB Manager shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\SMS Database Manager.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = 'db_manager_gui.py'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.Description = 'Supabase SMS Database Manager - View/Edit/Delete messages'; $Shortcut.Save()"

REM 3. Flash SMS Tool
echo Creating Flash SMS shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Flash SMS Tool.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = 'flash_sms_gui.py'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.Description = 'Flash SMS Tool - Send urgent popup messages'; $Shortcut.Save()"

echo.
echo Desktop shortcuts created:
echo - Conductor SMS System.lnk
echo - SMS Database Manager.lnk  
echo - Flash SMS Tool.lnk
echo.
echo All shortcuts point to: %PROJECT_DIR%
echo.
pause
