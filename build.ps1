# PowerShell script to build Portfolio Manager executable
# Save this as build.ps1

# Change to the project directory
Set-Location "D:\Projects\PortfolioM"

# Navigate to portfolio_manager directory
Set-Location "portfolio_manager"

# Run PyInstaller
pyinstaller --onefile --windowed --name="PortfolioManager" main.py

Write-Host "Build complete! Check the 'dist' folder for the executable."