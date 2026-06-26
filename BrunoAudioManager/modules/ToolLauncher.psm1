function Open-ExistingPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path,
        [Parameter(Mandatory)]
        [string]$FriendlyName
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$FriendlyName was not found: $Path"
    }

    Start-Process -FilePath $Path | Out-Null
}

function Open-Documentation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$UserGuidePath
    )

    Open-ExistingPath -Path $UserGuidePath -FriendlyName 'Documentation'
}

Export-ModuleMember -Function Open-ExistingPath, Open-Documentation
