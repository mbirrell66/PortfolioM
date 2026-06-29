@echo off
setlocal

echo ============================================================
echo  Portfolio Manager - Build Script
echo ============================================================
echo.

cd /d "%~dp0portfolio_manager"
if errorlevel 1 (
    echo ERROR: Could not change to portfolio_manager directory.
    pause
    exit /b 1
)

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found on PATH.
    pause
    exit /b 1
)

:: Install / upgrade PyInstaller
echo [1/3] Installing PyInstaller...
pip install --quiet --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: pip install pyinstaller failed.
    pause
    exit /b 1
)

:: Clean previous build artefacts
echo [2/3] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

:: Run PyInstaller
echo [3/3] Building executable...
pyinstaller PortfolioManager.spec
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller failed - see output above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Build complete!
echo  Executable: dist\PortfolioManager\PortfolioManager.exe
echo ============================================================
echo.
pause
