function Initialize-Settings {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$SettingsRoot,
        [Parameter(Mandatory)]
        [string]$PreferencesPath,
        [Parameter(Mandatory)]
        [psobject]$DefaultPreferences
    )

    if (-not (Test-Path -LiteralPath $SettingsRoot)) {
        New-Item -ItemType Directory -Path $SettingsRoot -Force | Out-Null
    }

    if (-not (Test-Path -LiteralPath $PreferencesPath)) {
        Save-Preferences -PreferencesPath $PreferencesPath -Preferences $DefaultPreferences
    }
}

function Get-Preferences {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$PreferencesPath,
        [Parameter(Mandatory)]
        [psobject]$DefaultPreferences
    )

    if (-not (Test-Path -LiteralPath $PreferencesPath)) {
        Save-Preferences -PreferencesPath $PreferencesPath -Preferences $DefaultPreferences
        return $DefaultPreferences
    }

    try {
        $content = Get-Content -LiteralPath $PreferencesPath -Raw
        if ([string]::IsNullOrWhiteSpace($content)) {
            return $DefaultPreferences
        }

        return $content | ConvertFrom-Json
    }
    catch {
        Save-Preferences -PreferencesPath $PreferencesPath -Preferences $DefaultPreferences
        return $DefaultPreferences
    }
}

function Save-Preferences {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$PreferencesPath,
        [Parameter(Mandatory)]
        [psobject]$Preferences
    )

    $folder = Split-Path -Parent $PreferencesPath
    if (-not (Test-Path -LiteralPath $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }

    $Preferences | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $PreferencesPath -Encoding UTF8
}

Export-ModuleMember -Function Initialize-Settings, Get-Preferences, Save-Preferences
