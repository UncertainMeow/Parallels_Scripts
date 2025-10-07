#
# install-mysql-odbc.ps1 - Install MySQL ODBC driver
#

$ErrorActionPreference = "Stop"

Write-Host "Installing MySQL ODBC Driver..."

$url = "https://dev.mysql.com/get/Downloads/Connector-ODBC/8.0/mysql-connector-odbc-8.0.35-winx64.msi"
$installer = "$env:TEMP\mysql_odbc_x64.msi"

# Download
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing

# Install
Write-Host "Installing..."
Start-Process msiexec.exe -ArgumentList "/i `"$installer`" /quiet /norestart ADDLOCAL=ALL" -Wait -NoNewWindow

# Verify
$driver = Get-OdbcDriver -Name "MySQL*" -ErrorAction SilentlyContinue
if ($driver) {
    Write-Host "✓ MySQL ODBC Driver installed: $($driver.Name)"
} else {
    Write-Warning "MySQL ODBC Driver may not be installed correctly"
}

# Cleanup
Remove-Item $installer -ErrorAction SilentlyContinue

Write-Host "✓ Complete"
