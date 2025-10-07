#
# configure-windows.ps1 - Configure Windows settings for optimal use
#

$ErrorActionPreference = "Stop"

Write-Host "Configuring Windows settings..."

# Disable Windows Update automatic restarts
Write-Host "Configuring Windows Update..."
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "NoAutoRebootWithLoggedOnUsers" -Value 1 -Force

# Disable hibernation (saves disk space)
Write-Host "Disabling hibernation..."
powercfg /hibernate off

# Set timezone to UTC (or customize)
Write-Host "Setting timezone..."
Set-TimeZone -Id "Pacific Standard Time" -PassThru

# Disable unnecessary services
Write-Host "Disabling unnecessary services..."
$services = @(
    "DiagTrack",    # Diagnostics Tracking
    "dmwappushservice"  # WAP Push Message Routing
)

foreach ($service in $services) {
    try {
        Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
        Set-Service -Name $service -StartupType Disabled -ErrorAction SilentlyContinue
        Write-Host "  - Disabled $service"
    } catch {
        Write-Warning "Could not disable $service"
    }
}

# Enable RDP (optional)
# Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -name "fDenyTSConnections" -Value 0
# Enable-NetFirewallRule -DisplayGroup "Remote Desktop"

# Configure Windows Explorer
Write-Host "Configuring Windows Explorer..."
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "Hidden" -Value 1  # Show hidden files
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -Value 0  # Show file extensions

# Disable telemetry
Write-Host "Disabling telemetry..."
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -Force

# Create analytics directory
Write-Host "Creating directories..."
New-Item -Path "C:\Analytics" -ItemType Directory -Force | Out-Null
New-Item -Path "C:\Analytics\Data" -ItemType Directory -Force | Out-Null
New-Item -Path "C:\Analytics\Reports" -ItemType Directory -Force | Out-Null
New-Item -Path "C:\Scripts" -ItemType Directory -Force | Out-Null

Write-Host "✓ Windows configured"
