#!/usr/bin/env bash
#
# excel-odbc-setup.sh - Automate ODBC configuration in Windows VM for Excel
# Sets up connections to PostgreSQL, MySQL, SQL Server for Metabase/analytics
#

set -euo pipefail

# Configuration
VM_NAME="${PARALLELS_EXCEL_VM:-Windows 11}"
METABASE_HOST="${METABASE_HOST:-localhost}"
METABASE_PORT="${METABASE_PORT:-5432}"
METABASE_DB="${METABASE_DB:-metabase}"
METABASE_USER="${METABASE_USER:-metabase}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if VM exists and is running
check_vm() {
    log "Checking VM status: $VM_NAME"

    if ! prlctl list "$VM_NAME" &>/dev/null; then
        error "VM '$VM_NAME' not found"
        exit 1
    fi

    local status=$(prlctl list "$VM_NAME" -o status --no-header | tr -d ' ')
    if [ "$status" != "running" ]; then
        log "Starting VM: $VM_NAME"
        prlctl start "$VM_NAME"
        log "Waiting for VM to boot..."
        sleep 30
    fi

    success "VM is running"
}

# Create PowerShell script to install ODBC drivers
create_driver_installer() {
    cat > /tmp/install_odbc_drivers.ps1 << 'PSEOF'
# Install PostgreSQL ODBC Driver
$pgOdbcUrl = "https://ftp.postgresql.org/pub/odbc/releases/REL-13_02_0000/psqlodbc_x64.msi"
$pgInstaller = "$env:TEMP\psqlodbc_x64.msi"

Write-Host "Downloading PostgreSQL ODBC driver..."
Invoke-WebRequest -Uri $pgOdbcUrl -OutFile $pgInstaller
Write-Host "Installing PostgreSQL ODBC driver..."
Start-Process msiexec.exe -ArgumentList "/i $pgInstaller /quiet /norestart" -Wait

# Install MySQL ODBC Driver
$mysqlOdbcUrl = "https://dev.mysql.com/get/Downloads/Connector-ODBC/8.0/mysql-connector-odbc-8.0.33-winx64.msi"
$mysqlInstaller = "$env:TEMP\mysql_odbc.msi"

Write-Host "Downloading MySQL ODBC driver..."
Invoke-WebRequest -Uri $mysqlOdbcUrl -OutFile $mysqlInstaller
Write-Host "Installing MySQL ODBC driver..."
Start-Process msiexec.exe -ArgumentList "/i $mysqlInstaller /quiet /norestart" -Wait

Write-Host "ODBC drivers installed successfully"
PSEOF

    success "Created driver installer script"
}

# Create PowerShell script to configure ODBC DSNs
create_dsn_configurator() {
    cat > /tmp/configure_odbc_dsns.ps1 << PSEOF
# Configure PostgreSQL DSN for Metabase
\$dsnName = "Metabase_PostgreSQL"
\$driver = "PostgreSQL Unicode(x64)"
\$server = "$METABASE_HOST"
\$port = "$METABASE_PORT"
\$database = "$METABASE_DB"
\$username = "$METABASE_USER"

Write-Host "Creating ODBC DSN: \$dsnName"

# Create system DSN
Add-OdbcDsn -Name \$dsnName ``
    -DriverName \$driver ``
    -DsnType "System" ``
    -SetPropertyValue @(
        "Server=\$server",
        "Port=\$port",
        "Database=\$database",
        "UID=\$username"
    )

Write-Host "DSN created successfully"

# List all ODBC data sources
Write-Host "`nConfigured ODBC Data Sources:"
Get-OdbcDsn | Format-Table -AutoSize
PSEOF

    success "Created DSN configurator script"
}

# Copy script to Windows VM and execute
execute_in_vm() {
    local script_name="$1"
    local script_path="/tmp/$script_name"

    log "Copying script to VM: $script_name"

    # Copy file to VM (Parallels Shared Folders must be enabled)
    prlctl set "$VM_NAME" --shf-host on --shf-host-defined on

    log "Executing script in VM..."
    prlctl exec "$VM_NAME" powershell.exe -ExecutionPolicy Bypass -File "\\\\psf\\Home\\tmp\\$script_name"

    success "Script execution complete"
}

# Install ODBC drivers
install_drivers() {
    log "Installing ODBC drivers in Windows VM..."
    create_driver_installer
    execute_in_vm "install_odbc_drivers.ps1"
}

# Configure DSNs
configure_dsns() {
    log "Configuring ODBC DSNs..."
    create_dsn_configurator
    execute_in_vm "configure_odbc_dsns.ps1"
}

# Test connection from macOS to verify database is reachable
test_connection() {
    log "Testing database connection from host..."

    if command -v psql &>/dev/null; then
        log "Testing PostgreSQL connection..."
        PGPASSWORD="${METABASE_PASSWORD:-}" psql -h "$METABASE_HOST" -p "$METABASE_PORT" -U "$METABASE_USER" -d "$METABASE_DB" -c "SELECT version();" &>/dev/null
        if [ $? -eq 0 ]; then
            success "Database connection successful"
        else
            error "Database connection failed. Check credentials and network."
        fi
    else
        log "psql not found, skipping connection test"
    fi
}

# Create Excel connection test file
create_excel_test() {
    log "Creating Excel connection test guide..."

    cat > /tmp/excel_connection_test.txt << 'EOF'
Excel ODBC Connection Test
==========================

1. Open Excel in your Windows VM
2. Go to: Data → Get Data → From Other Sources → From ODBC
3. Select "Metabase_PostgreSQL" from the dropdown
4. Enter password when prompted
5. Select tables and load data

Alternatively, use Power Query:
1. Data → Get Data → From Database → From PostgreSQL Database
2. Server: localhost (or your Metabase host)
3. Database: metabase

For VBA/Macro connections:
```vba
Sub ConnectToMetabase()
    Dim conn As Object
    Set conn = CreateObject("ADODB.Connection")

    conn.ConnectionString = "DSN=Metabase_PostgreSQL;UID=metabase;PWD=yourpassword"
    conn.Open

    ' Your query here
    Dim rs As Object
    Set rs = conn.Execute("SELECT * FROM your_table LIMIT 10")

    ' Process results...
    conn.Close
End Sub
```

EOF

    success "Created Excel test guide at /tmp/excel_connection_test.txt"
    cat /tmp/excel_connection_test.txt
}

# Main menu
show_usage() {
    cat << EOF
Usage: $0 <command>

Commands:
    install     Install ODBC drivers in Windows VM
    configure   Configure ODBC DSNs
    test        Test database connection
    all         Do all steps (install → configure → test)
    excel-guide Show Excel connection guide

Environment Variables:
    PARALLELS_EXCEL_VM  VM name (default: "Windows 11")
    METABASE_HOST       Database host (default: localhost)
    METABASE_PORT       Database port (default: 5432)
    METABASE_DB         Database name (default: metabase)
    METABASE_USER       Database user (default: metabase)
    METABASE_PASSWORD   Database password

Example:
    METABASE_HOST=192.168.1.100 METABASE_USER=analytics $0 all

EOF
}

main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi

    case "$1" in
        install)
            check_vm
            install_drivers
            ;;
        configure)
            check_vm
            configure_dsns
            ;;
        test)
            test_connection
            ;;
        all)
            check_vm
            test_connection
            install_drivers
            configure_dsns
            create_excel_test
            success "All done! Check /tmp/excel_connection_test.txt for next steps"
            ;;
        excel-guide)
            create_excel_test
            ;;
        *)
            error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
