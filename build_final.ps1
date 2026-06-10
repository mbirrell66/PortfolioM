# Build script for Portfolio Manager
# This script builds a standalone executable with PyInstaller

# Change to the correct directory
Set-Location "D:\Projects\PortfolioM\portfolio_manager"

# Remove previous build artifacts
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

# Build the executable with PyInstaller
pyinstaller --onefile --windowed --name="PortfolioManager" --add-data="portfolio_manager.ico;." --hidden-import="portfolio_manager.gui.main_window" --hidden-import="portfolio_manager.gui.tax_management_tab" --hidden-import="portfolio_manager.gui.tax_event_dialog" --hidden-import="portfolio_manager.gui.capital_gains_dialog" --hidden-import="portfolio_manager.services.tax_service" --hidden-import="portfolio_manager.database.tax_models" --hidden-import="PySide6.QtWidgets" --hidden-import="PySide6.QtGui" --hidden-import="PySide6.QtCore" --hidden-import="sqlalchemy" --hidden-import="pandas" --hidden-import="numpy" --hidden-import="yfinance" "main.py"

Write-Host "Build complete! Executable is in the dist folder."