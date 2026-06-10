@echo off
echo Building Portfolio Manager executable with PyInstaller...
echo.

REM Change to the portfolio_manager directory
cd portfolio_manager

REM Run PyInstaller to create a single executable
pyinstaller --onefile --windowed --name="PortfolioManager" --icon="portfolio_manager.ico" main.py

echo.
echo Build complete! The executable is in the 'dist' folder.
echo.
echo To run the application:
echo   dist\PortfolioManager.exe