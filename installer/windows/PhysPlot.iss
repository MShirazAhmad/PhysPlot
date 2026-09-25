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
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\icons\PhysPlot.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#BuildOutput}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\config\*"; DestDir: "{userdocs}\PhysPlot\config"; Excludes: "__pycache__,*.pyc,.DS_Store,._*"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist
Source: "..\..\test_data\*"; DestDir: "{userdocs}\PhysPlot\test_data"; Excludes: ".DS_Store,._*"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist

[Dirs]
Name: "{userdocs}\PhysPlot"
Name: "{userdocs}\PhysPlot\config"
Name: "{userdocs}\PhysPlot\config\data_importers"
Name: "{userdocs}\PhysPlot\config\transformations"
Name: "{userdocs}\PhysPlot\config\fit_functions"
Name: "{userdocs}\PhysPlot\config\templates"
Name: "{userdocs}\PhysPlot\config\figureforge_fit_styles"
Name: "{userdocs}\PhysPlot\config\pipelines"
Name: "{userdocs}\PhysPlot\config\sequences"
Name: "{userdocs}\PhysPlot\config\plotter_modules"
Name: "{userdocs}\PhysPlot\config\plot_types"
Name: "{userdocs}\PhysPlot\config\protocol_modules"
Name: "{userdocs}\PhysPlot\test_data"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
