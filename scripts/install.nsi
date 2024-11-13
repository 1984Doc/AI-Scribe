!include "MUI2.nsh"
!include "LogicLib.nsh"

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

; Variables for checkboxes
Var /GLOBAL CPU_CHECKBOX
Var /GLOBAL NVIDIA_CHECKBOX
Var /GLOBAL SELECTED_OPTION

; Function to create a custom page with CPU/NVIDIA options
Function ARCHITECHTURE_SELECT
    nsDialogs::Create 1018
    Pop $0

    ${If} $0 == error
        Abort
    ${EndIf}

    ; Text for selection instruction
    ${NSD_CreateLabel} 0 0 100% 12u "Select an installation option (only one):"
    Pop $0

    ; Checkbox for CPU
    ${NSD_CreateCheckbox} 10 15u 100% 10u "CPU"
    Pop $CPU_CHECKBOX

    ; Checkbox for NVIDIA
    ${NSD_CreateCheckbox} 10 30u 100% 10u "NVIDIA"
    Pop $NVIDIA_CHECKBOX

    ; Register event handlers for mutually exclusive behavior
    ${NSD_OnClick} $CPU_CHECKBOX OnCheckboxClick
    ${NSD_OnClick} $NVIDIA_CHECKBOX OnCheckboxClick

    nsDialogs::Show
FunctionEnd

; Callback function to ensure only one checkbox is selected
Function OnCheckboxClick
    ${If} $0 == $CPU_CHECKBOX
        ${NSD_SetState} $NVIDIA_CHECKBOX ${BST_UNCHECKED}
        StrCpy $SELECTED_OPTION "CPU"
    ${ElseIf} $0 == $NVIDIA_CHECKBOX
        ${NSD_SetState} $CPU_CHECKBOX ${BST_UNCHECKED}
        StrCpy $SELECTED_OPTION "NVIDIA"
    ${EndIf}
FunctionEnd

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

    ${If} $SELECTED_OPTION == "CPU"
        ; Add files to the installer
        File /r "..\dist\freescribe-client-cpu\freescribe-client-cpu.exe"
        File /r "..\dist\freescribe-client-cpu\_internal"
    ${EndIf}

    ${If} $SELECTED_OPTION == "NVIDIA"
        ; Add files to the installer
        File /r "..\dist\freescribe-client-nvidia\freescribe-client-nvidia.exe"
        File /r "..\dist\freescribe-client-nvidia\_internal"
    ${EndIf}

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
Page Custom ARCHITECHTURE_SELECT
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\freescribe-client.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Run App now"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE English

; Define the uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
