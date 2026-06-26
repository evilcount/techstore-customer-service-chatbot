[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$publishRoot = Join-Path $projectRoot 'dist'
$exeTarget = Join-Path $publishRoot 'BrunoAudioManager.exe'
$scriptSource = Join-Path $projectRoot 'BrunoAudioManager.ps1'
$scriptTarget = Join-Path $publishRoot 'BrunoAudioManager.ps1'
$sourcePath = Join-Path $projectRoot 'launcher\Program.cs'
$manifestPath = Join-Path $projectRoot 'launcher\app.manifest'
$cscPath = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'

if (-not (Test-Path -LiteralPath $cscPath)) {
    $cscPath = 'C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe'
}

if (-not (Test-Path -LiteralPath $cscPath)) {
    throw 'csc.exe was not found. Install .NET Framework developer tools or use the script directly with PowerShell 7.'
}

if (-not (Test-Path -LiteralPath $publishRoot)) {
    New-Item -ItemType Directory -Path $publishRoot -Force | Out-Null
}

& $cscPath `
    /nologo `
    /target:winexe `
    /optimize+ `
    /win32manifest:$manifestPath `
    /out:$exeTarget `
    $sourcePath

Copy-Item -LiteralPath $scriptSource -Destination $scriptTarget -Force

Write-Host "Executable generated: $exeTarget"
