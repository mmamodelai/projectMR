
# Force Modem to COM24
# Finds Simcom AT PORT and assigns it to COM24

Write-Host "========================================" -ForegroundColor Green
Write-Host "  FORCE COM24 ASSIGNMENT"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Find Simcom device
Write-Host "Finding Simcom AT PORT device..." -ForegroundColor Cyan
$device = Get-PnpDevice | Where-Object { $_.Name -like "*Simcom*AT PORT*" } | Select-Object -First 1

if (-not $device) {
    Write-Host "ERROR: Simcom AT PORT device not found!" -ForegroundColor Red
    Write-Host "Available devices:" -ForegroundColor Yellow
    Get-PnpDevice | Where-Object { $_.Name -like "*Simcom*" } | Select-Object Name
    exit 1
}

Write-Host "Found: $($device.Name)" -ForegroundColor Green
Write-Host ""

# Get registry path
$instanceId = $device.InstanceId
$parts = $instanceId.Split('\')
$basePath = "HKLM:\SYSTEM\CurrentControlSet\Enum\$($parts[0])\$($parts[1])\Device Parameters"

Write-Host "Registry path: $basePath" -ForegroundColor White

if (Test-Path $basePath) {
    $current = Get-ItemProperty $basePath -Name "PortName" -ErrorAction SilentlyContinue
    Write-Host "Current port: $($current.PortName)" -ForegroundColor Yellow
    
    Write-Host "Setting to COM24..." -ForegroundColor Cyan
    Set-ItemProperty -Path $basePath -Name "PortName" -Value "COM24" -Force -ErrorAction Stop
    
    $verify = Get-ItemProperty $basePath -Name "PortName"
    Write-Host "Verified: $($verify.PortName)" -ForegroundColor Green
    Write-Host ""
    Write-Host "SUCCESS! Modem assigned to COM24" -ForegroundColor Green
} else {
    Write-Host "ERROR: Registry path not found!" -ForegroundColor Red
    Write-Host "Trying alternate registry locations..." -ForegroundColor Yellow
    
    # Try USBSER
    $altPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\USBSER\$($parts[1])\Device Parameters"
    if (Test-Path $altPath) {
        Write-Host "Found alternate path: $altPath" -ForegroundColor Green
        Set-ItemProperty -Path $altPath -Name "PortName" -Value "COM24" -Force -ErrorAction Stop
        Write-Host "SUCCESS! Set to COM24" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Disconnect your modem (unplug USB)"
Write-Host "2. Wait 5 seconds"
Write-Host "3. Reconnect your modem"
Write-Host "4. Run: .\start_conductor.bat"
Write-Host ""



