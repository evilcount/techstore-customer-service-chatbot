function Test-EqualizerApoInstalled {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ApoConfigRoot
    )

    Test-Path -LiteralPath $ApoConfigRoot
}

function Test-PeaceInstalled {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$PeaceExePath,
        [Parameter(Mandatory)]
        [string]$PeaceConfigPath
    )

    (Test-Path -LiteralPath $PeaceExePath) -or (Test-Path -LiteralPath $PeaceConfigPath)
}

function Test-ConfigurationEditorInstalled {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ConfigEditorExePath
    )

    Test-Path -LiteralPath $ConfigEditorExePath
}

function Initialize-ApoStructure {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [psobject]$Paths,
        [Parameter(Mandatory)]
        [hashtable]$ProfileCatalog,
        [Parameter(Mandatory)]
        [string[]]$ManagedConfigLines
    )

    if (-not (Test-EqualizerApoInstalled -ApoConfigRoot $Paths.ApoConfigRoot)) {
        return [pscustomobject]@{
            EqualizerApoDetected = $false
            PeaceDetected        = $false
            ConfigEditorDetected = $false
            Message              = 'Equalizer APO was not found. Install it before switching profiles.'
        }
    }

    if (-not (Test-Path -LiteralPath $Paths.ProfilesRoot)) {
        New-Item -ItemType Directory -Path $Paths.ProfilesRoot -Force | Out-Null
    }

    Ensure-ProfileLibrary -ProfilesRoot $Paths.ProfilesRoot -ProfileCatalog $ProfileCatalog

    if (-not (Test-Path -LiteralPath $Paths.ActiveProfilePath)) {
        Set-ActiveProfile -ProfilesRoot $Paths.ProfilesRoot -ActiveProfilePath $Paths.ActiveProfilePath -Device 'HD599' -ProfileName 'Reference' | Out-Null
    }

    if (-not (Test-Path -LiteralPath $Paths.ApoConfigPath)) {
        $ManagedConfigLines | Set-Content -LiteralPath $Paths.ApoConfigPath -Encoding UTF8
    }

    [pscustomobject]@{
        EqualizerApoDetected = $true
        PeaceDetected        = Test-PeaceInstalled -PeaceExePath $Paths.PeaceExePath -PeaceConfigPath $Paths.PeaceConfigPath
        ConfigEditorDetected = Test-ConfigurationEditorInstalled -ConfigEditorExePath $Paths.ConfigEditorExePath
        Message              = 'Equalizer APO profile structure is ready.'
    }
}

Export-ModuleMember -Function Test-EqualizerApoInstalled, Test-PeaceInstalled, Test-ConfigurationEditorInstalled, Initialize-ApoStructure
