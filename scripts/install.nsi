!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

; Define the name of the installer
OutFile "..\dist\FreeScribeInstaller.exe"

; Define the default installation directory to AppData
InstallDir "$PROGRAMFILES\FreeScribe"

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
Var /GLOBAL CPU_RADIO
Var /GLOBAL NVIDIA_RADIO
Var /GLOBAL SELECTED_OPTION
Var /GLOBAL REMOVE_CONFIG_CHECKBOX
Var /GLOBAL REMOVE_CONFIG

Function Check_For_Old_Version_In_App_Data
    ; Check if the old version exists in AppData
    IfFileExists "$APPDATA\FreeScribe\freescribe-client.exe" 0 OldVersionDoesNotExist
        ; Open Dialog to ask user if they want to uninstall the old version
        MessageBox MB_YESNO|MB_ICONQUESTION "An old version of FreeScribe has been detected. Would you like to uninstall it?" IDYES UninstallOldVersion IDNO OldVersionDoesNotExist
        UninstallOldVersion:
            ; Remove the contents/folders of the old version
            RMDir /r "$APPDATA\FreeScribe\presets"
            RMDir /r "$APPDATA\FreeScribe\_internal"
            RMDir /r "$APPDATA\FreeScribe\models"

            ; Remove the old version executable
            Delete "$APPDATA\FreeScribe\freescribe-client.exe"

            ; Remove the uninstaller entry from the Control Panel
            Delete "$APPDATA\FreeScribe\uninstall.exe"

            ; Remove the start menu shortcut
            Delete "$SMPROGRAMS\FreeScribe\FreeScribe.lnk"
            RMDir "$SMPROGRAMS\FreeScribe"

            ; Show message when uninstallation is complete
            MessageBox MB_OK "FreeScribe has been successfully uninstalled."
    OldVersionDoesNotExist:
FunctionEnd


; Function to create a custom page with CPU/NVIDIA options
Function ARCHITECHTURE_SELECT
    Call Check_For_Old_Version_In_App_Data
    !insertmacro MUI_HEADER_TEXT "Architecture Selection" "Choose your preferred installation architecture based on your hardware"

    nsDialogs::Create 1018
    Pop $0

    ${If} $0 == error
        Abort
    ${EndIf}

    ; Main instruction text for architecture selection
    ${NSD_CreateLabel} 0 0 100% 12u "Choose your preferred installation architecture based on your hardware:"
    Pop $0

    ; Radio button for CPU
    ${NSD_CreateRadioButton} 10 15u 100% 10u "CPU"
    Pop $CPU_RADIO
    ${NSD_Check} $CPU_RADIO
    StrCpy $SELECTED_OPTION "CPU"

    ; CPU explanation text (grey with padding)
    ${NSD_CreateLabel} 20 25u 100% 20u "Recommended for most users. Runs on any modern processor and provides good performance for general use."
    Pop $0
    SetCtlColors $0 808080 transparent

    ; Radio button for NVIDIA
    ${NSD_CreateRadioButton} 10 55u 100% 10u "NVIDIA"
    Pop $NVIDIA_RADIO

    ; NVIDIA explanation text (grey with padding)
    ${NSD_CreateLabel} 20 65u 100% 30u "Choose this option if you have an NVIDIA GPU. Provides accelerated performance. Only select if you have a Nvidia GPU installed."
    Pop $0
    SetCtlColors $0 808080 transparent

    ; Bottom padding (10u of space)
    ${NSD_CreateLabel} 0 95u 100% 10u ""
    Pop $0

    ${NSD_OnClick} $CPU_RADIO OnRadioClick
    ${NSD_OnClick} $NVIDIA_RADIO OnRadioClick

    nsDialogs::Show
FunctionEnd

; Callback function for radio button clicks
Function OnRadioClick
    Pop $0 ; Get the handle of the clicked control

    ${If} $0 == $CPU_RADIO
        StrCpy $SELECTED_OPTION "CPU"
    ${ElseIf} $0 == $NVIDIA_RADIO
        StrCpy $SELECTED_OPTION "NVIDIA"
    ${EndIf}
FunctionEnd

; Function to show message box on finish
Function .onInstSuccess
    ; Check if silent, if is silent skip message box prompt
    IfSilent +2
    MessageBox MB_OK "Installation completed successfully! Please note upon first launch start time may be slow. Please wait for the program to open!"
FunctionEnd

Function un.onInit
    CheckIfFreeScribeIsRunning:
    nsExec::ExecToStack 'cmd /c tasklist /FI "IMAGENAME eq freescribe-client.exe" /NH | find /I "freescribe-client.exe" > nul'
    Pop $0 ; Return value

    ; Check if the process is running
    ${If} $0 == 0
        MessageBox MB_RETRYCANCEL "FreeScribe is currently running. Please close the application and try again." IDRETRY CheckIfFreeScribeIsRunning IDCANCEL abort
        abort:
            Abort
    ${EndIf}
