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

if ($SelfTest) {
    $appInfo = Get-AppInfo
    $paths = Get-AppPaths -ProjectRoot $ProjectRoot -ApoConfigRoot $ApoConfigRoot
    $defaultPreferences = Get-DefaultPreferences

    Initialize-Settings -SettingsRoot $paths.SettingsRoot -PreferencesPath $paths.PreferencesPath -DefaultPreferences $defaultPreferences
    Initialize-Log -LogsRoot $paths.LogsRoot
    $preferences = Get-Preferences -PreferencesPath $paths.PreferencesPath -DefaultPreferences $defaultPreferences

    if ($preferences.selectedDevice -ne 'HD599') {
        throw 'Default preferences self-test failed.'
    }

    Write-Host "$($appInfo.Name) $($appInfo.Version) self-test bootstrap OK"
    Write-Host 'Paths, settings, and logging self-test OK'
    exit 0
}

Write-Host 'Bruno Audio Manager bootstrap is ready. Additional modules will be loaded in later tasks.'
