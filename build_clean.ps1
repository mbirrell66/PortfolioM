# Clean-room build for Portfolio Manager
# Builds the onedir bundle from an isolated venv containing ONLY the app's
# runtime dependencies, so PyInstaller can't pick up unrelated global
# packages (torch, transformers, etc. — the cause of the 1.6GB installer).
#
# Builds the app bundle AND the Inno Setup installer, taking the version from
# portfolio_manager\_version.py so nothing can drift out of step.
#
# Usage:  .\build_clean.ps1                  (reuses existing build venv)
#         .\build_clean.ps1 -Rebuild         (recreates the venv from scratch)
#         .\build_clean.ps1 -SkipInstaller   (bundle only, no installer)
#
# To cut a release: bump __version__ in portfolio_manager\_version.py, then run
# this script. Output lands in installer\Output\PortfolioManager-Setup-<ver>.exe

param(
    [switch]$Rebuild,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$VenvDir  = Join-Path $RepoRoot ".venv-build"
$AppDir   = Join-Path $RepoRoot "portfolio_manager"

# 0. Read the version from the single source of truth so the bundle, the
#    installer filename and the embedded metadata can never disagree.
$VersionFile = Join-Path $AppDir "_version.py"
$VersionText = Get-Content $VersionFile -Raw
if ($VersionText -notmatch '__version__\s*=\s*["'']([^"'']+)["'']') {
    Write-Host "Could not read __version__ from $VersionFile" -ForegroundColor Red
    exit 1
}
$Version = $Matches[1]
Write-Host "Building Portfolio Manager $Version" -ForegroundColor Cyan

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
if (-not (Test-Path $Bundle)) {
    Write-Host "Build failed - bundle not found at $Bundle" -ForegroundColor Red
    exit 1
}
$SizeMB = [math]::Round((Get-ChildItem $Bundle -Recurse | Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Host ""
Write-Host "Build complete: $Bundle" -ForegroundColor Green
Write-Host "Bundle size: $SizeMB MB (was ~5300 MB from the global environment)" -ForegroundColor Green

# 6. Compile the installer, passing the version through so the .exe filename
#    and the embedded version metadata always match _version.py
if ($SkipInstaller) {
    Write-Host ""
    Write-Host "-SkipInstaller set; stopping after the bundle." -ForegroundColor Yellow
    exit 0
}

$Iss = Join-Path $RepoRoot "installer\PortfolioManager.iss"
$Iscc = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty Source -First 1
if (-not $Iscc) {
    foreach ($candidate in @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    )) {
        if (Test-Path $candidate) { $Iscc = $candidate; break }
    }
}
if (-not $Iscc) {
    Write-Host ""
    Write-Host "Inno Setup (ISCC.exe) not found - bundle is built but no installer was made." -ForegroundColor Yellow
    Write-Host "Install Inno Setup 6 from https://jrsoftware.org/isinfo.php, then run:" -ForegroundColor Yellow
    Write-Host "  ISCC.exe /DAppVersion=$Version `"$Iss`"" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Compiling installer with Inno Setup..." -ForegroundColor Cyan
& $Iscc "/DAppVersion=$Version" $Iss
if ($LASTEXITCODE -ne 0) {
    Write-Host "Inno Setup failed (exit code $LASTEXITCODE) - see errors above" -ForegroundColor Red
    exit 1
}

$Setup = Join-Path $RepoRoot "installer\Output\PortfolioManager-Setup-$Version.exe"
if (Test-Path $Setup) {
    $SetupMB = [math]::Round((Get-Item $Setup).Length / 1MB, 1)
    Write-Host ""
    Write-Host "Release ready: $Setup ($SetupMB MB)" -ForegroundColor Green
} else {
    Write-Host "Inno Setup reported success but $Setup is missing" -ForegroundColor Red
    exit 1
}
