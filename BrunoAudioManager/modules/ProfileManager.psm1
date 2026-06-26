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

        foreach ($profile in $ProfileCatalog[$device]) {
            Ensure-PresetFile -ProfilesRoot $ProfilesRoot -Device $device -ProfileName $profile | Out-Null
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

    # Remove o prefixo do dispositivo do nome do perfil.
    # Exemplo: "HD599 - Rock & Metal" vira "Rock & Metal"
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

function Set-ActiveProfile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ProfilesRoot,

        [Parameter(Mandatory)]
        [string]$ActiveProfilePath,

        [Parameter(Mandatory)]
        [string]$Device,

        [Parameter(Mandatory)]
        [string]$ProfileName
    )

    $presetPath = Ensure-PresetFile -ProfilesRoot $ProfilesRoot -Device $Device -ProfileName $ProfileName
    $relativePath = Get-PresetRelativePath -Device $Device -ProfileName $ProfileName

    if (-not (Test-Path -LiteralPath $presetPath)) {
        throw "Preset file not found: $presetPath"
    }

    "Include: $relativePath" | Set-Content -LiteralPath $ActiveProfilePath -Encoding UTF8

    [pscustomobject]@{
        Device      = $Device
        ProfileName = $ProfileName
        DisplayName = "$Device / $ProfileName"
        IncludeLine = "Include: $relativePath"
    }
}

Export-ModuleMember -Function ConvertTo-PresetFileName, Get-PresetRelativePath, Ensure-ProfileLibrary, Ensure-PresetFile, Get-ActiveProfile, Set-ActiveProfile