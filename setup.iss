; Inno Setup Script for creating an installer

[Setup]
; Required settings
AppName=FreeScribe
AppVersion=0.0.1
DefaultDirName={pf}\FreeScribe
DefaultGroupName=FreeScribe
OutputDir=output
OutputBaseFilename=FreeScribeInstaller
Compression=lzma
SolidCompression=yes

[Files]
; Source: is where your PyInstaller output executable is located
; Destination: where the file will be placed during installation
Source: "dist\client.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Create a shortcut for the application in the Start Menu and Desktop
Name: "{group}\FreeScribe"; Filename: "{app}\FreeScribe.exe"
Name: "{userdesktop}\FreeScribe"; Filename: "{app}\FreeScribe.exe"; Tasks: desktopicon

[Tasks]
; Option to create a desktop shortcut
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
; Run the application after install
Filename: "{app}\client.exe"; Description: "Launch My Application"; Flags: nowait postinstall skipifsilent

