#
# cleanup-temp.ps1 - Clean up temporary files
#

$ErrorActionPreference = "Continue"

Write-Host "Cleaning up temporary files..."

# Clean Windows temp
Write-Host "Cleaning Windows temp..."
Remove-Item -Path $env:TEMP\* -Recurse -Force -ErrorAction SilentlyContinue

# Clean user temp
Write-Host "Cleaning user temp..."
Remove-Item -Path "$env:USERPROFILE\AppData\Local\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# Clean Windows Update cache
Write-Host "Cleaning Windows Update cache..."
Stop-Service -Name wuauserv -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
Start-Service -Name wuauserv -ErrorAction SilentlyContinue

# Clean Chocolatey cache
if (Test-Path "C:\ProgramData\chocolatey\cache") {
    Write-Host "Cleaning Chocolatey cache..."
    Remove-Item -Path "C:\ProgramData\chocolatey\cache\*" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "✓ Temporary files cleaned"
