; Inno Setup script for the Windows PhysPlot installer.
; Build with scripts\build_windows_installer.ps1 from a Windows checkout.

#define MyAppName "PhysPlot"
#define MyAppPublisher "M. Shiraz Ahmad"
#define MyAppURL "https://github.com/MShirazAhmad/PhysPlot"
#define MyAppExeName "PhysPlot.exe"
#define MyAppVersion GetEnv("PHYSPLOT_VERSION")
#if MyAppVersion == ""
  #define MyAppVersion "1.0.0"
#endif
#define BuildOutput "..\..\dist\PhysPlot"

[Setup]
AppId={{7B3A6BC4-A1F4-4E6A-A165-938A63975929}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\..\dist\installer
OutputBaseFilename=PhysPlot-{#MyAppVersion}-Windows-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
SetupLogging=yes
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#BuildOutput}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\fileloader\*"; DestDir: "{userdocs}\PhysPlot\fileloader"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist
Source: "..\..\functions\*"; DestDir: "{userdocs}\PhysPlot\functions"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist
Source: "..\..\curvefitting\*"; DestDir: "{userdocs}\PhysPlot\curvefitting"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist
Source: "..\..\test_data\*"; DestDir: "{userdocs}\PhysPlot\test_data"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist

[Dirs]
Name: "{userdocs}\PhysPlot"
Name: "{userdocs}\PhysPlot\fileloader"
Name: "{userdocs}\PhysPlot\functions"
Name: "{userdocs}\PhysPlot\curvefitting"
Name: "{userdocs}\PhysPlot\test_data"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
