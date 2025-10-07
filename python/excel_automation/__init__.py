"""
Excel Automation Framework for Parallels Desktop
Automates Excel + ODBC workflows for corporate data analytics
"""

__version__ = "0.1.0"
__author__ = "Kellen Malstrom"

from .vm_manager import VMManager
from .odbc_config import ODBCConfigurator
from .excel_controller import ExcelController
from .logger import setup_logger

__all__ = [
    "VMManager",
    "ODBCConfigurator",
    "ExcelController",
    "setup_logger",
]
