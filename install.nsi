!include "MUI2.nsh"

; Define the name of the installer
OutFile "FreeScribeInstaller.exe"

; Define the default installation directory to AppData
InstallDir "$APPDATA\FreeScribe"

; Define the name of the installer
Name "FreeScribe"

; Define the version of the installer
VIProductVersion "0.0.0.1"
VIAddVersionKey "ProductName" "FreeScribe"
VIAddVersionKey "FileVersion" "0.0.0.1"
VIAddVersionKey "LegalCopyright" "Copyright (c) 2023-2024 Braedon Hendy"
VIAddVersionKey "FileDescription" "FreeScribe Installer"

; Define the logo image
!define MUI_ICON ./assets/logo.ico

; Define the section of the installer
Section "MainSection" SEC01
    ; Set output path to the installation directory
    SetOutPath "$INSTDIR"

    ; Add files to the installer
    File /r "dist\*"

    ; Create a start menu shortcut
    CreateDirectory "$SMPROGRAMS\FreeScribe"
    CreateShortcut "$SMPROGRAMS\FreeScribe\FreeScribe.lnk" "$INSTDIR\freescribe-client.exe"

    ; Create an uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

; Define the uninstaller section
Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\*"

    ; Remove the installation directory
    RMDir "$INSTDIR"

    ; Remove the start menu shortcut
    Delete "$SMPROGRAMS\FreeScribe\FreeScribe.lnk"
    RMDir "$SMPROGRAMS\FreeScribe"

    ; Remove the uninstaller entry from the Control Panel
    Delete "$INSTDIR\Uninstall.exe"
SectionEnd

; Define the installer pages
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\freescribe-client.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Run App now"
!define MUI_FINISHPAGE_RUN_NOTCHECKED
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE English


; Define the uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
