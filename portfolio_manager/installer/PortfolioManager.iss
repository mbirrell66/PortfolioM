; ============================================================
;  Portfolio Manager — Inno Setup installer script
;  Inno Setup 6.x required (https://jrsoftware.org/isinfo.php)
;
;  How to build:
;    1. Build the application first:
;         cd portfolio_manager
;         pyinstaller PortfolioManager.spec
;       This produces:
;         portfolio_manager\dist\PortfolioManager\PortfolioManager.exe
;         portfolio_manager\dist\PortfolioManager\_internal\
;
;    2. (Optional) Convert portfolio_manager\PortM.png to portfolio_manager\PortM.ico
;       using an online converter or ImageMagick:
;         magick portfolio_manager\PortM.png -define icon:auto-resize=256,128,64,48,32,16 portfolio_manager\PortM.ico
;
;    3. Open this file in Inno Setup Compiler and press Compile (F9),
;       or run from the command line:
;         ISCC.exe installer\PortfolioManager.iss
;
;  The finished installer will be written to:
;    installer\Output\PortfolioManager-Setup-{#AppVersion}.exe
; ============================================================

#define AppName        "Portfolio Manager"
#define AppVersion     "1.0.0"
#define AppPublisher   "Martin Birrell"
#define AppURL         "https://github.com/martin-birrell/PortfolioM"
#define AppExeName     "PortfolioManager.exe"
#define AppDescription "Personal portfolio tracking and financial management"

; Root of the repo — this .iss file lives in installer\ so the root is one level up
#define RepoRoot       ".."
#define DistDir        RepoRoot + "\portfolio_manager\dist\PortfolioManager"
#define IconFile       RepoRoot + "\portfolio_manager\PortM.ico"

[Setup]
; ---- Identity -------------------------------------------------------
AppId                     = {{A3F7C2E1-8B4D-4A9F-B6E2-1C0D5F8A2E3B}
AppName                   = {#AppName}
AppVersion                = {#AppVersion}
AppVerName                = {#AppName} {#AppVersion}
AppPublisher              = {#AppPublisher}
AppPublisherURL           = {#AppURL}
AppSupportURL             = {#AppURL}
AppUpdatesURL             = {#AppURL}
AppCopyright              = Copyright (C) 2024 {#AppPublisher}
AppComments               = {#AppDescription}

; ---- Paths ----------------------------------------------------------
; Install to %LOCALAPPDATA%\PortfolioM so the app can write its
; SQLite database next to the exe without requiring admin rights.
DefaultDirName            = {localappdata}\PortfolioM
DefaultGroupName          = {#AppName}
DisableDirPage            = no
DisableProgramGroupPage   = yes

; ---- Output ---------------------------------------------------------
OutputDir                 = Output
OutputBaseFilename        = PortfolioManager-Setup-{#AppVersion}
SetupIconFile             = {#IconFile}
UninstallDisplayIcon      = {app}\{#AppExeName}
UninstallDisplayName      = {#AppName} {#AppVersion}

; ---- Compression ----------------------------------------------------
Compression               = lzma2/ultra64
SolidCompression          = yes
LZMAUseSeparateProcess    = yes

; ---- Appearance / behaviour -----------------------------------------
WizardStyle               = modern
WizardSizePercent         = 120
ShowLanguageDialog        = no

; ---- Misc -----------------------------------------------------------
ArchitecturesInstallIn64BitMode = x64compatible
MinVersion                = 10.0
PrivilegesRequired        = lowest
PrivilegesRequiredOverridesAllowed = dialog
CloseApplications         = yes
RestartApplications       = no
CreateUninstallRegKey     = yes

; ---- Version info embedded in the installer exe ---------------------
VersionInfoVersion        = {#AppVersion}
VersionInfoCompany        = {#AppPublisher}
VersionInfoDescription    = {#AppName} Setup
VersionInfoProductName    = {#AppName}
VersionInfoProductVersion = {#AppVersion}


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"


[Tasks]
Name: "desktopicon";    Description: "Create a &desktop shortcut";      GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "startupicon";   Description: "Launch {#AppName} at &Windows startup"; GroupDescription: "Additional shortcuts:"; Flags: unchecked


[Files]
; ---- Main executable ------------------------------------------------
Source: "{#DistDir}\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; ---- _internal\ (all PyInstaller dependencies) ---------------------
Source: "{#DistDir}\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; ---- Application icon (for shortcut display) -----------------------
; The .ico is optional; remove these two lines if you have not yet
; converted PortM.png to PortM.ico.
Source: "{#RepoRoot}\portfolio_manager\PortM.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist


[Dirs]
; Pre-create the data directory so the app can write its database
; without needing elevated permissions on first launch.
Name: "{app}\data"; Permissions: users-full


[Icons]
; Start Menu shortcut
Name: "{group}\{#AppName}";                  Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\PortM.ico"; Comment: "{#AppDescription}"
Name: "{group}\Uninstall {#AppName}";        Filename: "{uninstallexe}"

; Desktop shortcut (optional task)
Name: "{userdesktop}\{#AppName}";            Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\PortM.ico"; Comment: "{#AppDescription}"; Tasks: desktopicon

; Startup shortcut (optional task)
Name: "{userstartup}\{#AppName}";            Filename: "{app}\{#AppExeName}"; Tasks: startupicon


[Run]
; Offer to launch the application after installation completes
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent


[UninstallRun]
; Nothing extra needed — Inno Setup removes all installed files automatically


[UninstallDelete]
; Remove the user-data directory on uninstall.
; CAUTION: this deletes the portfolio database.
; Comment out the line below if you want to preserve user data on uninstall.
Type: filesandordirs; Name: "{app}\data"


[Code]
// ---------------------------------------------------------------------------
// Upgrade / reinstall detection
// ---------------------------------------------------------------------------
function GetUninstallString(): String;
var
  sUnInstPath, sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function InitializeSetup(): Boolean;
var
  V: Integer;
  iResultCode: Integer;
  sUnInstallString: String;
begin
  Result := True;

  // If a previous version is installed, offer to uninstall it first
  if IsUpgrade() then
  begin
    V := MsgBox(
      ExpandConstant('{#AppName} is already installed. The previous version will be removed before installing the new one. Continue?'),
      mbConfirmation,
      MB_YESNO
    );
    if V = IDYES then
    begin
      sUnInstallString := GetUninstallString();
      sUnInstallString := RemoveQuotes(sUnInstallString);
      Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES', '', SW_HIDE, ewWaitUntilTerminated, iResultCode);
    end else begin
      Result := False;
    end;
  end;
end;
