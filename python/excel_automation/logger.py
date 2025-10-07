"""
Logging configuration for Excel automation
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str = "excel_automation",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    max_bytes: int = 100 * 1024 * 1024,  # 100MB
    backup_count: int = 10,
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (optional)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with color formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Console format with colors (if terminal supports it)
    if sys.stdout.isatty():
        console_format = "%(levelname_color)s[%(levelname)s]%(reset)s %(message)s"
    else:
        console_format = "[%(levelname)s] %(message)s"

    console_formatter = ColoredFormatter(console_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)

        file_format = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for terminal output"""

    COLORS = {
        "DEBUG": "\033[0;36m",  # Cyan
        "INFO": "\033[0;34m",  # Blue
        "WARNING": "\033[1;33m",  # Yellow
        "ERROR": "\033[0;31m",  # Red
        "CRITICAL": "\033[1;35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        # Add color codes to record
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname_color = self.COLORS[levelname]
            record.reset = self.RESET
        else:
            record.levelname_color = ""
            record.reset = ""

        return super().format(record)
