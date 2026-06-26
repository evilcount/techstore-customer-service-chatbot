[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$modulePath = Join-Path $PSScriptRoot '..\modules\ProfileManager.psm1'
Import-Module $modulePath -Force -DisableNameChecking

function Assert-Equal {
    param(
        [Parameter(Mandatory)]
        $Actual,
        [Parameter(Mandatory)]
        $Expected,
        [Parameter(Mandatory)]
        [string]$Message
    )

    if ($Actual -ne $Expected) {
        throw "$Message Expected: [$Expected]. Actual: [$Actual]."
    }
}

function Assert-Contains {
    param(
        [Parameter(Mandatory)]
        [string]$Text,
        [Parameter(Mandatory)]
        [string]$ExpectedSubstring,
        [Parameter(Mandatory)]
        [string]$Message
    )

    if (-not $Text.Contains($ExpectedSubstring)) {
        throw "$Message Missing substring: [$ExpectedSubstring]."
    }
}

function Assert-Throws {
    param(
        [Parameter(Mandatory)]
        [scriptblock]$ScriptBlock,
        [Parameter(Mandatory)]
        [string]$ExpectedMessage,
        [Parameter(Mandatory)]
        [string]$Message
    )

    try {
        & $ScriptBlock
    }
    catch {
        if ($_.Exception.Message -notlike "*$ExpectedMessage*") {
            throw "$Message Expected error containing [$ExpectedMessage]. Actual: [$($_.Exception.Message)]."
        }
        return
    }

    throw "$Message Expected an exception, but none was thrown."
}

function New-TestApoRoot {
    $root = Join-Path ([System.IO.Path]::GetTempPath()) ("BrunoAudioManager-Test-" + [guid]::NewGuid().ToString('N'))
    $profilesRoot = Join-Path $root 'Profiles'
    New-Item -ItemType Directory -Path (Join-Path $profilesRoot 'HD599') -Force | Out-Null

    [pscustomobject]@{
        Root              = $root
        ProfilesRoot      = $profilesRoot
        ActiveProfilePath = Join-Path $profilesRoot 'Active.txt'
        ConfigPath        = Join-Path $root 'config.txt'
    }
}

$testRoot = New-TestApoRoot

try {
    $presetPath = Join-Path $testRoot.ProfilesRoot 'HD599\HD599 - Rock & Metal.txt'
    @(
        'Preamp: -8 dB'
        'Filter: ON PK Fc 1000 Hz Gain 4 dB Q 1'
    ) | Set-Content -LiteralPath $presetPath -Encoding UTF8

    $result = Set-ActiveProfile `
        -ProfilesRoot $testRoot.ProfilesRoot `
        -ActiveProfilePath $testRoot.ActiveProfilePath `
        -ConfigPath $testRoot.ConfigPath `
        -Device 'HD599' `
        -ProfileName 'Rock & Metal'

    Assert-Equal -Actual (Get-Content -LiteralPath $testRoot.ActiveProfilePath -Raw).Trim() -Expected 'Include: HD599\HD599 - Rock & Metal.txt' -Message 'Active.txt should track the selected preset.'

    $configContent = Get-Content -LiteralPath $testRoot.ConfigPath -Raw
    Assert-Contains -Text $configContent -ExpectedSubstring '# Bruno Audio Manager' -Message 'config.txt should be managed by Bruno Audio Manager.'
    Assert-Contains -Text $configContent -ExpectedSubstring '# Active profile: HD599 / Rock & Metal' -Message 'config.txt should name the active profile.'
    Assert-Contains -Text $configContent -ExpectedSubstring '# Source: Profiles\HD599\HD599 - Rock & Metal.txt' -Message 'config.txt should name the preset source.'
    Assert-Contains -Text $configContent -ExpectedSubstring 'Preamp: -8 dB' -Message 'config.txt should contain preset filters.'
    Assert-Contains -Text $configContent -ExpectedSubstring 'Filter: ON PK Fc 1000 Hz Gain 4 dB Q 1' -Message 'config.txt should contain all preset filter lines.'
    Assert-Equal -Actual $result.PresetPath -Expected $presetPath -Message 'Set-ActiveProfile should return the applied preset path.'
    Assert-Equal -Actual $result.ConfigPath -Expected $testRoot.ConfigPath -Message 'Set-ActiveProfile should return the written config path.'
    Assert-Equal -Actual $result.HasAudibleContent -Expected $true -Message 'Filter presets should be marked as audible.'

    Assert-Throws -ScriptBlock {
        Set-ActiveProfile `
            -ProfilesRoot $testRoot.ProfilesRoot `
            -ActiveProfilePath $testRoot.ActiveProfilePath `
            -ConfigPath $testRoot.ConfigPath `
            -Device 'HD599' `
            -ProfileName 'Missing'
    } -ExpectedMessage 'Preset file not found' -Message 'Missing presets should fail clearly.'

    $commentOnlyPath = Join-Path $testRoot.ProfilesRoot 'HD599\HD599 - Reference.txt'
    @(
        '# Comment only'
        ''
        '# No filters here'
    ) | Set-Content -LiteralPath $commentOnlyPath -Encoding UTF8

    $commentOnlyResult = Set-ActiveProfile `
        -ProfilesRoot $testRoot.ProfilesRoot `
        -ActiveProfilePath $testRoot.ActiveProfilePath `
        -ConfigPath $testRoot.ConfigPath `
        -Device 'HD599' `
        -ProfileName 'Reference'

    Assert-Equal -Actual $commentOnlyResult.HasAudibleContent -Expected $false -Message 'Comment-only presets should be reported as non-audible.'
    Assert-Contains -Text $commentOnlyResult.WarningMessage -ExpectedSubstring 'não contém filtros ativos' -Message 'Comment-only presets should return a useful warning.'
}
finally {
    if (Test-Path -LiteralPath $testRoot.Root) {
        Remove-Item -LiteralPath $testRoot.Root -Recurse -Force
    }
}

Write-Host 'ProfileManager tests passed'
