# Excel Automation Python Library

Production-grade Python framework for automating Excel + ODBC workflows with Parallels Desktop.

## Features

- **VM Management**: Start/stop VMs, snapshots, command execution
- **ODBC Configuration**: Automated driver installation and DSN setup
- **Configuration Management**: YAML configs with secure environment variables
- **CLI Tool**: User-friendly command-line interface
- **Logging**: Professional logging with rotation and color output
- **Type-Safe**: Full type hints for better IDE support

## Installation

### Option 1: Development Install

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Option 2: Production Install

```bash
pip install -r requirements.txt
pip install .
```

## Quick Start

### 1. Configure Database Connections

```bash
# Copy example config
cp ../config/database-connections.example.yml ../config/database-connections.yml

# Edit with your database details
nano ../config/database-connections.yml
```

### 2. Set Environment Variables

```bash
# Add to ~/.zshrc or ~/.bashrc
export METABASE_PASSWORD='your_password_here'
```

### 3. Use the CLI

```bash
# List VMs
excel-auto vm list

# Start Excel VM
excel-auto vm start "Windows Analytics"

# Install ODBC drivers
excel-auto odbc install-drivers "Windows Analytics" --driver all

# Configure DSN from config file
excel-auto odbc configure "Windows Analytics" --connection metabase_prod

# List configured DSNs
excel-auto odbc list "Windows Analytics"

# Create snapshot before changes
excel-auto vm snapshot "Windows Analytics" --name "before_excel_updates"

# List snapshots
excel-auto vm snapshots "Windows Analytics"
```

## Python API Usage

### VM Management

```python
from excel_automation import VMManager

# Create VM manager
vm = VMManager("Windows Analytics")

# Start VM and wait for boot
vm.start(wait=True, wait_seconds=45)

# Check if running
if vm.is_running():
    print(f"VM IP: {vm.get_ip()}")

# Create snapshot
snap_name = vm.snapshot(name="before_changes", description="Safety snapshot")

# Execute command in VM
result = vm.execute("ipconfig /all")
print(result.stdout)

# Stop VM
vm.stop()
```

### ODBC Configuration

```python
from excel_automation import VMManager, ODBCConfigurator

# Set up VM and ODBC configurator
vm = VMManager("Windows Analytics")
vm.start()

odbc = ODBCConfigurator(vm)

# Install PostgreSQL driver
odbc.install_driver("postgresql")

# Configure DSN
odbc.configure_dsn(
    dsn_name="Metabase_Production",
    driver="PostgreSQL Unicode(x64)",
    server="db.company.com",
    database="metabase",
    port=5432,
    username="analytics_user",
)

# List all DSNs
dsns = odbc.list_dsns()
for dsn in dsns:
    print(f"{dsn['name']}: {dsn['driver']}")

# Test DSN exists
if odbc.test_connection("Metabase_Production"):
    print("DSN configured correctly")
```

### Configuration Loading

```python
from excel_automation import ConfigLoader
from pathlib import Path

# Load config
config = ConfigLoader(Path("config/database-connections.yml"))

# Get connection details
metabase = config.get_connection("metabase_prod")
print(f"Host: {metabase['host']}")
print(f"Database: {metabase['database']}")

# List all connections
connections = config.list_connections()
print(f"Available connections: {', '.join(connections)}")
```

### Logging

```python
from excel_automation import setup_logger
from pathlib import Path

# Set up logger
logger = setup_logger(
    name="my_automation",
    level="INFO",
    log_file=Path("logs/automation.log"),
)

logger.info("Starting automation")
logger.warning("VM startup taking longer than expected")
logger.error("Failed to connect to database")
```

## CLI Commands

### VM Commands

```bash
# List all VMs
excel-auto vm list

# Start VM
excel-auto vm start "Windows Analytics"
excel-auto vm start "Windows Analytics" --no-wait  # Don't wait for boot

# Stop VM
excel-auto vm stop "Windows Analytics"
excel-auto vm stop "Windows Analytics" --force  # Force stop

# Create snapshot
excel-auto vm snapshot "Windows Analytics"
excel-auto vm snapshot "Windows Analytics" --name "before_updates"
excel-auto vm snapshot "Windows Analytics" --name "backup" --description "Weekly backup"

# List snapshots
excel-auto vm snapshots "Windows Analytics"
```

