# Simple build script to create a standalone executable for Portfolio Manager
# Run this from the D:\Projects\PortfolioM directory

import subprocess
import os

def build_executable():
    print("Building Portfolio Manager executable...")
    
    # Change to the portfolio_manager directory where main.py is located
    os.chdir("portfolio_manager")
    
    # Create the build command
    build_command = [
        "pyinstaller",
        "--onefile",           # Create a single file executable
        "--windowed",          # No console window
        "--name=PortfolioManager",  # Executable name
        "--icon=portfolio_manager.ico",  # Icon file (if exists)
        "main.py"              # Main application file
    ]
    
    # Add additional paths for PyInstaller to find modules
    build_command.extend([
        "--add-data=database;database",
        "--add-data=gui;gui",
        "--add-data=services;services",
        "--add-data=data;data",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=sqlalchemy",
        "--hidden-import=pandas",
        "--hidden-import=numpy",
        "--hidden-import=yfinance"
    ])
    
    try:
        # Run the build command
        result = subprocess.run(build_command, capture_output=True, text=True)
        if result.returncode == 0:
            print("Build successful!")
            print("Executable is in the 'dist' folder")
        else:
            print("Build failed:")
            print(result.stderr)
    except Exception as e:
        print(f"Error during build: {e}")

if __name__ == "__main__":
    build_executable()