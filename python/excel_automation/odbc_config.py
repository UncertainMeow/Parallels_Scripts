"""
ODBC configuration manager for Windows VMs
Automates installation and configuration of ODBC drivers and DSNs
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from .vm_manager import VMManager
from .logger import setup_logger

logger = setup_logger(__name__)


class ODBCConfigurator:
    """Configure ODBC drivers and DSNs in Windows VMs"""

    # ODBC driver download URLs
    DRIVERS = {
        "postgresql": {
            "name": "PostgreSQL Unicode(x64)",
            "url": "https://ftp.postgresql.org/pub/odbc/releases/REL-16_00_0000/psqlodbc_x64.msi",
            "file": "psqlodbc_x64.msi",
        },
        "mysql": {
            "name": "MySQL ODBC 8.0 Driver",
            "url": "https://dev.mysql.com/get/Downloads/Connector-ODBC/8.0/mysql-connector-odbc-8.0.35-winx64.msi",
            "file": "mysql_odbc_x64.msi",
        },
        "sqlserver": {
            "name": "ODBC Driver 18 for SQL Server",
            "url": "https://go.microsoft.com/fwlink/?linkid=2249006",
            "file": "msodbcsql_x64.msi",
        },
    }

    def __init__(self, vm: VMManager):
        """
        Initialize ODBC configurator.

        Args:
            vm: VMManager instance for the target Windows VM
        """
        self.vm = vm

    def install_driver(self, driver_type: str) -> None:
        """
        Install ODBC driver in Windows VM.

        Args:
            driver_type: One of 'postgresql', 'mysql', 'sqlserver'

        Raises:
            ValueError: If driver_type is not supported
            RuntimeError: If installation fails
        """
        if driver_type not in self.DRIVERS:
            raise ValueError(
                f"Unsupported driver: {driver_type}. "
                f"Supported: {', '.join(self.DRIVERS.keys())}"
            )

        driver = self.DRIVERS[driver_type]
        logger.info(f"Installing {driver['name']}...")

        # Create PowerShell script to download and install
        script = self._generate_driver_install_script(driver)

        # Execute in VM
        self._execute_powershell(script, f"install_{driver_type}_driver")

        logger.info(f"✓ {driver['name']} installed")

    def _generate_driver_install_script(self, driver: Dict[str, str]) -> str:
        """Generate PowerShell script to install ODBC driver"""
        return f"""
# Install {driver['name']}
$ErrorActionPreference = "Stop"

$url = "{driver['url']}"
$installer = "$env:TEMP\\{driver['file']}"

Write-Host "Downloading {driver['name']}..."
try {{
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
    Write-Host "Download complete"
}} catch {{
    Write-Error "Failed to download: $_"
    exit 1
}}