### ODBC Commands

```bash
# Install drivers
excel-auto odbc install-drivers "Windows Analytics" --driver postgresql
excel-auto odbc install-drivers "Windows Analytics" --driver mysql
excel-auto odbc install-drivers "Windows Analytics" --driver all

# Configure DSN from config file
excel-auto odbc configure "Windows Analytics" --connection metabase_prod

# List DSNs
excel-auto odbc list "Windows Analytics"
```

### Configuration Commands

```bash
# List configured connections
excel-auto config list-connections

# Validate config file
excel-auto config validate
```

## Configuration File Format

```yaml
connections:
  metabase_prod:
    type: postgresql
    driver: "PostgreSQL Unicode(x64)"
    host: "db.company.com"
    port: 5432
    database: "metabase"
    username: "analytics_user"
    password: "${METABASE_PASSWORD}"  # From environment variable
    dsn_name: "Metabase_Production"
    ssl_mode: "require"
    description: "Production Metabase database"

vm:
  name: "Windows Analytics"
  startup_wait_seconds: 45

logging:
  level: "INFO"
  file: "logs/excel-automation.log"
```

## Security Best Practices

1. **Never commit passwords**: Always use environment variables
2. **Use .gitignore**: Config files with secrets are ignored by default
3. **Rotate credentials**: Change passwords regularly
4. **Use read-only accounts**: For analytics, use read-only database users
5. **Enable SSL**: Always use SSL for database connections

## Advanced Usage

### Automated Data Pipeline

```python
from excel_automation import VMManager, ConfigLoader
from pathlib import Path
import pandas as pd

# Load config
config = ConfigLoader(Path("config/database-connections.yml"))
vm_config = config.get_vm_config()

# Start VM
vm = VMManager(vm_config['name'])
vm.start()

# Execute Excel macro to refresh data
vm.execute(
    'powershell -Command "'
    '$excel = New-Object -ComObject Excel.Application; '
    '$wb = $excel.Workbooks.Open(\\\"C:\\Analytics\\Dashboard.xlsx\\\"); '
    '$excel.Run(\\\"RefreshAllData\\\"); '
    '$wb.Save(); '
    '$excel.Quit()'
    '"'
)

# Process results...
```

### Snapshot Rotation

```python
from excel_automation import VMManager
import time

vm = VMManager("Windows Analytics")

# Keep only last 7 snapshots
snapshots = vm.list_snapshots()
if len(snapshots) > 7:
    # Delete oldest snapshots
    for snap in snapshots[:-7]:
        vm._run_prlctl("snapshot-delete", vm.vm_name, "--id", snap['id'])

# Create new snapshot
vm.snapshot(name=f"auto_{int(time.time())}")
```

## Troubleshooting

### prlctl not found

Ensure Parallels Desktop Pro or Business is installed. Standard edition doesn't include CLI tools.

### Environment variable not set

```bash
# Check if set
echo $METABASE_PASSWORD

# Set temporarily
export METABASE_PASSWORD='your_password'

# Set permanently (add to ~/.zshrc or ~/.bashrc)
echo "export METABASE_PASSWORD='your_password'" >> ~/.zshrc
```

### VM won't start

```bash
# Check VM exists
prlctl list -a

# Check VM status
prlctl list "Windows Analytics" -i

# Try manual start
prlctl start "Windows Analytics"
```

### ODBC driver installation fails

- Ensure VM is running
- Check Parallels Shared Folders are enabled
- Verify internet connection in VM
- Check Windows Event Viewer for errors

## Development

### Running Tests

```bash
pytest
pytest --cov=excel_automation
```

### Code Quality

```bash
# Format code
black excel_automation/

# Sort imports
isort excel_automation/

# Type checking
mypy excel_automation/

# Linting
flake8 excel_automation/
```

## License

MIT License - See LICENSE file for details

## Support

- GitHub Issues: https://github.com/UncertainMeow/Parallels_Scripts/issues
- Documentation: ../docs/QUICKSTART_EXCEL_SQL.md
- Examples: ../docs/WORKFLOWS.md
