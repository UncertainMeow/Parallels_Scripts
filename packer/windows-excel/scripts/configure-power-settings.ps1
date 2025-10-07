#
# configure-power-settings.ps1 - Configure power settings for VMs
#

$ErrorActionPreference = "Stop"

Write-Host "Configuring power settings..."

# Set power plan to High Performance
$plan = powercfg /list | Select-String "High performance"
if ($plan) {
    $planGuid = ($plan -split "\s+")[3]
    powercfg /setactive $planGuid
    Write-Host "✓ Set to High Performance plan"
}

# Never turn off display
powercfg /change monitor-timeout-ac 0
powercfg /change monitor-timeout-dc 0

# Never sleep
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0

# Never turn off hard disk
powercfg /change disk-timeout-ac 0
powercfg /change disk-timeout-dc 0

Write-Host "✓ Power settings configured for VM use"
