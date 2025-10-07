#
# install-postgresql-odbc.ps1 - Install PostgreSQL ODBC driver
#

$ErrorActionPreference = "Stop"

Write-Host "Installing PostgreSQL ODBC Driver..."

$url = "https://ftp.postgresql.org/pub/odbc/releases/REL-16_00_0000/psqlodbc_x64.msi"
$installer = "$env:TEMP\psqlodbc_x64.msi"

# Download
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing

# Install
Write-Host "Installing..."
Start-Process msiexec.exe -ArgumentList "/i `"$installer`" /quiet /norestart ADDLOCAL=ALL" -Wait -NoNewWindow

# Verify
$driver = Get-OdbcDriver -Name "PostgreSQL*" -ErrorAction SilentlyContinue
if ($driver) {
    Write-Host "✓ PostgreSQL ODBC Driver installed: $($driver.Name)"
} else {
    Write-Warning "PostgreSQL ODBC Driver may not be installed correctly"
}

# Cleanup
Remove-Item $installer -ErrorAction SilentlyContinue

Write-Host "✓ Complete"
