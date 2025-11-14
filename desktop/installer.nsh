; NSIS Installer Custom Script for Smart Hiring System

; Custom installer page for MongoDB installation
!macro customInit
  ; Check if MongoDB is already installed
  ReadRegStr $0 HKLM "SOFTWARE\MongoDB\Server\6.0" "InstallPath"
  ${If} $0 == ""
    ; MongoDB not found, ask user
    MessageBox MB_YESNO "MongoDB is not installed. Would you like to install MongoDB Community Server? (Recommended for local deployment)" IDYES installMongo IDNO skipMongo
    installMongo:
      SetOutPath "$TEMP"
      File "${BUILD_RESOURCES_DIR}\mongodb-installer.msi"
      ExecWait "msiexec /i $TEMP\mongodb-installer.msi /qn /norestart" $1
      ${If} $1 != 0
        MessageBox MB_OK "MongoDB installation failed. You can install it manually later or use MongoDB Atlas (cloud)."
      ${EndIf}
      Delete "$TEMP\mongodb-installer.msi"
    skipMongo:
  ${EndIf}
!macroend

; Custom uninstaller actions
!macro customUnInit
  ; Ask if user wants to keep data
  MessageBox MB_YESNO "Do you want to keep your database data and configuration? (Click Yes to keep, No to remove everything)" IDYES keepData IDNO removeData
  keepData:
    ; Keep data, just remove application
    Goto done
  removeData:
    ; Remove all data
    RMDir /r "$APPDATA\smart-hiring-system"
    RMDir /r "$LOCALAPPDATA\smart-hiring-system"
  done:
!macroend

; Custom install complete page
!macro customInstallMode
  ; Create environment file from template
  ${If} ${FileExists} "$INSTDIR\resources\.env.template"
    ${IfNot} ${FileExists} "$APPDATA\smart-hiring-system\.env"
      CreateDirectory "$APPDATA\smart-hiring-system"
      CopyFiles "$INSTDIR\resources\.env.template" "$APPDATA\smart-hiring-system\.env"
    ${EndIf}
  ${EndIf}
!macroend