Write-Host "Installing {driver['name']}..."
try {{
    $arguments = "/i `"$installer`" /quiet /norestart ADDLOCAL=ALL"
    Start-Process msiexec.exe -ArgumentList $arguments -Wait -NoNewWindow
    Write-Host "Installation complete"
}} catch {{
    Write-Error "Failed to install: $_"
    exit 1
}}

# Cleanup
Remove-Item $installer -ErrorAction SilentlyContinue

Write-Host "✓ {driver['name']} installed successfully"
"""

    def configure_dsn(
        self,
        dsn_name: str,
        driver: str,
        server: str,
        database: str,
        port: Optional[int] = None,
        username: Optional[str] = None,
        additional_props: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Configure ODBC DSN in Windows VM.

        Args:
            dsn_name: Data Source Name
            driver: ODBC driver name (e.g., "PostgreSQL Unicode(x64)")
            server: Database server hostname
            database: Database name
            port: Database port (optional)
            username: Database username (optional)
            additional_props: Additional driver-specific properties

        Note:
            Passwords are NOT configured here for security.
            Users will be prompted when connecting from Excel.
        """
        logger.info(f"Configuring DSN: {dsn_name}")

        script = self._generate_dsn_config_script(
            dsn_name=dsn_name,
            driver=driver,
            server=server,
            database=database,
            port=port,
            username=username,
            additional_props=additional_props or {},
        )

        self._execute_powershell(script, f"configure_dsn_{dsn_name}")

        logger.info(f"✓ DSN configured: {dsn_name}")

    def _generate_dsn_config_script(
        self,
        dsn_name: str,
        driver: str,
        server: str,
        database: str,
        port: Optional[int],
        username: Optional[str],
        additional_props: Dict[str, str],
    ) -> str:
        """Generate PowerShell script to configure ODBC DSN"""

        # Build property list
        properties = [
            f'Server={server}',
            f'Database={database}',
        ]

        if port:
            properties.append(f'Port={port}')

        if username:
            properties.append(f'UID={username}')

        # Add additional driver-specific properties
        for key, value in additional_props.items():
            properties.append(f'{key}={value}')

        properties_str = '", "'.join(properties)

        return f"""
# Configure ODBC DSN: {dsn_name}
$ErrorActionPreference = "Stop"

$dsnName = "{dsn_name}"
$driver = "{driver}"

Write-Host "Configuring DSN: $dsnName"

try {{
    # Remove existing DSN if it exists
    Remove-OdbcDsn -Name $dsnName -DsnType "System" -ErrorAction SilentlyContinue

    # Create new System DSN
    Add-OdbcDsn `
        -Name $dsnName `
        -DriverName $driver `
        -DsnType "System" `
        -SetPropertyValue @("{properties_str}")

    Write-Host "✓ DSN configured successfully"
}} catch {{
    Write-Error "Failed to configure DSN: $_"
    exit 1
}}

# Verify DSN was created
$dsn = Get-OdbcDsn -Name $dsnName -DsnType "System" -ErrorAction SilentlyContinue
if ($dsn) {{
    Write-Host "✓ DSN verified: $dsnName"
    Write-Host "  Driver: $($dsn.DriverName)"
}} else {{
    Write-Error "DSN verification failed"
    exit 1
}}
"""

    def list_dsns(self) -> List[Dict[str, str]]:
        """
        List all ODBC DSNs in Windows VM.

        Returns:
            List of DSN dictionaries with 'name', 'driver', 'type'
        """
        logger.info("Listing ODBC DSNs...")

        script = """
# List all ODBC DSNs
Get-OdbcDsn | Select-Object Name, DriverName, DsnType | ConvertTo-Json -Compress
"""

        result = self._execute_powershell(script, "list_dsns")

        # Parse JSON output
        import json

        try:
            dsns = json.loads(result.stdout)
            # Handle single DSN (not in array)
            if isinstance(dsns, dict):
                dsns = [dsns]

            return [
                {
                    "name": dsn.get("Name", ""),
                    "driver": dsn.get("DriverName", ""),
                    "type": dsn.get("DsnType", ""),
                }
                for dsn in dsns
            ]
        except json.JSONDecodeError:
            logger.warning("No DSNs found or failed to parse")
            return []

    def test_connection(self, dsn_name: str) -> bool:
        """
        Test ODBC connection (without password).

        Args:
            dsn_name: DSN name to test

        Returns:
            True if DSN exists and driver is available

        Note:
            This only tests that the DSN is configured, not that it can connect
            (connection requires password)
        """
        logger.info(f"Testing DSN configuration: {dsn_name}")

        script = f"""
# Test DSN configuration
$dsn = Get-OdbcDsn -Name "{dsn_name}" -ErrorAction SilentlyContinue
if ($dsn) {{
    Write-Host "✓ DSN exists: {dsn_name}"
    Write-Host "  Driver: $($dsn.DriverName)"
    exit 0
}} else {{
    Write-Error "DSN not found: {dsn_name}"
    exit 1
}}
"""

        try:
            self._execute_powershell(script, f"test_dsn_{dsn_name}")
            logger.info(f"✓ DSN configuration valid: {dsn_name}")
            return True
        except RuntimeError:
            logger.error(f"✗ DSN configuration invalid: {dsn_name}")
            return False

    def _execute_powershell(
        self, script: str, script_name: str
    ) -> subprocess.CompletedProcess:
        """
        Execute PowerShell script in Windows VM.

        Args:
            script: PowerShell script content
            script_name: Name for the script file

        Returns:
            CompletedProcess instance

        Raises:
            RuntimeError: If script execution fails
        """
        # Write script to temp file
        script_file = Path(tempfile.gettempdir()) / f"{script_name}.ps1"
        script_file.write_text(script)

        logger.debug(f"Created PowerShell script: {script_file}")

        # Execute via prlctl exec
        # Assumes Parallels Shared Folders are enabled (\\psf\Home)
        vm_script_path = f"\\\\psf\\Home\\tmp\\{script_name}.ps1"

        try:
            # Ensure VM can access the script
            # Copy to shared location if needed
            import shutil

            shared_tmp = Path.home() / ".parallels_shared" / "tmp"
            shared_tmp.mkdir(parents=True, exist_ok=True)

            shared_script = shared_tmp / f"{script_name}.ps1"
            shutil.copy(script_file, shared_script)

            # Execute in VM
            result = self.vm.execute(
                f'powershell.exe -ExecutionPolicy Bypass -File "{vm_script_path}"'
            )

            logger.debug(f"Script output:\n{result.stdout}")

            return result

        except subprocess.CalledProcessError as e:
            logger.error(f"PowerShell script failed: {script_name}")
            logger.error(f"Error: {e.stderr}")
            raise RuntimeError(f"Failed to execute PowerShell script: {script_name}")
        finally:
            # Cleanup
            script_file.unlink(missing_ok=True)

    def install_all_drivers(self) -> None:
        """Install all supported ODBC drivers"""
        logger.info("Installing all ODBC drivers...")

        for driver_type in self.DRIVERS.keys():
            try:
                self.install_driver(driver_type)
            except Exception as e:
                logger.error(f"Failed to install {driver_type}: {e}")
                # Continue with other drivers

        logger.info("✓ Driver installation complete")


# Import subprocess for CompletedProcess type hint
import subprocess
