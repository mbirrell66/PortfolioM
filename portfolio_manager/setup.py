from setuptools import setup, find_packages

setup(
    name="portfolio-manager",
    version="1.0.0",
    author="Portfolio Manager Team",
    author_email="portfolio@example.com",
    description="A desktop application for managing investment portfolios",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/portfolio-manager",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
    install_requires=[
        "PySide6>=6.5.0",
        "SQLAlchemy>=2.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "pyqtgraph>=0.13.0",
        "yfinance>=0.2.18",
    ],
    entry_points={
        "console_scripts": [
            "portfolio-manager=main:main",
        ],
    },
)