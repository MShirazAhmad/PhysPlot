# Install or update PhysPlot on Windows.
#
#   irm https://raw.githubusercontent.com/MShirazAhmad/PhysPlot/indevelopment/scripts/install_windows.ps1 | iex
#
# Creates %LOCALAPPDATA%\PhysPlot (Python environment and PhysPlot source) and a
# Start menu shortcut. Close PhysPlot, then run the same command again to update.
# Uninstall: delete %LOCALAPPDATA%\PhysPlot and the PhysPlot Start menu shortcut.
#
# Optional environment variables:
#   PHYSPLOT_REF      branch or tag to install (default: indevelopment)
#   PHYSPLOT_HOME     install folder (default: %LOCALAPPDATA%\PhysPlot)
#   PHYSPLOT_SOURCE   install from this local checkout instead of downloading
#
# Works in Windows PowerShell 5.1 and PowerShell 7. Everything runs inside a
# script block so `irm | iex` never closes the caller's window on an error.

& {
    $ErrorActionPreference = 'Stop'
    $ProgressPreference = 'SilentlyContinue'  # much faster downloads in PowerShell 5.1
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

    $repo = 'MShirazAhmad/PhysPlot'
    $ref = if ($env:PHYSPLOT_REF) { $env:PHYSPLOT_REF } else { 'indevelopment' }
    $installDir = if ($env:PHYSPLOT_HOME) { $env:PHYSPLOT_HOME } else { Join-Path $env:LOCALAPPDATA 'PhysPlot' }
    $venv = Join-Path $installDir 'venv'
    $venvPython = Join-Path $venv 'Scripts\python.exe'
    $venvPythonw = Join-Path $venv 'Scripts\pythonw.exe'
    # PhysPlot's Figure Editor (FigureForge) supports Python 3.11-3.13.
    $versionCheck = 'import sys; print(sys.executable if (3, 11) <= sys.version_info[:2] <= (3, 13) else "")'

    function Say([string]$message) { Write-Host "==> $message" -ForegroundColor Cyan }

    # Run a native command; stop on a non-zero exit code. Native stderr (pip
    # notices) must not become a terminating error in PowerShell 5.1.
    function Invoke-Checked([string]$what, [scriptblock]$command) {
        $previous = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try { & $command } finally { $ErrorActionPreference = $previous }
        if ($LASTEXITCODE -ne 0) { throw "$what failed (exit code $LASTEXITCODE)." }
    }

    # Return the full path of a Python 3.11-3.13, or $null.
    function Find-Python {
        $previous = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try {
            if (Get-Command py -ErrorAction SilentlyContinue) {
                foreach ($version in '3.12', '3.13', '3.11') {
                    $path = & py "-$version" -c $versionCheck 2>$null
                    if ($LASTEXITCODE -eq 0 -and $path) { return ([string]$path).Trim() }
                }
            }
            foreach ($name in 'python', 'python3') {
                $command = Get-Command $name -ErrorAction SilentlyContinue
                # Skip the Microsoft Store alias that opens the Store instead of running Python.
                if ($command -and $command.Source -notlike '*\WindowsApps\*') {
                    $path = & $command.Source -c $versionCheck 2>$null
                    if ($LASTEXITCODE -eq 0 -and $path) { return ([string]$path).Trim() }
                }
            }
            $candidate = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
            if (Test-Path $candidate) { return $candidate }
            return $null
        } finally { $ErrorActionPreference = $previous }
    }

    Say 'Looking for Python 3.11-3.13'
    $python = Find-Python
    if (-not $python) {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Say 'Installing Python 3.12 with winget'
            Invoke-Checked 'Installing Python' { winget install --exact --id Python.Python.3.12 --scope user }
            $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
            $python = Find-Python
        }
        if (-not $python) {
            throw 'Python 3.11-3.13 is required. Install Python 3.12 from https://www.python.org/downloads/windows/ (tick "Add python.exe to PATH"), then run this command again.'
        }
    }
    Say "Using $python"

    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
    if ($env:PHYSPLOT_SOURCE) {
        $source = (Resolve-Path $env:PHYSPLOT_SOURCE).Path
        Say "Installing from local source $source"
    } else {
        $source = Join-Path $installDir 'src'
        Say "Downloading PhysPlot ($ref) from GitHub"
        $tmp = Join-Path ([IO.Path]::GetTempPath()) ('physplot-' + [guid]::NewGuid())
        New-Item -ItemType Directory -Path $tmp | Out-Null
        try {
            $zip = Join-Path $tmp 'physplot.zip'
            Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/$repo/archive/$ref.zip" -OutFile $zip
            Expand-Archive -Path $zip -DestinationPath $tmp
            $extracted = Get-ChildItem -Path $tmp -Directory | Where-Object { $_.Name -like 'PhysPlot-*' } | Select-Object -First 1
            if (-not $extracted) { throw "The download from GitHub did not contain PhysPlot ($ref)." }
            if (Test-Path $source) {
                try { Remove-Item -Recurse -Force $source }
                catch { throw "Could not replace $source. Close PhysPlot and run the command again." }
            }
            Move-Item -Path $extracted.FullName -Destination $source
        } finally {
            Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
        }
    }

    $reuse = $false
    if (Test-Path $venvPython) {
        $previous = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $found = & $venvPython -c $versionCheck 2>$null
        $reuse = ($LASTEXITCODE -eq 0) -and [bool]$found
        $ErrorActionPreference = $previous
    }
    if ($reuse) {
        Say "Updating the PhysPlot environment in $venv"
    } else {
        Say "Creating the PhysPlot environment in $venv"
        if (Test-Path $venv) { Remove-Item -Recurse -Force $venv }
        Invoke-Checked 'Creating the Python environment' { & $python -m venv $venv }
    }
    Say 'Installing PhysPlot and its dependencies (about 1 GB the first time; this can take a few minutes)'
    Invoke-Checked 'Updating pip' { & $venvPython -m pip install --quiet --upgrade pip }
    # Editable install, so the bundled config\ folder (transformations, loaders,
    # templates) stays next to the code where PhysPlot looks for it.
    Invoke-Checked 'Installing PhysPlot' { & $venvPython -m pip install --quiet --upgrade -e $source }
    Invoke-Checked 'Checking the installation' { & $venvPython -c 'import physplot, physplot_gui' }

    # The install is complete here; a shortcut problem is only a warning.
    $shortcutPath = ''
    try {
        $shortcutPath = Join-Path ([Environment]::GetFolderPath('Programs')) 'PhysPlot.lnk'
        Say "Creating the Start menu shortcut $shortcutPath"
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $venvPythonw
        $shortcut.Arguments = '-m physplot_gui'
        $shortcut.WorkingDirectory = [Environment]::GetFolderPath('MyDocuments')
        $shortcut.Description = 'PhysPlot'
        $icon = Join-Path $source 'installer\icons\PhysPlot.ico'
        if (Test-Path $icon) { $shortcut.IconLocation = $icon }
        $shortcut.Save()
    } catch {
        Write-Warning "Could not create the Start menu shortcut ($($_.Exception.Message)). Start PhysPlot with: & '$venvPythonw' -m physplot_gui"
    }

    Say 'PhysPlot is installed.'
    Write-Host ''
    Write-Host "  Open it:        Start menu > PhysPlot"
    Write-Host "  Terminal:       & '$venv\Scripts\physplot-gui.exe'"
    Write-Host "  Command line:   & '$venv\Scripts\physplot.exe' run-workflow Sequence.py --input data.csv --output out"
    Write-Host "  Sample data:    $source\test_data"
    Write-Host '  Update:         close PhysPlot, then run the same install command again'
    $uninstall = "Remove-Item -Recurse -Force '$installDir'"
    if ($shortcutPath -and (Test-Path $shortcutPath)) { $uninstall += "; Remove-Item '$shortcutPath'" }
    Write-Host "  Uninstall:      $uninstall"
    Write-Host ''
}
