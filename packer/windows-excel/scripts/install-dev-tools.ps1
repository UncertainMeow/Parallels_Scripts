#
# install-dev-tools.ps1 - Install useful development tools
#

$ErrorActionPreference = "Stop"

Write-Host "Installing development tools via Chocolatey..."

# Install useful tools
$tools = @(
    "git",
    "python",
    "7zip",
    "notepadplusplus",
    "dbeaver",  # Universal database tool
    "vscode"    # Optional: VS Code
)

foreach ($tool in $tools) {
    Write-Host "Installing $tool..."
    try {
        choco install $tool -y --limit-output
        Write-Host "✓ $tool installed"
    } catch {
        Write-Warning "Failed to install $tool: $_"
    }
}

# Verify installations
Write-Host ""
Write-Host "Installed tools:"
choco list --local-only --limit-output | ForEach-Object {
    Write-Host "  - $_"
}

Write-Host ""
Write-Host "✓ Development tools installed"
