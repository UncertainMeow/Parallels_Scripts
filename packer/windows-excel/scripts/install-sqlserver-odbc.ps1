#
# install-sqlserver-odbc.ps1 - Install SQL Server ODBC driver
#

$ErrorActionPreference = "Stop"

Write-Host "Installing SQL Server ODBC Driver..."

$url = "https://go.microsoft.com/fwlink/?linkid=2249006"
$installer = "$env:TEMP\msodbcsql_x64.msi"

# Download
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing

# Install
Write-Host "Installing..."
Start-Process msiexec.exe -ArgumentList "/i `"$installer`" /quiet /norestart IACCEPTMSODBCSQLLICENSETERMS=YES" -Wait -NoNewWindow

# Verify
$driver = Get-OdbcDriver -Name "*SQL Server*" -ErrorAction SilentlyContinue
if ($driver) {
    Write-Host "✓ SQL Server ODBC Driver installed"
    $driver | ForEach-Object { Write-Host "  - $($_.Name)" }
} else {
    Write-Warning "SQL Server ODBC Driver may not be installed correctly"
}

# Cleanup
Remove-Item $installer -ErrorAction SilentlyContinue

Write-Host "✓ Complete"
