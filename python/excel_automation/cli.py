"""
Command-line interface for Excel automation
"""

import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .vm_manager import VMManager
from .odbc_config import ODBCConfigurator
from .config_loader import ConfigLoader
from .logger import setup_logger

console = Console()
logger = setup_logger(__name__)


@click.group()
@click.option(
    '--config',
    '-c',
    type=click.Path(exists=True, path_type=Path),
    default=Path('config/database-connections.yml'),
    help='Configuration file path',
)
@click.pass_context
def cli(ctx, config):
    """Excel automation CLI for Parallels Desktop"""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config


@cli.group()
def vm():
    """VM management commands"""
    pass


@vm.command('list')
@click.pass_context
def vm_list(ctx):
    """List all Parallels VMs"""
    try:
        import subprocess

        result = subprocess.run(
            ['prlctl', 'list', '-a', '--no-header', '-o', 'name,status,os,ip'],
            capture_output=True,
            text=True,
            check=True,
        )

        table = Table(title="Parallels Virtual Machines")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("OS", style="yellow")
        table.add_column("IP", style="blue")

        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split(maxsplit=3)
                status_style = "green" if "running" in parts[1].lower() else "red"
                table.add_row(
                    parts[0],
                    f"[{status_style}]{parts[1]}[/{status_style}]",
                    parts[2] if len(parts) > 2 else "-",
                    parts[3] if len(parts) > 3 else "-",
                )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@vm.command('start')
