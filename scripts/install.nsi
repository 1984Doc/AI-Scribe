!include "MUI2.nsh"

; Define the name of the installer
OutFile "..\dist\FreeScribeInstaller.exe"

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

; Function to show message box on finish
Function .onInstSuccess
    ; Check if silent, if is silent skip message box prompt
    IfSilent +2
    MessageBox MB_OK "Installation completed successfully! Please note upon first launch start time may be slow. Please wait for the program to open!"
FunctionEnd

; Define the section of the installer
Section "MainSection" SEC01
    ; Set output path to the installation directory
    SetOutPath "$INSTDIR"

    ; Add files to the installer
    File /r "..\dist\freescribe-client\freescribe-client.exe"
    File /r "..\dist\freescribe-client\_internal"
    File /r "..\src\FreeScribe.client\markdown"

    IfFileExists "$INSTDIR\settings.txt" +7

    ; Add default settings file
    File "..\default_settings.txt"

    ; Rename default_settings.txt to settings.txt
    Rename "$INSTDIR\default_settings.txt" "$INSTDIR\settings.txt"

    ; add presets
    CreateDirectory "$INSTDIR\presets"
    SetOutPath "$INSTDIR\presets"
    File /r "..\src\FreeScribe.client\presets\*"

    SetOutPath "$INSTDIR"

    ; Create a start menu shortcut
    CreateDirectory "$SMPROGRAMS\FreeScribe"
    CreateShortcut "$SMPROGRAMS\FreeScribe\FreeScribe.lnk" "$INSTDIR\freescribe-client.exe"

    ; Create an uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "GGUF Installs" GGUF_INSTALLS
    AddSize 4493079 ; Add the size in kilobyes for the models

    CreateDirectory "$INSTDIR\models"
    SetOutPath "$INSTDIR\models"

    ; Copy the license
    File ".\assets\gemma_license.txt"

    ; install the gemma 2 q4
    inetc::get /TIMEOUT=30000 "https://huggingface.co/lmstudio-community/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf?download=true" "$INSTDIR\models\gemma-2-2b-it-Q4_K_M.gguf" /END


    ; install the gemma 2 q8
    inetc::get /TIMEOUT=30000 "https://huggingface.co/lmstudio-community/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q8_0.gguf?download=true" "$INSTDIR\models\gemma-2-2b-it-Q8_0.gguf" /END

    SetOutPath "$INSTDIR"

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
    
    ; Show message when uninstallation is complete
    MessageBox MB_OK "FreeScribe has been successfully uninstalled."
SectionEnd

; Define the installer pages
!insertmacro MUI_PAGE_LICENSE ".\assets\License.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\freescribe-client.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Run App now"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE English

; Define the uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES