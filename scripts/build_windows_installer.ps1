param(
    [string]$Python = "python",
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Get-InnoSetupCompiler {
    $command = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
        "${env:LOCALAPPDATA}\Programs\Inno Setup 6\ISCC.exe"
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    return $null
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & $Python -m venv .venv
}

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -e ".[dev]"

Get-ChildItem -Path . -Recurse -Force -Filter "._*" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Force -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

if (Test-Path "build") {
    Remove-Item "build" -Recurse -Force
}
if (Test-Path "dist\PhysPlot") {
    Remove-Item "dist\PhysPlot" -Recurse -Force
}

& $venvPython -m PyInstaller --clean --noconfirm PhysPlot.spec

$appExe = Join-Path $repoRoot "dist\PhysPlot\PhysPlot.exe"
if (-not (Test-Path $appExe)) {
    throw "Expected PyInstaller output was not created: $appExe"
}

$version = (& $venvPython -c "import importlib.metadata; print(importlib.metadata.version('python-physplot'))").Trim()
$env:PHYSPLOT_VERSION = $version

if ($SkipInstaller) {
    Write-Host "Built portable Windows app: dist\PhysPlot\PhysPlot.exe"
    exit 0
}

$iscc = Get-InnoSetupCompiler
if (-not $iscc) {
    Write-Warning "Inno Setup 6 was not found. Install it from https://jrsoftware.org/isinfo.php or rerun with -SkipInstaller."
    Write-Host "Built portable Windows app: dist\PhysPlot\PhysPlot.exe"
    exit 0
}

if (-not (Test-Path "dist\installer")) {
    New-Item -ItemType Directory -Path "dist\installer" | Out-Null
}

& $iscc "installer\windows\PhysPlot.iss"

$installer = Join-Path $repoRoot "dist\installer\PhysPlot-$version-Windows-Setup.exe"
if (-not (Test-Path $installer)) {
    throw "Expected installer was not created: $installer"
}

Write-Host "Built portable Windows app: dist\PhysPlot\PhysPlot.exe"
Write-Host "Built standalone installer: dist\installer\PhysPlot-$version-Windows-Setup.exe"
