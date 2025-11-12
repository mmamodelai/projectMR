# Find and show Conductor window
$process = Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -like '*conductor_system.py*'}

if ($process) {
    $pid = $process.ProcessId
    Write-Host "`n[OK] Conductor is running (PID: $pid)" -ForegroundColor Green
    
    # Get runtime
    $runtime = (Get-Date) - $process.CreationDate
    Write-Host "Runtime: $($runtime.Days)d $($runtime.Hours)h $($runtime.Minutes)m" -ForegroundColor Cyan
    
    # Try to bring window to front
    Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        public class Win32 {
            [DllImport("user32.dll")]
            public static extern bool SetForegroundWindow(IntPtr hWnd);
            [DllImport("user32.dll")]
            public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
        }
"@
    
    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($proc -and $proc.MainWindowHandle -ne 0) {
        [Win32]::ShowWindow($proc.MainWindowHandle, 9) # SW_RESTORE
        [Win32]::SetForegroundWindow($proc.MainWindowHandle)
        Write-Host "`n[OK] Brought Conductor window to front" -ForegroundColor Green
    } else {
        Write-Host "`n[INFO] Conductor has no visible window (running in background)" -ForegroundColor Yellow
        Write-Host "View logs to see activity:" -ForegroundColor Yellow
        Write-Host "  Get-Content logs\conductor_system.log -Tail 20 -Wait" -ForegroundColor White
    }
    
    # Show recent log
    Write-Host "`n=== LAST 5 LOG ENTRIES ===" -ForegroundColor Cyan
    Get-Content "logs\conductor_system.log" -Tail 5
    
} else {
    Write-Host "`n[ERROR] Conductor is NOT running!" -ForegroundColor Red
    Write-Host "`nTo start:" -ForegroundColor Yellow
    Write-Host "  python conductor_system.py" -ForegroundColor White
}

Write-Host ""

