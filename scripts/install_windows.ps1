# Install or update PhysPlot on Windows.
#
#   irm https://raw.githubusercontent.com/MShirazAhmad/PhysPlot/main/scripts/install_windows.ps1 | iex
#
# Needs nothing installed first: without Python 3.12-3.14 it installs Python 3.12 for
# this user (with winget, or from python.org). Creates %LOCALAPPDATA%\PhysPlot (Python
# environment and PhysPlot source) and a Start menu shortcut. Close PhysPlot, then run
# the same command again to update.
# Uninstall: delete %LOCALAPPDATA%\PhysPlot and the PhysPlot Start menu shortcut.
#
# Optional environment variables:
#   PHYSPLOT_REF      branch or tag to install (default: main, the stable branch)
#   PHYSPLOT_HOME     install folder (default: %LOCALAPPDATA%\PhysPlot)
#   PHYSPLOT_SOURCE   install from this local checkout instead of downloading
#   PHYSPLOT_RELAUNCH set to 1 to open PhysPlot when done (used by Help > Check for Updates)
#
# Works in Windows PowerShell 5.1 and PowerShell 7. Everything runs inside a
# script block so `irm | iex` never closes the caller's window on an error.

& {
    $ErrorActionPreference = 'Stop'
    $ProgressPreference = 'SilentlyContinue'  # much faster downloads in PowerShell 5.1
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

    $repo = 'MShirazAhmad/PhysPlot'
    $ref = if ($env:PHYSPLOT_REF) { $env:PHYSPLOT_REF } else { 'main' }
    $installDir = if ($env:PHYSPLOT_HOME) { $env:PHYSPLOT_HOME } else { Join-Path $env:LOCALAPPDATA 'PhysPlot' }
    $venv = Join-Path $installDir 'venv'
    $venvPython = Join-Path $venv 'Scripts\python.exe'
    $venvPythonw = Join-Path $venv 'Scripts\pythonw.exe'
    # PhysPlot needs Python 3.12-3.14 (numpy and scipy need 3.12+; tested up to 3.14).
    # On Windows on ARM it uses the x64 build of Python (run by Windows' built-in
    # emulation), where every dependency has a ready-made wheel. sysconfig names the build
    # (platform.machine() gives the CPU, ARM64, even in x64 Python 3.12). The check has no double quotes: Windows PowerShell 5.1
    # drops them from native-command arguments.
    $arm64 = ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') -or ($env:PROCESSOR_ARCHITEW6432 -eq 'ARM64')
    $versionCheck = 'import sys, sysconfig; print(sys.executable) if (3, 12) <= sys.version_info[:2] <= (3, 14) and sysconfig.get_platform() != ''win-arm64'' else sys.exit(1)'

    function Say([string]$message) { Write-Host "==> $message" -ForegroundColor Cyan }

    # Run a native command; stop on a non-zero exit code. Native stderr (pip
    # notices) must not become a terminating error in PowerShell 5.1.
    function Invoke-Checked([string]$what, [scriptblock]$command) {
        $previous = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try { & $command } finally { $ErrorActionPreference = $previous }
        if ($LASTEXITCODE -ne 0) { throw "$what failed (exit code $LASTEXITCODE)." }
    }

    # Return the full path of a Python 3.12-3.14, or $null.
    function Find-Python {
        $previous = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try {
            if (Get-Command py -ErrorAction SilentlyContinue) {
                # "-3.12" selects the x64 or x86-64 build; ARM64 builds are tagged "-3.12-arm64".
                foreach ($version in '3.12', '3.13', '3.14') {
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
            foreach ($folder in 'Python312', 'Python312-x64') {
                $candidate = Join-Path $env:LOCALAPPDATA "Programs\Python\$folder\python.exe"
                if (Test-Path $candidate) { return $candidate }
            }
            return $null
        } finally { $ErrorActionPreference = $previous }
    }

    function Update-Path {
        $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
    }

    # Both ways install Python for this user only, so no administrator rights are needed.
    Say 'Looking for Python 3.12-3.14'
    $python = Find-Python
    if (-not $python) {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Say 'Installing Python 3.12 with winget'
            # winget's exit code is not reliable here (an already installed Python gives
            # "no applicable upgrade"), so look for Python again instead of checking it.
            # The agreement flags stop a fresh Windows from asking about the winget source.
            $previous = $ErrorActionPreference
            $ErrorActionPreference = 'Continue'
            $wingetArgs = @('install', '--exact', '--id', 'Python.Python.3.12', '--scope', 'user', '--source', 'winget',
                '--accept-source-agreements', '--accept-package-agreements')
            if ($arm64) { $wingetArgs += @('--architecture', 'x64') }
            try { winget @wingetArgs } finally { $ErrorActionPreference = $previous }
            Update-Path
            $python = Find-Python
        }
        if (-not $python) {
            # No winget (or it failed): the python.org installer. The x64 build, also on
            # Windows on ARM (see above).
            Say 'Downloading Python 3.12 from python.org'
            $setup = Join-Path ([IO.Path]::GetTempPath()) 'python-3.12.10-amd64.exe'
            try {
                Invoke-WebRequest -UseBasicParsing -Uri 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe' -OutFile $setup
                Say 'Installing Python 3.12'
                $setupArgs = @('/quiet', 'InstallAllUsers=0', 'InstallLauncherAllUsers=0', 'PrependPath=1', 'Include_test=0')
                $process = Start-Process -FilePath $setup -ArgumentList $setupArgs -Wait -PassThru
                if ($process.ExitCode -ne 0) { Write-Warning "The Python installer stopped with exit code $($process.ExitCode)." }
            } catch {
                Write-Warning "Could not install Python from python.org ($($_.Exception.Message))."
            } finally {
                Remove-Item -Force $setup -ErrorAction SilentlyContinue
            }
            Update-Path
            $python = Find-Python
        }
        if (-not $python) {
            $build = if ($arm64) { 'the "Windows installer (64-bit)" (x64, not ARM64) of Python 3.12' } else { 'Python 3.12' }
            throw "Python 3.12-3.14 is required. Install $build from https://www.python.org/downloads/windows/ (tick `"Add python.exe to PATH`"), then run this command again."
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
            # Not Expand-Archive: in PowerShell 5.1 it is slow and shows a progress bar
            # whatever $ProgressPreference says.
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            [IO.Compression.ZipFile]::ExtractToDirectory($zip, $tmp)
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

    # Right-click "Open with > PhysPlot" for data files (built-in loaders plus every loader
    # plugin's FILE_EXTENSIONS). Per-user keys only; existing default apps are left alone.
    $progId = 'PhysPlot.DataFile'
    try {
        Say 'Registering PhysPlot in the Open with menu for data files'
        $classes = 'HKCU:\Software\Classes'
        $command = "`"$venvPythonw`" -m physplot_gui `"%1`""
        New-Item -Path "$classes\$progId\shell\open\command" -Force | Out-Null
        Set-ItemProperty -Path "$classes\$progId" -Name '(default)' -Value 'PhysPlot data file'
        Set-ItemProperty -Path "$classes\$progId" -Name 'FriendlyTypeName' -Value 'PhysPlot data file'
        Set-ItemProperty -Path "$classes\$progId\shell\open\command" -Name '(default)' -Value $command
        $icon = Join-Path $source 'installer\icons\PhysPlot.ico'
        if (Test-Path $icon) {
            New-Item -Path "$classes\$progId\DefaultIcon" -Force | Out-Null
            Set-ItemProperty -Path "$classes\$progId\DefaultIcon" -Name '(default)' -Value $icon
        }
        $extensions = & $venvPython -c 'from physplot_gui.app.main_window import data_file_extensions; print(*data_file_extensions())'
        foreach ($ext in ("$extensions".Trim() -split ' ')) {
            if (-not $ext) { continue }
            $key = "$classes\$ext\OpenWithProgids"
            New-Item -Path $key -Force | Out-Null
            New-ItemProperty -Path $key -Name $progId -PropertyType String -Value '' -Force | Out-Null
        }
    } catch {
        Write-Warning "Could not register PhysPlot for data files ($($_.Exception.Message))."
    }

    # Record what was installed, for Help > Check for Updates.
    try {
        $commit = $null
        if (-not $env:PHYSPLOT_SOURCE) {
            $commit = (Invoke-RestMethod -UseBasicParsing -Uri "https://api.github.com/repos/$repo/commits/$ref" -Headers @{ 'User-Agent' = 'PhysPlot-installer' }).sha
        }
        [ordered]@{ ref = $ref; commit = $commit; local_source = [bool]$env:PHYSPLOT_SOURCE; installed_at = (Get-Date -Format s) } |
            ConvertTo-Json | Set-Content -Encoding UTF8 -Path (Join-Path $installDir 'install.json')
    } catch {
        Write-Warning "Could not record the installed version ($($_.Exception.Message))."
    }

    Say 'PhysPlot is installed.'
    Write-Host ''
    Write-Host "  Open it:        Start menu > PhysPlot"
    Write-Host "  Data files:     right-click a data file > Open with > PhysPlot"
    Write-Host "  Terminal:       & '$venv\Scripts\physplot-gui.exe'"
    Write-Host "  Command line:   & '$venv\Scripts\physplot.exe' run-workflow Sequence.py --input data.csv --output out"
    Write-Host "  Sample data:    $source\test_data"
    Write-Host '  Update:         close PhysPlot, then run the same install command again'
    $uninstall = "Remove-Item -Recurse -Force '$installDir'"
    if ($shortcutPath -and (Test-Path $shortcutPath)) { $uninstall += "; Remove-Item '$shortcutPath'" }
    $uninstall += "; Remove-Item -Recurse 'HKCU:\Software\Classes\$progId'"
    Write-Host "  Uninstall:      $uninstall"
    Write-Host ''
    if ($env:PHYSPLOT_RELAUNCH -eq '1') {
        Say 'Reopening PhysPlot'
        Start-Process -FilePath $venvPythonw -ArgumentList '-m', 'physplot_gui' -WorkingDirectory ([Environment]::GetFolderPath('MyDocuments'))
    }
}
