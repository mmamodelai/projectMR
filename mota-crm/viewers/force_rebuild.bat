@echo off
echo Forcing contact directory rebuild...
del contact_directory_cache.json 2>nul
echo Cache deleted.
echo.
echo Restarting Manual Conductor...
start_manual_conductor.bat