FunctionEnd
; Checks on installer start
Function .onInit
    CheckIfFreeScribeIsRunning:
    nsExec::ExecToStack 'cmd /c tasklist /FI "IMAGENAME eq freescribe-client.exe" /NH | find /I "freescribe-client.exe" > nul'
    Pop $0 ; Return value

    ; Check if the process is running
    ${If} $0 == 0
        MessageBox MB_RETRYCANCEL "FreeScribe is currently running. Please close the application and try again." IDRETRY CheckIfFreeScribeIsRunning IDCANCEL abort
        abort:
            Abort
    ${EndIf}

    IfSilent SILENT_MODE NOT_SILENT_MODE

    SILENT_MODE:
        ${GetParameters} $R0
        ; Check for custom parameters
        ${GetOptions} $R0 "/ARCH=" $R1
        ${If} $R1 != ""
            StrCpy $SELECTED_OPTION $R1
        ${EndIf}
        
    NOT_SILENT_MODE:
FunctionEnd

Function CleanUninstall
    ; Remove the contents/folders of the old version
    RMDir /r "$INSTDIR\presets"
    RMDir /r "$INSTDIR\_internal"

    ; Remove the old version executable
    Delete "$INSTDIR\freescribe-client.exe"

    ; Remove the uninstaller entry from the Control Panel
    Delete "$INSTDIR\uninstall.exe"

    ; Remove the start menu shortcut
    Delete "$SMPROGRAMS\FreeScribe\FreeScribe.lnk"
    RMDir "$SMPROGRAMS\FreeScribe"
FunctionEnd

Function CheckForOldConfig
    ; Check if the old version exists in AppData
    IfFileExists "$APPDATA\FreeScribe\settings.txt" 0 End
        ; Open Dialog to ask user if they want to uninstall the old version
        MessageBox MB_YESNO|MB_ICONQUESTION "An old configuration file has been detected. Would you like to remove it?" IDYES RemoveOldConfig IDNO End
        RemoveOldConfig:
            ClearErrors
            ; Remove the old version executable
            RMDir /r "$APPDATA\FreeScribe"
            ${If} ${Errors}
                MessageBox MB_RETRYCANCEL "Unable to remove old configuration. Please close any applications using these files and try again." IDRETRY RemoveOldConfig IDCANCEL ConfigFilesFailed
            ${EndIf}
            Goto End
    ConfigFilesFailed:
        MessageBox MB_OK|MB_ICONEXCLAMATION "Old configuration files could not be removed. Proceeding with installation."
    End:
FunctionEnd

; Define the section of the installer
Section "MainSection" SEC01
    Call CleanUninstall
    Call CheckForOldConfig
    ; Set output path to the installation directory
    SetOutPath "$INSTDIR"

    ${If} $SELECTED_OPTION == "CPU"
        ; Add files to the installer
        File /r "..\dist\freescribe-client-cpu\freescribe-client-cpu.exe"
        Rename "$INSTDIR\freescribe-client-cpu.exe" "$INSTDIR\freescribe-client.exe"
        File /r "..\dist\freescribe-client-cpu\_internal"
    ${EndIf}

    ${If} $SELECTED_OPTION == "NVIDIA"
        ; Add files to the installer
        File /r "..\dist\freescribe-client-nvidia\freescribe-client-nvidia.exe"
        Rename "$INSTDIR\freescribe-client-nvidia.exe" "$INSTDIR\freescribe-client.exe"
        File /r "..\dist\freescribe-client-nvidia\_internal"  
    ${EndIf}


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
    AddSize 2800000 ; Add the size in kilobytes for the models

    CreateDirectory "$INSTDIR\models"
    SetOutPath "$INSTDIR\models"

    ; Copy the license
    File ".\assets\gemma_license.txt"

    ; Check if the file already exists
    IfFileExists "$INSTDIR\models\gemma-2-2b-it-Q8_0.gguf" 0 +2
    Goto SkipDownload

    ; Install the gemma 2 q8
    inetc::get /TIMEOUT=30000 "https://huggingface.co/lmstudio-community/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q8_0.gguf?download=true" "$INSTDIR\models\gemma-2-2b-it-Q8_0.gguf" /END

SkipDownload:
    SetOutPath "$INSTDIR"

SectionEnd

