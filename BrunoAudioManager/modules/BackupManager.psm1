function Export-ProfilesBackup {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ProfilesRoot,
        [Parameter(Mandatory)]
        [string]$DestinationZip
    )

    if (-not (Test-Path -LiteralPath $ProfilesRoot)) {
        throw "Profiles folder was not found: $ProfilesRoot"
    }

    $destinationFolder = Split-Path -Parent $DestinationZip
    if (-not (Test-Path -LiteralPath $destinationFolder)) {
        New-Item -ItemType Directory -Path $destinationFolder -Force | Out-Null
    }

    if (Test-Path -LiteralPath $DestinationZip) {
        Remove-Item -LiteralPath $DestinationZip -Force
    }

    Compress-Archive -Path (Join-Path $ProfilesRoot '*') -DestinationPath $DestinationZip -Force
    return $DestinationZip
}

function Import-ProfilesBackup {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ProfilesRoot,
        [Parameter(Mandatory)]
        [string]$SourceZip
    )

    if (-not (Test-Path -LiteralPath $SourceZip)) {
        throw "Backup ZIP was not found: $SourceZip"
    }

    if (-not (Test-Path -LiteralPath $ProfilesRoot)) {
        New-Item -ItemType Directory -Path $ProfilesRoot -Force | Out-Null
    }

    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("BrunoAudioManagerImport-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

    try {
        Expand-Archive -LiteralPath $SourceZip -DestinationPath $tempRoot -Force
        $items = Get-ChildItem -LiteralPath $tempRoot -Force
        if (-not $items) {
            throw 'Backup ZIP is empty.'
        }

        Copy-Item -Path (Join-Path $tempRoot '*') -Destination $ProfilesRoot -Recurse -Force
    }
    finally {
        if (Test-Path -LiteralPath $tempRoot) {
            Remove-Item -LiteralPath $tempRoot -Recurse -Force
        }
    }
}

Export-ModuleMember -Function Export-ProfilesBackup, Import-ProfilesBackup
