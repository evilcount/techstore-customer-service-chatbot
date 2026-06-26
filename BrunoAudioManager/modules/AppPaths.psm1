function Get-ProjectRoot {
    [CmdletBinding()]
    param(
        [string]$StartPath
    )

    if ([string]::IsNullOrWhiteSpace($StartPath)) {
        return (Split-Path -Parent $PSScriptRoot)
    }

    return (Resolve-Path -LiteralPath $StartPath).Path
}

function Get-AppPaths {
    [CmdletBinding()]
    param(
        [string]$ProjectRoot,
        [string]$ApoConfigRoot
    )

    if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
        $ProjectRoot = Split-Path -Parent $PSScriptRoot
    }

    if ([string]::IsNullOrWhiteSpace($ApoConfigRoot)) {
        $ApoConfigRoot = 'C:\Program Files\EqualizerAPO\config'
    }

    $profilesRoot = Join-Path $ApoConfigRoot 'Profiles'

    [pscustomobject]@{
        ProjectRoot         = $ProjectRoot
        ModulesRoot         = Join-Path $ProjectRoot 'modules'
        AssetsRoot          = Join-Path $ProjectRoot 'assets'
        DocsRoot            = Join-Path $ProjectRoot 'docs'
        UserGuidePath       = Join-Path (Join-Path $ProjectRoot 'docs') 'USER_GUIDE.md'
        LogsRoot            = Join-Path $ProjectRoot 'logs'
        AudioLogPath        = Join-Path (Join-Path $ProjectRoot 'logs') 'audio.log'
        SettingsRoot        = Join-Path $ProjectRoot 'settings'
        PreferencesPath     = Join-Path (Join-Path $ProjectRoot 'settings') 'preferences.json'
        ApoConfigRoot       = $ApoConfigRoot
        ApoConfigPath       = Join-Path $ApoConfigRoot 'config.txt'
        PeaceConfigPath     = Join-Path $ApoConfigRoot 'peace.txt'
        ProfilesRoot        = $profilesRoot
        ActiveProfilePath   = Join-Path $profilesRoot 'Active.txt'
        PeaceExePath        = Join-Path $ApoConfigRoot 'Peace.exe'
        ConfigEditorExePath = 'C:\Program Files\EqualizerAPO\Editor.exe'
    }
}

function Ensure-Directory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }

    return (Resolve-Path -LiteralPath $Path).Path
}

Export-ModuleMember -Function Get-ProjectRoot, Get-AppPaths, Ensure-Directory
