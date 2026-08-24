import re
from pathlib import Path

from setuptools import setup, find_packages

HERE = Path(__file__).parent


def read_version() -> str:
    """Read __version__ from _version.py without importing the package."""
    source = (HERE / "_version.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', source, re.M)
    if not match:
        raise RuntimeError("Could not find __version__ in _version.py")
    return match.group(1)


setup(
    name="portfolio-manager",
    version=read_version(),
    author="Martin Birrell",
    author_email="martin.birrell@gmail.com",
    description="A desktop application for managing investment portfolios",
    long_description=(HERE / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/mbirrell66/PortfolioM",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Win32 (MS Windows)",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.10",
    install_requires=[
        "PySide6>=6.5.0",
        "SQLAlchemy>=2.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pyqtgraph>=0.13.0",
        "yfinance>=0.2.18",
        "requests>=2.28.0",
        "feedparser>=6.0.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "gui_scripts": [
            "portfolio-manager=main:main",
        ],
    },
)
