# PowerShell script to build Portfolio Manager executable
param(
    [string]$ProjectPath = "D:\Projects\PortfolioM\portfolio_manager"
)

# Change to the project directory
Set-Location $ProjectPath

# Clean previous builds
Write-Host "Cleaning previous build artifacts..."
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

# Check if main.py exists
if (-not (Test-Path "main.py")) {
    Write-Error "main.py not found in $ProjectPath"
    exit 1
}

Write-Host "Building executable with PyInstaller..."
try {
    # Build with PyInstaller using the spec file
    pyinstaller PortfolioManager.spec
    
    # Check if the build succeeded
    if (Test-Path "dist\PortfolioManager.exe") {
        Write-Host "SUCCESS: PortfolioManager.exe created in dist folder"
        Get-ChildItem -Path "dist" -File
    } else {
        Write-Host "ERROR: PortfolioManager.exe was not created"
        if (Test-Path "build") {
            Write-Host "Build files created in build folder:"
            Get-ChildItem -Path "build" -Recurse -File
        }
    }
} catch {
    Write-Error "Build failed with error: $($_.Exception.Message)"
}