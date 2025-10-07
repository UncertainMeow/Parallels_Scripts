#
# install-chocolatey.ps1 - Install Chocolatey package manager
#

$ErrorActionPreference = "Stop"

Write-Host "Installing Chocolatey..."

# Set TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Install Chocolatey
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Verify installation
if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "✓ Chocolatey installed successfully"
    choco --version
} else {
    Write-Error "Chocolatey installation failed"
    exit 1
}

# Disable confirmation prompts
choco feature enable -n allowGlobalConfirmation

Write-Host "✓ Chocolatey configured"
