# Clean-room build for Portfolio Manager
# Builds the onedir bundle from an isolated venv containing ONLY the app's
# runtime dependencies, so PyInstaller can't pick up unrelated global
# packages (torch, transformers, etc. — the cause of the 1.6GB installer).
#
# Usage:  .\build_clean.ps1            (reuses existing build venv)
#         .\build_clean.ps1 -Rebuild   (recreates the venv from scratch)

param(
    [switch]$Rebuild
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$VenvDir  = Join-Path $RepoRoot ".venv-build"
$AppDir   = Join-Path $RepoRoot "portfolio_manager"

# 1. Create / recreate the isolated build venv
if ($Rebuild -and (Test-Path $VenvDir)) {
    Write-Host "Removing existing build venv..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $VenvDir
}
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating build venv at $VenvDir ..." -ForegroundColor Cyan
    python -m venv $VenvDir
}

$Python = Join-Path $VenvDir "Scripts\python.exe"

# 2. Install runtime deps + PyInstaller (nothing else)
Write-Host "Installing build requirements..." -ForegroundColor Cyan
& $Python -m pip install --upgrade pip --quiet
& $Python -m pip install -r (Join-Path $RepoRoot "requirements-build.txt") --quiet

# 3. Remove any stale bundle so a failed build can't masquerade as success
$Bundle = Join-Path $AppDir "dist\PortfolioManager"
if (Test-Path $Bundle) {
    Write-Host "Removing stale bundle..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $Bundle
}

# 4. Build the onedir bundle the installer consumes
Write-Host "Running PyInstaller..." -ForegroundColor Cyan
Push-Location $AppDir
try {
    & $Python -m PyInstaller PortfolioManager.spec --noconfirm --clean
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyInstaller failed (exit code $LASTEXITCODE) - see errors above" -ForegroundColor Red
        exit 1
    }
} finally {
    Pop-Location
}

# 5. Report bundle size
if (Test-Path $Bundle) {
    $SizeMB = [math]::Round((Get-ChildItem $Bundle -Recurse | Measure-Object Length -Sum).Sum / 1MB, 1)
    Write-Host ""
    Write-Host "Build complete: $Bundle" -ForegroundColor Green
    Write-Host "Bundle size: $SizeMB MB (was ~5300 MB from the global environment)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next step: compile the installer with Inno Setup (installer\PortfolioManager.iss)"
} else {
    Write-Host "Build failed - bundle not found at $Bundle" -ForegroundColor Red
    exit 1
}
