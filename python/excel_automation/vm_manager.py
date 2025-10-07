"""
Parallels Desktop VM management
"""

import subprocess
import time
import re
from typing import Optional, Dict, List
from dataclasses import dataclass
from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class VMInfo:
    """Information about a Parallels VM"""

    name: str
    uuid: str
    status: str
    os: str
    ip: Optional[str] = None
    uptime: Optional[str] = None


class VMManager:
    """Manage Parallels Desktop virtual machines"""

    def __init__(self, vm_name: str):
        """
        Initialize VM manager.

        Args:
            vm_name: Name of the Parallels VM to manage
        """
        self.vm_name = vm_name
        self._check_parallels()

    def _check_parallels(self) -> None:
        """Verify that prlctl is available"""
        try:
            subprocess.run(
                ["prlctl", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "prlctl not found. Ensure Parallels Desktop Pro/Business is installed."
            )

    def _run_prlctl(
        self, *args, check: bool = True, capture: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run prlctl command.

        Args:
            *args: Command arguments
            check: Raise exception on error
            capture: Capture output

        Returns:
            CompletedProcess instance
        """
        cmd = ["prlctl"] + list(args)
        logger.debug(f"Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"Command failed: {' '.join(cmd)}")
            logger.error(f"Error: {result.stderr}")

        return result

    def exists(self) -> bool:
        """Check if VM exists"""
        result = self._run_prlctl("list", "-a", "--no-header", check=False)
        return self.vm_name in result.stdout

    def is_running(self) -> bool:
        """Check if VM is running"""
        if not self.exists():
            return False

        result = self._run_prlctl("list", self.vm_name, "--no-header", "-o", "status")
        return "running" in result.stdout.lower()

    def get_info(self) -> VMInfo:
        """
        Get VM information.

        Returns:
            VMInfo object with VM details

        Raises:
            RuntimeError: If VM doesn't exist
        """
        if not self.exists():
            raise RuntimeError(f"VM '{self.vm_name}' not found")

        result = self._run_prlctl(
            "list", self.vm_name, "--no-header", "-o", "name,uuid,status,os,ip,uptime"
        )

        # Parse output
        parts = result.stdout.strip().split(maxsplit=5)
        return VMInfo(
            name=parts[0] if len(parts) > 0 else self.vm_name,
            uuid=parts[1] if len(parts) > 1 else "",
            status=parts[2] if len(parts) > 2 else "unknown",
            os=parts[3] if len(parts) > 3 else "unknown",
            ip=parts[4] if len(parts) > 4 and parts[4] != "-" else None,
            uptime=parts[5] if len(parts) > 5 else None,
        )

    def start(self, wait: bool = True, wait_seconds: int = 45) -> None:
        """
        Start the VM.

        Args:
            wait: Wait for VM to fully boot
            wait_seconds: Seconds to wait after starting
        """
        if self.is_running():
            logger.info(f"VM '{self.vm_name}' is already running")
            return

        logger.info(f"Starting VM: {self.vm_name}")
        self._run_prlctl("start", self.vm_name)

        if wait:
            logger.info(f"Waiting {wait_seconds}s for VM to boot...")
            time.sleep(wait_seconds)

            # Verify it started
            if not self.is_running():
                raise RuntimeError(f"VM '{self.vm_name}' failed to start")

            logger.info(f"✓ VM '{self.vm_name}' is running")

    def stop(self, force: bool = False) -> None:
        """
        Stop the VM.

        Args:
            force: Force stop (kill) instead of graceful shutdown
        """
        if not self.is_running():
            logger.info(f"VM '{self.vm_name}' is not running")
            return

        logger.info(f"Stopping VM: {self.vm_name}")

        if force:
            self._run_prlctl("stop", self.vm_name, "--kill")
        else:
            self._run_prlctl("stop", self.vm_name)

        logger.info(f"✓ VM '{self.vm_name}' stopped")

    def restart(self, wait: bool = True, wait_seconds: int = 45) -> None:
        """
        Restart the VM.

        Args:
            wait: Wait for VM to fully boot
            wait_seconds: Seconds to wait after restarting
        """
        logger.info(f"Restarting VM: {self.vm_name}")
        self.stop()
        time.sleep(5)  # Brief pause before restart
        self.start(wait=wait, wait_seconds=wait_seconds)

    def snapshot(self, name: Optional[str] = None, description: str = "") -> str:
        """
        Create a snapshot of the VM.

        Args:
            name: Snapshot name (auto-generated if not provided)
            description: Snapshot description

        Returns:
            Snapshot name
        """
        if not name:
            name = f"auto_{int(time.time())}"

        logger.info(f"Creating snapshot: {name}")

        cmd = ["snapshot", self.vm_name, "--name", name]
        if description:
            cmd.extend(["--description", description])

        self._run_prlctl(*cmd)
        logger.info(f"✓ Snapshot created: {name}")

        return name

    def list_snapshots(self) -> List[Dict[str, str]]:
        """
        List all snapshots for the VM.

        Returns:
            List of snapshot dictionaries with 'id', 'name', 'date'
        """
        result = self._run_prlctl("snapshot-list", self.vm_name)

        snapshots = []
        for line in result.stdout.split("\n"):
            # Parse snapshot format: {UUID} NAME DATE
            match = re.match(r"\{([^}]+)\}\s+(.+?)\s+(\d{4}-\d{2}-\d{2}.*)$", line)
            if match:
                snapshots.append(
                    {
                        "id": match.group(1),
                        "name": match.group(2).strip(),
                        "date": match.group(3).strip(),
                    }
                )

        return snapshots

    def restore_snapshot(self, snapshot_id: str) -> None:
        """
        Restore VM to a snapshot.

        Args:
            snapshot_id: Snapshot UUID to restore

        Warning:
            This will discard all changes since the snapshot
        """
        logger.warning(f"Restoring snapshot: {snapshot_id}")
        logger.warning("All changes since snapshot will be lost!")

        self._run_prlctl("snapshot-switch", self.vm_name, "--id", snapshot_id)
        logger.info(f"✓ Snapshot restored: {snapshot_id}")

    def execute(
        self, command: str, check: bool = True, capture: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Execute a command in the VM.

        Args:
            command: Command to execute
            check: Raise exception on error
            capture: Capture output

        Returns:
            CompletedProcess instance

        Note:
            VM must be running and have Parallels Tools installed
        """
        if not self.is_running():
            raise RuntimeError(f"VM '{self.vm_name}' is not running")

        logger.debug(f"Executing in VM: {command}")

        return self._run_prlctl("exec", self.vm_name, command, check=check)

    def get_ip(self) -> Optional[str]:
        """
        Get VM IP address.

        Returns:
            IP address or None if not available
        """
        info = self.get_info()
        return info.ip

    def wait_for_ip(self, timeout: int = 60) -> str:
        """
        Wait for VM to get an IP address.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            IP address

        Raises:
            TimeoutError: If timeout reached without getting IP
        """
        logger.info(f"Waiting for VM to get IP address (timeout: {timeout}s)...")

        start = time.time()
        while time.time() - start < timeout:
            ip = self.get_ip()
            if ip:
                logger.info(f"✓ VM IP: {ip}")
                return ip

            time.sleep(2)

        raise TimeoutError(f"VM did not get IP address within {timeout}s")
