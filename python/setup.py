"""
Setup script for Excel Automation Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements
requirements = Path("requirements.txt").read_text().splitlines()
requirements = [r for r in requirements if r and not r.startswith("#")]

# Read long description
long_description = Path("../README.md").read_text()

setup(
    name="excel-automation",
    version="0.1.0",
    description="Excel + ODBC automation framework for Parallels Desktop",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kellen Malstrom",
    author_email="kellen@uncertainmeow.com",
    url="https://github.com/UncertainMeow/Parallels_Scripts",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "excel-auto=excel_automation.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Office/Business",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
