
# Pin Modem to COM24
# This script ensures the modem is always assigned to COM24

# Requires admin privileges
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERROR: This script requires administrator privileges!"
    Write-Host "Please run PowerShell as Administrator and try again."
    pause
    exit 1
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "  MODEM COM24 PIN SCRIPT"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Step 1: Find the modem device
Write-Host "Step 1: Finding modem device..." -ForegroundColor Cyan

# Get all COM ports and their devices
$comPorts = @()
$regPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\USBSER"

if (Test-Path $regPath) {
    $devices = Get-ChildItem $regPath
    foreach ($device in $devices) {
        $portName = (Get-ItemProperty "$regPath\$($device.PSChildName)\Device Parameters" -ErrorAction SilentlyContinue)."PortName"
        if ($portName) {
            $friendlyName = (Get-ItemProperty "$regPath\$($device.PSChildName)" -ErrorAction SilentlyContinue)."FriendlyName"
            $comPorts += @{
                Port = $portName
                FriendlyName = $friendlyName
                DeviceID = $device.PSChildName
            }
            Write-Host "  Found: $portName - $friendlyName" -ForegroundColor Green
        }
    }
}

if ($comPorts.Count -eq 0) {
    Write-Host "  No COM ports found. The modem may not be connected."
    Write-Host "  Please connect your modem and try again."
    pause
    exit 1
}

# Step 2: Let user select or find modem
Write-Host ""
Write-Host "Available COM ports:" -ForegroundColor Cyan
$comPorts | ForEach-Object { Write-Host "  $($_.Port) - $($_.FriendlyName)" }

# Try to find GSM/modem devices
Write-Host ""
Write-Host "Step 2: Searching for GSM/Modem devices..." -ForegroundColor Cyan

$gsmDevices = @()
$regPath = "HKLM:\SYSTEM\CurrentControlSet\Enum"
$searchPaths = @("USB", "USBSER", "COM")

foreach ($basePath in $searchPaths) {
    $fullPath = "$regPath\$basePath"
    if (Test-Path $fullPath) {
        $devices = Get-ChildItem $fullPath -Recurse -ErrorAction SilentlyContinue | Where-Object {
            $_.Name -like "*GSM*" -or 
            $_.Name -like "*Modem*" -or 
            $_.Name -like "*SIM*" -or
            $_.Name -like "*Mobile*"
        }
        
        foreach ($device in $devices) {
            $friendlyName = (Get-ItemProperty $device.PSPath -ErrorAction SilentlyContinue)."FriendlyName"
            if ($friendlyName) {
                $gsmDevices += @{
                    Name = $friendlyName
                    Path = $device.PSPath
                }
                Write-Host "  Found: $friendlyName" -ForegroundColor Green
            }
        }
    }
}

if ($gsmDevices.Count -eq 0) {
    Write-Host "  No GSM/Modem devices found automatically." -ForegroundColor Yellow
    Write-Host "  Using first available COM port instead..."
    $selectedPort = $comPorts[0].Port
} else {
    Write-Host ""
    Write-Host "Found $($gsmDevices.Count) GSM/Modem device(s)" -ForegroundColor Green
    $selectedPort = $comPorts[0].Port
}

# Step 3: Assign to COM24
Write-Host ""
Write-Host "Step 3: Setting port assignment..." -ForegroundColor Cyan

# Find the registry entry for the current port
$currentRegPath = $null
foreach ($com in $comPorts) {
    if ($com.Port -eq $selectedPort) {
        Write-Host "  Current port: $($com.Port) ($($com.FriendlyName))" -ForegroundColor White
        $currentRegPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\USBSER\$($com.DeviceID)\Device Parameters"
        break
    }
}

if ($currentRegPath -and (Test-Path $currentRegPath)) {
    try {
        Write-Host "  Updating registry to use COM24..." -ForegroundColor White
        Set-ItemProperty -Path $currentRegPath -Name "PortName" -Value "COM24" -ErrorAction Stop
        Write-Host "  ✓ Successfully set to COM24!" -ForegroundColor Green
    } catch {
        Write-Host "  ERROR: Could not update registry: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "  MANUAL FIX:" -ForegroundColor Yellow
        Write-Host "  1. Open Device Manager (devmgmt.msc)"
        Write-Host "  2. Expand 'Ports (COM & LPT)'"
        Write-Host "  3. Right-click your modem device"
        Write-Host "  4. Select 'Properties' → 'Port Settings' → 'Advanced'"
        Write-Host "  5. Change COM Port to COM24"
        Write-Host "  6. Click OK and restart Conductor"
    }
} else {
    Write-Host "  Could not find registry path. Using Device Manager method instead." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  MANUAL FIX:" -ForegroundColor Yellow
    Write-Host "  1. Open Device Manager (devmgmt.msc)"
    Write-Host "  2. Expand 'Ports (COM & LPT)'"
    Write-Host "  3. Right-click your modem device"
    Write-Host "  4. Select 'Properties' → 'Port Settings' → 'Advanced'"
    Write-Host "  5. Change COM Port to COM24"
    Write-Host "  6. Click OK"
    Write-Host "  7. Disconnect and reconnect your modem"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  NEXT STEPS:"
Write-Host "========================================" -ForegroundColor Green
Write-Host "  1. Disconnect your modem"
Write-Host "  2. Wait 10 seconds"
Write-Host "  3. Reconnect your modem"
Write-Host "  4. Run: cd C:\Dev\conductor\conductor-sms"
Write-Host "  5. Run: .\start_conductor.bat"
Write-Host ""
pause



