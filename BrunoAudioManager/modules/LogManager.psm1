function Initialize-Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$LogsRoot
    )

    if (-not (Test-Path -LiteralPath $LogsRoot)) {
        New-Item -ItemType Directory -Path $LogsRoot -Force | Out-Null
    }
}

function Write-ProfileChangeLog {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$AudioLogPath,
        [Parameter(Mandatory)]
        [string]$OldProfile,
        [Parameter(Mandatory)]
        [string]$NewProfile
    )

    $folder = Split-Path -Parent $AudioLogPath
    if (-not (Test-Path -LiteralPath $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "$timestamp | Old: $OldProfile | New: $NewProfile"
    Add-Content -LiteralPath $AudioLogPath -Value $line -Encoding UTF8
}

function Write-ErrorLog {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$AudioLogPath,
        [Parameter(Mandatory)]
        [string]$Context,
        [Parameter(Mandatory)]
        [string]$ErrorMessage
    )

    $folder = Split-Path -Parent $AudioLogPath
    if (-not (Test-Path -LiteralPath $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "$timestamp | ERROR | $Context | $ErrorMessage"
    Add-Content -LiteralPath $AudioLogPath -Value $line -Encoding UTF8
}

Export-ModuleMember -Function Initialize-Log, Write-ProfileChangeLog, Write-ErrorLog