; Define the uninstaller section
Section "Uninstall"
    ; Remove the installation directory and all its contents
    RMDir /r "$INSTDIR"

    ; Remove the start menu shortcut
    Delete "$SMPROGRAMS\FreeScribe\FreeScribe.lnk"
    RMDir "$SMPROGRAMS\FreeScribe"

    ; Remove the uninstaller entry from the Control Panel
    Delete "$INSTDIR\Uninstall.exe"

    RemoveConfigFiles:
        ; Remove configuration files if the checkbox is selected
        ${If} $REMOVE_CONFIG == ${BST_CHECKED}
            ClearErrors
            RMDir /r "$APPDATA\FreeScribe"
            ${If} ${Errors}
                MessageBox MB_RETRYCANCEL "Unable to remove old configuration. Please close any applications using these files and try again." IDRETRY RemoveConfigFiles IDCANCEL ConfigFilesFailed
            ${EndIf}
        ${EndIf}
    
    ; Show message when uninstallation is complete
    MessageBox MB_OK "FreeScribe has been successfully uninstalled."
    Goto EndUninstall

    ConfigFilesFailed:
        MessageBox MB_OK|MB_ICONEXCLAMATION "FreeScribe has been successfully uninstalled, but the configuration files could not be removed. Please close any applications using these files and try again."
    EndUninstall:
SectionEnd

# Variables for checkboxes
Var DesktopShortcutCheckbox
Var StartMenuCheckbox
Var RunAppCheckbox

Function CustomizeFinishPage
    !insertmacro MUI_HEADER_TEXT "Installation Complete" "Please select your preferences and close the installer."

    nsDialogs::Create 1018
    Pop $0
    
    ${If} $0 == error
        Abort
    ${EndIf}

    # Run App Checkbox
    ${NSD_CreateCheckbox} 10u 10u 100% 12u "Run FreeScribe after installation"
    Pop $RunAppCheckbox
    ${NSD_SetState} $RunAppCheckbox ${BST_CHECKED}

    # Desktop Shortcut Checkbox
    ${NSD_CreateCheckbox} 10u 30u 100% 12u "Create Desktop Shortcut"
    Pop $DesktopShortcutCheckbox
    ${NSD_SetState} $DesktopShortcutCheckbox ${BST_CHECKED}

    # Start Menu Checkbox
    ${NSD_CreateCheckbox} 10u 50u 100% 12u "Add to Start Menu"
    Pop $StartMenuCheckbox
    ${NSD_SetState} $StartMenuCheckbox ${BST_CHECKED}

    nsDialogs::Show
FunctionEnd

Function RunApp
    ${NSD_GetState} $RunAppCheckbox $0
    ${If} $0 == ${BST_CHECKED}
        Exec '"$INSTDIR\freescribe-client.exe"'
    ${EndIf}

    # Check Desktop Shortcut
    ${NSD_GetState} $DesktopShortcutCheckbox $0
    StrCmp $0 ${BST_CHECKED} +2
        Goto SkipDesktopShortcut
    CreateShortcut "$DESKTOP\FreeScribe.lnk" "$INSTDIR\freescribe-client.exe"
    SkipDesktopShortcut:

    # Check Start Menu
    ${NSD_GetState} $StartMenuCheckbox $0
    StrCmp $0 ${BST_CHECKED} +2
        Goto SkipStartMenu
    CreateDirectory "$SMPROGRAMS\FreeScribe"
    CreateShortcut "$SMPROGRAMS\FreeScribe\FreeScribe.lnk" "$INSTDIR\freescribe-client.exe"
    SkipStartMenu:
FunctionEnd

; Function to execute when leaving the InstallFiles page
; Goes to the next page after the installation is complete
Function InsfilesPageLeave
    SetAutoClose true
FunctionEnd

Function un.CreateRemoveConfigFilesPage
    !insertmacro MUI_HEADER_TEXT "Remove Configuration Files" "Do you want to remove the configuration files (e.g., settings)?"
    
    nsDialogs::Create 1018
    Pop $0

    ${If} $0 == error
        Abort
    ${EndIf}

    ${NSD_CreateCheckbox} 0 20u 100% 12u "Remove configuration files"
    Pop $REMOVE_CONFIG_CHECKBOX
    ${NSD_SetState} $REMOVE_CONFIG_CHECKBOX ${BST_CHECKED}

    nsDialogs::Show
FunctionEnd

Function un.RemoveConfigFilesPageLeave
    ${NSD_GetState} $REMOVE_CONFIG_CHECKBOX $REMOVE_CONFIG
FunctionEnd

; Define installer pages
!insertmacro MUI_PAGE_LICENSE ".\assets\License.txt"
Page Custom ARCHITECHTURE_SELECT
!insertmacro MUI_PAGE_DIRECTORY
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE InsfilesPageLeave
!insertmacro MUI_PAGE_INSTFILES
Page Custom CustomizeFinishPage RunApp

; Define the uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
UninstPage custom un.CreateRemoveConfigFilesPage un.RemoveConfigFilesPageLeave
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Define the languages
!insertmacro MUI_LANGUAGE English
