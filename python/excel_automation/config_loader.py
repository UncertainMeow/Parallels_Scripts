"""
Configuration file loader with environment variable substitution
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from .logger import setup_logger

logger = setup_logger(__name__)


class ConfigLoader:
    """Load and parse YAML configuration files"""

    ENV_VAR_PATTERN = re.compile(r'\$\{(\w+)\}')

    def __init__(self, config_file: Path):
        """
        Initialize config loader.

        Args:
            config_file: Path to YAML configuration file
        """
        self.config_file = Path(config_file)

        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

    def load(self) -> Dict[str, Any]:
        """
        Load configuration file with environment variable substitution.

        Returns:
            Parsed configuration dictionary

        Raises:
            ValueError: If environment variable is not set
        """
        logger.debug(f"Loading config: {self.config_file}")

        with open(self.config_file, 'r') as f:
            content = f.read()

        # Substitute environment variables
        content = self._substitute_env_vars(content)

        # Parse YAML
        config = yaml.safe_load(content)

        logger.debug(f"✓ Config loaded: {len(config)} top-level keys")

        return config

    def _substitute_env_vars(self, content: str) -> str:
        """
        Substitute environment variables in format ${VAR_NAME}.

        Args:
            content: Configuration file content

        Returns:
            Content with substituted variables

        Raises:
            ValueError: If required environment variable is not set
        """

        def replace_var(match):
            var_name = match.group(1)
            value = os.environ.get(var_name)

            if value is None:
                raise ValueError(
                    f"Environment variable not set: {var_name}\\n"
                    f"Set it with: export {var_name}=<value>"
                )

            # Mask value in logs if it looks like a password
            if any(
                keyword in var_name.lower()
                for keyword in ['password', 'secret', 'token', 'key']
            ):
                logger.debug(f"Substituting {var_name}=***")
            else:
                logger.debug(f"Substituting {var_name}={value}")

            return value

        return self.ENV_VAR_PATTERN.sub(replace_var, content)

    def get_connection(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get database connection configuration by name.

        Args:
            name: Connection name

        Returns:
            Connection configuration or None if not found
        """
        config = self.load()
        connections = config.get('connections', {})
        return connections.get(name)

    def list_connections(self) -> list[str]:
        """
        List all configured database connections.

        Returns:
            List of connection names
        """
        config = self.load()
        connections = config.get('connections', {})
        return list(connections.keys())

    def get_vm_config(self) -> Dict[str, Any]:
        """Get VM configuration section"""
        config = self.load()
        return config.get('vm', {})

    def get_excel_config(self) -> Dict[str, Any]:
        """Get Excel configuration section"""
        config = self.load()
        return config.get('excel', {})

    def get_automation_config(self) -> Dict[str, Any]:
        """Get automation configuration section"""
        config = self.load()
        return config.get('automation', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration section"""
        config = self.load()
        return config.get('logging', {})