@click.argument('vm_name')
@click.option('--wait/--no-wait', default=True, help='Wait for VM to boot')
@click.option('--wait-seconds', default=45, help='Seconds to wait after start')
@click.pass_context
def vm_start(ctx, vm_name, wait, wait_seconds):
    """Start a VM"""
    try:
        vm_mgr = VMManager(vm_name)

        with console.status(f"[cyan]Starting VM: {vm_name}..."):
            vm_mgr.start(wait=wait, wait_seconds=wait_seconds)

        console.print(f"[green]✓[/green] VM started: {vm_name}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@vm.command('stop')
@click.argument('vm_name')
@click.option('--force', is_flag=True, help='Force stop (kill)')
@click.pass_context
def vm_stop(ctx, vm_name, force):
    """Stop a VM"""
    try:
        vm_mgr = VMManager(vm_name)

        with console.status(f"[cyan]Stopping VM: {vm_name}..."):
            vm_mgr.stop(force=force)

        console.print(f"[green]✓[/green] VM stopped: {vm_name}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@vm.command('snapshot')
@click.argument('vm_name')
@click.option('--name', '-n', help='Snapshot name (auto-generated if not provided)')
@click.option('--description', '-d', default='', help='Snapshot description')
@click.pass_context
def vm_snapshot(ctx, vm_name, name, description):
    """Create a VM snapshot"""
    try:
        vm_mgr = VMManager(vm_name)

        with console.status(f"[cyan]Creating snapshot for: {vm_name}..."):
            snap_name = vm_mgr.snapshot(name=name, description=description)

        console.print(f"[green]✓[/green] Snapshot created: {snap_name}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@vm.command('snapshots')
@click.argument('vm_name')
@click.pass_context
def vm_snapshots(ctx, vm_name):
    """List VM snapshots"""
    try:
        vm_mgr = VMManager(vm_name)
        snapshots = vm_mgr.list_snapshots()

        if not snapshots:
            console.print(f"[yellow]No snapshots found for: {vm_name}[/yellow]")
            return

        table = Table(title=f"Snapshots for {vm_name}")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Date", style="yellow")

        for snap in snapshots:
            table.add_row(snap['id'][:8] + '...', snap['name'], snap['date'])

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.group()
def odbc():
    """ODBC configuration commands"""
    pass


@odbc.command('install-drivers')
@click.argument('vm_name')
@click.option(
    '--driver',
    '-d',
    multiple=True,
    type=click.Choice(['postgresql', 'mysql', 'sqlserver', 'all']),
    help='Driver to install (can specify multiple)',
)
@click.pass_context
def odbc_install_drivers(ctx, vm_name, driver):
    """Install ODBC drivers in Windows VM"""
    try:
        vm_mgr = VMManager(vm_name)

        if not vm_mgr.is_running():
            console.print(f"[yellow]Starting VM: {vm_name}...[/yellow]")
            vm_mgr.start()

        odbc_config = ODBCConfigurator(vm_mgr)

        drivers_to_install = []
        if 'all' in driver or not driver:
            drivers_to_install = ['postgresql', 'mysql', 'sqlserver']
        else:
            drivers_to_install = list(driver)

        for drv in drivers_to_install:
            with console.status(f"[cyan]Installing {drv} driver..."):
                odbc_config.install_driver(drv)

            console.print(f"[green]✓[/green] {drv} driver installed")

        console.print(f"\n[green]✓ All drivers installed successfully[/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@odbc.command('configure')
@click.argument('vm_name')
@click.option('--connection', '-c', help='Connection name from config file')
@click.pass_context
def odbc_configure(ctx, vm_name, connection):
    """Configure ODBC DSN from config file"""
    try:
        config_path = ctx.obj['config_path']

        if not config_path.exists():
            console.print(
                f"[red]Error:[/red] Config file not found: {config_path}\n"
                f"Copy config/database-connections.example.yml to {config_path}"
            )
            sys.exit(1)

        config_loader = ConfigLoader(config_path)
        conn_config = config_loader.get_connection(connection)

        if not conn_config:
            console.print(f"[red]Error:[/red] Connection not found: {connection}")
            console.print(
                f"\nAvailable connections: {', '.join(config_loader.list_connections())}"
            )
            sys.exit(1)

        vm_mgr = VMManager(vm_name)

        if not vm_mgr.is_running():
            console.print(f"[yellow]Starting VM: {vm_name}...[/yellow]")
            vm_mgr.start()

        odbc_config = ODBCConfigurator(vm_mgr)

        # Configure DSN
        with console.status(f"[cyan]Configuring DSN: {conn_config['dsn_name']}..."):
            odbc_config.configure_dsn(
                dsn_name=conn_config['dsn_name'],
                driver=conn_config['driver'],
                server=conn_config['host'],
                database=conn_config['database'],
                port=conn_config.get('port'),
                username=conn_config.get('username'),
                additional_props={
                    k: v
                    for k, v in conn_config.items()
                    if k
                    not in [
                        'type',
                        'driver',
                        'host',
                        'database',
                        'port',
                        'username',
                        'password',
                        'dsn_name',
                        'description',
                    ]
                },
            )

        console.print(f"[green]✓ DSN configured: {conn_config['dsn_name']}[/green]")
        console.print(f"  Description: {conn_config.get('description', 'N/A')}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@odbc.command('list')
@click.argument('vm_name')
@click.pass_context
def odbc_list(ctx, vm_name):
    """List configured ODBC DSNs"""
    try:
        vm_mgr = VMManager(vm_name)

        if not vm_mgr.is_running():
            console.print(f"[red]Error:[/red] VM must be running: {vm_name}")
            sys.exit(1)

        odbc_config = ODBCConfigurator(vm_mgr)

        with console.status("[cyan]Fetching ODBC DSNs..."):
            dsns = odbc_config.list_dsns()

        if not dsns:
            console.print("[yellow]No ODBC DSNs found[/yellow]")
            return

        table = Table(title=f"ODBC DSNs in {vm_name}")
        table.add_column("Name", style="cyan")
        table.add_column("Driver", style="green")
        table.add_column("Type", style="yellow")

        for dsn in dsns:
            table.add_row(dsn['name'], dsn['driver'], dsn['type'])

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.group()
def config():
    """Configuration management"""
    pass


@config.command('list-connections')
@click.pass_context
def config_list_connections(ctx):
    """List configured database connections"""
    try:
        config_path = ctx.obj['config_path']

        if not config_path.exists():
            console.print(
                f"[yellow]Config file not found: {config_path}[/yellow]\n"
                f"Copy config/database-connections.example.yml to {config_path}"
            )
            return

        config_loader = ConfigLoader(config_path)
        config_data = config_loader.load()
        connections = config_data.get('connections', {})

        if not connections:
            console.print("[yellow]No connections configured[/yellow]")
            return

        table = Table(title="Configured Database Connections")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Host", style="yellow")
        table.add_column("Database", style="blue")
        table.add_column("DSN Name", style="magenta")

        for name, conn in connections.items():
            table.add_row(
                name,
                conn.get('type', 'N/A'),
                conn.get('host', 'N/A'),
                conn.get('database', 'N/A'),
                conn.get('dsn_name', 'N/A'),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@config.command('validate')
@click.pass_context
def config_validate(ctx):
    """Validate configuration file"""
    try:
        config_path = ctx.obj['config_path']

        if not config_path.exists():
            console.print(f"[red]Error:[/red] Config file not found: {config_path}")
            sys.exit(1)

        with console.status("[cyan]Validating configuration..."):
            config_loader = ConfigLoader(config_path)
            config_data = config_loader.load()

        # Basic validation
        errors = []

        if 'connections' not in config_data:
            errors.append("Missing 'connections' section")

        for name, conn in config_data.get('connections', {}).items():
            required = ['type', 'driver', 'host', 'database', 'dsn_name']
            missing = [f for f in required if f not in conn]

            if missing:
                errors.append(f"Connection '{name}' missing: {', '.join(missing)}")

        if errors:
            console.print("[red]✗ Configuration validation failed:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            sys.exit(1)

        console.print("[green]✓ Configuration is valid[/green]")

    except ValueError as e:
        # Environment variable not set
        console.print(f"[red]✗ Configuration validation failed:[/red]")
        console.print(f"  {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def main():
    """Entry point for CLI"""
    cli(obj={})


if __name__ == '__main__':
    main()
