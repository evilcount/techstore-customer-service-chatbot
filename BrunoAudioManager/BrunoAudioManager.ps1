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

Import-Module (Join-Path $ModuleRoot 'AppConfig.psm1') -Force

if ($SelfTest) {
    $appInfo = Get-AppInfo
    Write-Host "$($appInfo.Name) $($appInfo.Version) self-test bootstrap OK"
    exit 0
}

Write-Host 'Bruno Audio Manager bootstrap is ready. Additional modules will be loaded in later tasks.'
