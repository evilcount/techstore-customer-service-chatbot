[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$buildScript = Join-Path $projectRoot 'tools\Build-Exe.ps1'
$exePath = Join-Path $projectRoot 'dist\BrunoAudioManager.exe'
$scriptCopyPath = Join-Path $projectRoot 'dist\BrunoAudioManager.ps1'

& $buildScript

if (-not (Test-Path -LiteralPath $exePath)) {
    throw "Expected launcher was not generated: $exePath"
}

if (-not (Test-Path -LiteralPath $scriptCopyPath)) {
    throw "Expected script copy was not generated: $scriptCopyPath"
}

Write-Host 'Launcher build test passed'
