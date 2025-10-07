#
# cleanup-windows.ps1 - Final Windows cleanup before imaging
#

$ErrorActionPreference = "Continue"

Write-Host "Performing final Windows cleanup..."

# Clear event logs
Write-Host "Clearing event logs..."
Get-WinEvent -ListLog * | Where-Object {$_.RecordCount} | ForEach-Object {
    wevtutil clear-log $_.LogName
}

# Clear recent items
Write-Host "Clearing recent items..."
Remove-Item -Path "$env:APPDATA\Microsoft\Windows\Recent\*" -Force -ErrorAction SilentlyContinue

# Clear thumbnail cache
Write-Host "Clearing thumbnail cache..."
Remove-Item -Path "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\thumbcache_*.db" -Force -ErrorAction SilentlyContinue

# Run Disk Cleanup
Write-Host "Running Disk Cleanup..."
Start-Process -FilePath "cleanmgr.exe" -ArgumentList "/sagerun:1" -Wait -NoNewWindow -ErrorAction SilentlyContinue

# Clear DNS cache
Write-Host "Clearing DNS cache..."
ipconfig /flushdns | Out-Null

Write-Host "✓ Windows cleanup complete"
Write-Host ""
Write-Host "Golden image is ready!"
