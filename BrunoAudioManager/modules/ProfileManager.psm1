function ConvertTo-PresetFileName {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Device,

        [Parameter(Mandatory)]
        [string]$ProfileName
    )

    $safeDevice = $Device -replace '[\\/:*?"<>|]', ''
    $safeDevice = $safeDevice -replace '\s+', ' '

    $safeProfile = $ProfileName -replace '[\\/:*?"<>|]', ''
    $safeProfile = $safeProfile -replace '\s+', ' '

    return "$($safeDevice.Trim()) - $($safeProfile.Trim()).txt"
}

function Get-PresetRelativePath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Device,

        [Parameter(Mandatory)]
        [string]$ProfileName
    )

    $fileName = ConvertTo-PresetFileName -Device $Device -ProfileName $ProfileName
    return Join-Path $Device $fileName
}

function Ensure-ProfileLibrary {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ProfilesRoot,

        [Parameter(Mandatory)]
        [hashtable]$ProfileCatalog
    )

    if (-not (Test-Path -LiteralPath $ProfilesRoot)) {
        New-Item -ItemType Directory -Path $ProfilesRoot -Force | Out-Null
    }

    foreach ($device in $ProfileCatalog.Keys) {
        $devicePath = Join-Path $ProfilesRoot $device

        if (-not (Test-Path -LiteralPath $devicePath)) {
            New-Item -ItemType Directory -Path $devicePath -Force | Out-Null
        }
    }
}

function Ensure-PresetFile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ProfilesRoot,

        [Parameter(Mandatory)]
        [string]$Device,

        [Parameter(Mandatory)]
        [string]$ProfileName
    )

    $devicePath = Join-Path $ProfilesRoot $Device

    if (-not (Test-Path -LiteralPath $devicePath)) {
        New-Item -ItemType Directory -Path $devicePath -Force | Out-Null
    }

    $presetPath = Join-Path $ProfilesRoot (Get-PresetRelativePath -Device $Device -ProfileName $ProfileName)

    if (-not (Test-Path -LiteralPath $presetPath)) {
        @(
            '# Bruno Audio Manager preset'
            "# Device: $Device"
            "# Profile: $ProfileName"
            '# Add Equalizer APO filters below this line.'
            ''
            'Preamp: 0 dB'
        ) | Set-Content -LiteralPath $presetPath -Encoding UTF8
    }

    return $presetPath
}

function Get-ActiveProfile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ActiveProfilePath
    )

    if (-not (Test-Path -LiteralPath $ActiveProfilePath)) {
        return [pscustomobject]@{
            Device      = 'HD599'
            ProfileName = 'Reference'
            DisplayName = 'HD599 / Reference'
            IncludeLine = ''
        }
    }

    $line = Get-Content -LiteralPath $ActiveProfilePath |
        Where-Object { $_ -match '^Include:\s*(.+)$' } |
        Select-Object -First 1

    if (-not $line) {
        return [pscustomobject]@{
            Device      = 'HD599'
            ProfileName = 'Reference'
            DisplayName = 'HD599 / Reference'
            IncludeLine = ''
        }
    }

    $relativePath = ($line -replace '^Include:\s*', '').Trim()
    $parts = $relativePath -split '[\\/]'

    $device = if ($parts.Count -ge 2) { $parts[0] } else { 'HD599' }
    $fileName = if ($parts.Count -ge 2) { $parts[1] } else { $parts[0] }

    $profileName = [System.IO.Path]::GetFileNameWithoutExtension($fileName)

    # Remove the device prefix from file names like "HD599 - Rock & Metal".
    if ($profileName -like "$device - *") {
        $profileName = $profileName.Substring($device.Length + 3)
    }

    [pscustomobject]@{
        Device      = $device
        ProfileName = $profileName
        DisplayName = "$device / $profileName"
        IncludeLine = $line
    }
}

function Test-PresetHasAudibleContent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$PresetContent
    )

    $activeLines = $PresetContent -split "`r?`n" | Where-Object {
        $line = $_.Trim()
        -not [string]::IsNullOrWhiteSpace($line) -and
        -not $line.StartsWith('#')
    }

    return [bool]($activeLines | Select-Object -First 1)
}

function New-ManagedConfigContent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Device,

        [Parameter(Mandatory)]
        [string]$ProfileName,

        [Parameter(Mandatory)]
        [string]$RelativePath,

        [Parameter(Mandatory)]
        [string]$PresetContent
    )

    @"
# Bruno Audio Manager
# Active profile: $Device / $ProfileName
# Source: Profiles\$RelativePath

$PresetContent
"@
}

function Set-ActiveProfile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ProfilesRoot,

        [Parameter(Mandatory)]
        [string]$ActiveProfilePath,

        [Parameter(Mandatory)]
        [string]$ConfigPath,

        [Parameter(Mandatory)]
        [string]$Device,

        [Parameter(Mandatory)]
        [string]$ProfileName
    )

    $relativePath = Get-PresetRelativePath -Device $Device -ProfileName $ProfileName
    $presetPath = Join-Path $ProfilesRoot $relativePath

    if (-not (Test-Path -LiteralPath $presetPath)) {
        throw "Preset file not found: $presetPath"
    }

    $presetContent = Get-Content -LiteralPath $presetPath -Raw
    $hasAudibleContent = Test-PresetHasAudibleContent -PresetContent $presetContent
    $warningMessage = if ($hasAudibleContent) { '' } else { 'Este preset não contém filtros ativos; o perfil pode não ter efeito audível.' }

    $activeFolder = Split-Path -Parent $ActiveProfilePath
    if (-not (Test-Path -LiteralPath $activeFolder)) {
        New-Item -ItemType Directory -Path $activeFolder -Force | Out-Null
    }

    # Active.txt remains a readable record of the selected preset.
    "Include: $relativePath" | Set-Content -LiteralPath $ActiveProfilePath -Encoding UTF8

    $managedConfig = New-ManagedConfigContent -Device $Device -ProfileName $ProfileName -RelativePath $relativePath -PresetContent $presetContent
    try {
        Set-Content -LiteralPath $ConfigPath -Value $managedConfig -Encoding UTF8
    }
    catch [System.UnauthorizedAccessException] {
        throw "Não foi possível escrever no config.txt. Execute o Bruno Audio Manager como administrador. Caminho: $ConfigPath"
    }
    catch {
        throw "Não foi possível escrever no config.txt. Execute o Bruno Audio Manager como administrador se o arquivo estiver em Program Files. Detalhes: $($_.Exception.Message)"
    }

    [pscustomobject]@{
        Device            = $Device
        ProfileName       = $ProfileName
        DisplayName       = "$Device / $ProfileName"
        IncludeLine       = "Include: $relativePath"
        PresetPath        = $presetPath
        ConfigPath        = $ConfigPath
        HasAudibleContent = $hasAudibleContent
        WarningMessage    = $warningMessage
    }
}

Export-ModuleMember -Function ConvertTo-PresetFileName, Get-PresetRelativePath, Ensure-ProfileLibrary, Ensure-PresetFile, Get-ActiveProfile, Test-PresetHasAudibleContent, New-ManagedConfigContent, Set-ActiveProfile
