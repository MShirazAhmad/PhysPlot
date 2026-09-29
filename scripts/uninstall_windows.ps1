# Uninstall PhysPlot from Windows.
#
#   irm https://raw.githubusercontent.com/MShirazAhmad/PhysPlot/main/scripts/uninstall_windows.ps1 | iex
#
# Removes what scripts/install_windows.ps1 added: %LOCALAPPDATA%\PhysPlot, the Start menu
# shortcut, the "Open with" entries for data files and PhysPlot's saved settings. It also
# runs the uninstaller of the older setup program (PhysPlot-<version>-Windows-Setup.exe)
# when that is installed. Your own files in Documents\PhysPlot and Python are kept unless
# you ask for them to go:
#
#   PHYSPLOT_REMOVE_USER_FILES set to 1 to also delete Documents\PhysPlot (your modules)
#   PHYSPLOT_REMOVE_PYTHON     set to 1 to also uninstall every Python 3 and the Python
#                              Launcher (other programs that use Python stop working)
#   PHYSPLOT_HOME              install folder (default: %LOCALAPPDATA%\PhysPlot)
#
# Works in Windows PowerShell 5.1 and PowerShell 7. Everything runs inside a script block
# so `irm | iex` never closes the caller's window on an error.

& {
    $ErrorActionPreference = 'Stop'
    $installDir = if ($env:PHYSPLOT_HOME) { $env:PHYSPLOT_HOME } else { Join-Path $env:LOCALAPPDATA 'PhysPlot' }
    $progId = 'PhysPlot.DataFile'
    $classes = 'HKCU:\Software\Classes'
    $uninstallKeys = @(
        'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )
    $admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)

    function Say([string]$message) { Write-Host "==> $message" -ForegroundColor Cyan }

    function Remove-IfPresent([string]$path) {
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Recurse -Force; Say "Removed $path" }
    }

    # Entries in Settings > Apps whose name matches, without the hidden MSI parts.
    function Get-InstalledApp([string]$pattern) {
        Get-ItemProperty -Path $uninstallKeys -ErrorAction SilentlyContinue |
            Where-Object { $_.DisplayName -match $pattern -and $_.SystemComponent -ne 1 -and $_.UninstallString }
    }

    # Run an uninstaller without its windows. Returns $false when it needs admin rights.
    function Invoke-Uninstaller($app, [string]$silentArgs) {
        if ($app.PSPath -like '*HKEY_LOCAL_MACHINE*' -and -not $admin) {
            Write-Warning "$($app.DisplayName) was installed for all users. Remove it from Settings > Apps > Installed apps, or run this command in PowerShell as administrator."
            return $false
        }
        Say "Uninstalling $($app.DisplayName)"
        $line = if ($app.QuietUninstallString) { $app.QuietUninstallString } else { "$($app.UninstallString) $silentArgs" }
        if ($line -match '(?i)msiexec.*?(\{[0-9A-F-]+\})') {
            $process = Start-Process msiexec.exe -ArgumentList '/x', $Matches[1], '/qn', '/norestart' -Wait -PassThru
        } else {
            $process = Start-Process cmd.exe -ArgumentList '/c', "`"$line`"" -Wait -PassThru -WindowStyle Hidden
        }
        if ($process.ExitCode -ne 0) { Write-Warning "$($app.DisplayName): the uninstaller exited with code $($process.ExitCode)." }
        return $true
    }

    # Deleting the environment fails while PhysPlot runs from it.
    $prefix = Join-Path $installDir ''
    $running = Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -and $_.Path.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) }
    if ($running) {
        throw 'PhysPlot is still open. Close every PhysPlot window (and any PhysPlot command running in a terminal), then run this command again.'
    }

    Say 'Removing PhysPlot'
    Remove-IfPresent $installDir
    $programs = [Environment]::GetFolderPath('Programs')
    Remove-IfPresent (Join-Path $programs 'PhysPlot.lnk')

    # The older setup program (Inno Setup) has its own uninstaller and Start menu folder.
    foreach ($app in @(Get-InstalledApp '^PhysPlot\b')) {
        Invoke-Uninstaller $app '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART' | Out-Null
    }
    Remove-IfPresent (Join-Path $programs 'PhysPlot')

    Say 'Removing the Open with entries and saved settings'
    Remove-IfPresent "$classes\$progId"
    Get-ChildItem -Path $classes -ErrorAction SilentlyContinue |
        Where-Object { $_.PSChildName.StartsWith('.') } |
        ForEach-Object {
            $key = Join-Path $_.PSPath 'OpenWithProgids'
            if ((Get-ItemProperty -Path $key -ErrorAction SilentlyContinue).PSObject.Properties.Name -contains $progId) {
                Remove-ItemProperty -Path $key -Name $progId
            }
        }
    Remove-IfPresent 'HKCU:\Software\PhysLab\PhysPlot'
    if ((Test-Path 'HKCU:\Software\PhysLab') -and -not (Get-ChildItem 'HKCU:\Software\PhysLab')) {
        Remove-Item 'HKCU:\Software\PhysLab'
    }

    $documents = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'PhysPlot'
    if ($env:PHYSPLOT_REMOVE_USER_FILES -eq '1') {
        Remove-IfPresent $documents
    } elseif (Test-Path -LiteralPath $documents) {
        Say "Kept your files in $documents"
    }

    if ($env:PHYSPLOT_REMOVE_PYTHON -eq '1') {
        foreach ($app in @(Get-InstalledApp '^Python 3\.\d+')) {
            Invoke-Uninstaller $app '/uninstall /quiet' | Out-Null
        }
        foreach ($app in @(Get-InstalledApp '^Python Launcher')) {
            Invoke-Uninstaller $app '/qn' | Out-Null
        }
        Remove-IfPresent (Join-Path $env:LOCALAPPDATA 'pip')
        # The Python uninstallers leave their empty folders behind.
        $pythonDir = Join-Path $env:LOCALAPPDATA 'Programs\Python'
        foreach ($dir in @(Get-ChildItem -LiteralPath $pythonDir -Directory -ErrorAction SilentlyContinue) + @(Get-Item -LiteralPath $pythonDir -ErrorAction SilentlyContinue)) {
            if ($dir -and -not (Get-ChildItem -LiteralPath $dir.FullName -Recurse -File -ErrorAction SilentlyContinue)) {
                Remove-IfPresent $dir.FullName
            }
        }
    }

    Say 'PhysPlot is uninstalled.'
    if ($env:PHYSPLOT_REMOVE_PYTHON -ne '1') {
        Write-Host '  Python was kept. To remove it too, run:  $env:PHYSPLOT_REMOVE_PYTHON = "1"  then this command again.'
    }
}
