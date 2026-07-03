[CmdletBinding()]
param(
    [switch]$SelfTest,
    [string]$ApoConfigRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Error 'Bruno Audio Manager requires PowerShell 7 or newer.'
    exit 1
}

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ModuleRoot = Join-Path $ProjectRoot 'modules'

Import-Module (Join-Path $ModuleRoot 'AppConfig.psm1') -Force -DisableNameChecking
Import-Module (Join-Path $ModuleRoot 'AppPaths.psm1') -Force -DisableNameChecking
Import-Module (Join-Path $ModuleRoot 'SettingsManager.psm1') -Force -DisableNameChecking
Import-Module (Join-Path $ModuleRoot 'LogManager.psm1') -Force -DisableNameChecking
Import-Module (Join-Path $ModuleRoot 'ProfileManager.psm1') -Force -DisableNameChecking
Import-Module (Join-Path $ModuleRoot 'ApoManager.psm1') -Force -DisableNameChecking
Import-Module (Join-Path $ModuleRoot 'BackupManager.psm1') -Force -DisableNameChecking
Import-Module (Join-Path $ModuleRoot 'ToolLauncher.psm1') -Force -DisableNameChecking
Import-Module (Join-Path $ModuleRoot 'MainForm.psm1') -Force -DisableNameChecking

$appInfo = Get-AppInfo
$paths = Get-AppPaths -ProjectRoot $ProjectRoot -ApoConfigRoot $ApoConfigRoot
$defaultPreferences = Get-DefaultPreferences
$profileCatalog = Get-ProfileCatalog

Initialize-Settings -SettingsRoot $paths.SettingsRoot -PreferencesPath $paths.PreferencesPath -DefaultPreferences $defaultPreferences
Initialize-Log -LogsRoot $paths.LogsRoot
$preferences = Get-Preferences -PreferencesPath $paths.PreferencesPath -DefaultPreferences $defaultPreferences

if ($SelfTest) {
    if ($preferences.selectedDevice -ne 'HD599') {
        throw 'Default preferences self-test failed.'
    }

    if (-not [string]::IsNullOrWhiteSpace($ApoConfigRoot)) {
        New-Item -ItemType Directory -Path $ApoConfigRoot -Force | Out-Null
    }

    $apoStatus = Initialize-ApoStructure -Paths $paths -ProfileCatalog $profileCatalog -ManagedConfigLines (Get-ManagedConfigLines)
    if (-not $apoStatus.EqualizerApoDetected) {
        throw 'APO structure self-test failed because the test APO root was not detected.'
    }

    $selfTestPreset = Join-Path $paths.ProfilesRoot 'HD599\HD599 - Music.txt'
    if (-not (Test-Path -LiteralPath (Split-Path -Parent $selfTestPreset))) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $selfTestPreset) -Force | Out-Null
    }
    @(
        'Preamp: -6 dB'
        'Filter: ON PK Fc 1000 Hz Gain 3 dB Q 1'
    ) | Set-Content -LiteralPath $selfTestPreset -Encoding UTF8

    Set-ActiveProfile -ProfilesRoot $paths.ProfilesRoot -ActiveProfilePath $paths.ActiveProfilePath -ConfigPath $paths.ApoConfigPath -Device 'HD599' -ProfileName 'Music' | Out-Null
    $activeProfile = Get-ActiveProfile -ActiveProfilePath $paths.ActiveProfilePath
    if ($activeProfile.DisplayName -ne 'HD599 / Music') {
        throw 'Active profile self-test failed.'
    }

    $backupPath = Join-Path ([System.IO.Path]::GetTempPath()) 'BrunoAudioManager-ProfilesBackup.zip'
    Export-ProfilesBackup -ProfilesRoot $paths.ProfilesRoot -DestinationZip $backupPath | Out-Null
    Import-ProfilesBackup -ProfilesRoot $paths.ProfilesRoot -SourceZip $backupPath
    if (-not (Test-Path -LiteralPath $backupPath)) {
        throw 'Backup export self-test failed.'
    }

    Write-Host "$($appInfo.Name) $($appInfo.Version) self-test bootstrap OK"
    Write-Host 'Paths, settings, and logging self-test OK'
    Write-Host 'APO and profile management self-test OK'
    Write-Host 'Backup management self-test OK'
    exit 0
}

try {
    $apoStatus = Initialize-ApoStructure -Paths $paths -ProfileCatalog $profileCatalog -ManagedConfigLines (Get-ManagedConfigLines)
}
catch {
    $apoStatus = [pscustomobject]@{
        EqualizerApoDetected = $false
        PeaceDetected        = $false
        ConfigEditorDetected = $false
        Message              = "Unable to prepare Equalizer APO: $($_.Exception.Message)"
    }
}

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($apoStatus.EqualizerApoDetected -and -not $isAdmin) {
    $apoStatus.Message = "AVISO: Execute como administrador para aplicar perfis. $($apoStatus.Message)"
}

Show-BrunoAudioManagerForm -Paths $paths -AppInfo $appInfo -ProfileCatalog $profileCatalog -ApoStatus $apoStatus -Preferences $preferences

