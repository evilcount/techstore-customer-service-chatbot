# Bruno Audio Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Bruno Audio Manager v1.0 as a modular PowerShell 7 Windows Forms desktop app for managing Equalizer APO and Peace profiles.

**Architecture:** The app uses a small entry script plus focused PowerShell modules for configuration, paths, APO setup, profiles, backups, logs, settings, external tools, and the main WinForms UI. Non-UI modules accept injectable paths so verification can run against temporary folders instead of `C:\Program Files`.

**Tech Stack:** PowerShell 7, Windows Forms (.NET), built-in PowerShell cmdlets only, Windows 11.

---

## File Structure

Create these files:

- `BrunoAudioManager/BrunoAudioManager.ps1`: entry point, module import, startup, `-SelfTest` mode.
- `BrunoAudioManager/modules/AppConfig.psm1`: app constants and profile catalog.
- `BrunoAudioManager/modules/AppPaths.psm1`: project, APO, logs, settings, docs, and tool path resolution.
- `BrunoAudioManager/modules/SettingsManager.psm1`: JSON preferences.
- `BrunoAudioManager/modules/LogManager.psm1`: audio profile change log.
- `BrunoAudioManager/modules/ProfileManager.psm1`: profile file names, `Active.txt`, preset creation, profile switching.
- `BrunoAudioManager/modules/ApoManager.psm1`: Equalizer APO and Peace detection plus required config setup.
- `BrunoAudioManager/modules/BackupManager.psm1`: ZIP export/import of `Profiles/`.
- `BrunoAudioManager/modules/ToolLauncher.psm1`: safe launch/open helpers.
- `BrunoAudioManager/modules/MainForm.psm1`: Windows Forms layout and event wiring.
- `BrunoAudioManager/assets/.gitkeep`: keep assets folder.
- `BrunoAudioManager/logs/.gitkeep`: keep logs folder without committing runtime log content.
- `BrunoAudioManager/settings/preferences.json`: default preferences.
- `BrunoAudioManager/docs/USER_GUIDE.md`: user instructions.
- `BrunoAudioManager/docs/ARCHITECTURE.md`: module responsibilities.
- `BrunoAudioManager/README.md`: project overview and quick start.
- `BrunoAudioManager/CHANGELOG.md`: v1.0 entry.
- `BrunoAudioManager/LICENSE`: MIT license.

Do not modify unrelated existing files in the repository.

---

## Task 1: Scaffold Project and Documentation

**Files:**

- Create: `BrunoAudioManager/BrunoAudioManager.ps1`
- Create: `BrunoAudioManager/modules/AppConfig.psm1`
- Create: `BrunoAudioManager/assets/.gitkeep`
- Create: `BrunoAudioManager/logs/.gitkeep`
- Create: `BrunoAudioManager/settings/preferences.json`
- Create: `BrunoAudioManager/docs/USER_GUIDE.md`
- Create: `BrunoAudioManager/docs/ARCHITECTURE.md`
- Create: `BrunoAudioManager/README.md`
- Create: `BrunoAudioManager/CHANGELOG.md`
- Create: `BrunoAudioManager/LICENSE`

- [ ] **Step 1: Create the folder tree**

Use `apply_patch` to add the project files under `BrunoAudioManager/`.

- [ ] **Step 2: Add `AppConfig.psm1`**

```powershell
function Get-AppInfo {
    [CmdletBinding()]
    param()

    [pscustomobject]@{
        Name    = 'Bruno Audio Manager'
        Version = '1.0.0'
    }
}

function Get-ProfileCatalog {
    [CmdletBinding()]
    param()

    [ordered]@{
        HD599 = @(
            'Reference',
            'Music',
            'Rock & Metal',
            'Cinema',
            'Gaming FPS',
            'Gaming Immersive'
        )
        WH1000XM4 = @(
            'Reference',
            'Music',
            'Cinema',
            'Gaming',
            'Travel'
        )
    }
}

function Get-DefaultPreferences {
    [CmdletBinding()]
    param()

    [pscustomobject]@{
        selectedDevice   = 'HD599'
        selectedProfile  = 'Reference'
        lastBackupFolder = ''
    }
}

function Get-ManagedConfigLines {
    [CmdletBinding()]
    param()

    @(
        'Include: Profiles\Active.txt',
        'Include: peace.txt'
    )
}

Export-ModuleMember -Function Get-AppInfo, Get-ProfileCatalog, Get-DefaultPreferences, Get-ManagedConfigLines
```

- [ ] **Step 3: Add the initial entry point**

```powershell
[CmdletBinding()]
param(
    [switch]$SelfTest,
    [string]$ApoConfigRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Error 'Bruno Audio Manager requires PowerShell 7 or newer.'
    exit 1
}

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ModuleRoot = Join-Path $ProjectRoot 'modules'

Import-Module (Join-Path $ModuleRoot 'AppConfig.psm1') -Force

if ($SelfTest) {
    $appInfo = Get-AppInfo
    Write-Host "$($appInfo.Name) $($appInfo.Version) self-test bootstrap OK"
    exit 0
}

Write-Host 'Bruno Audio Manager bootstrap is ready. Additional modules will be loaded in later tasks.'
```

- [ ] **Step 4: Add default preferences**

```json
{
  "selectedDevice": "HD599",
  "selectedProfile": "Reference",
  "lastBackupFolder": ""
}
```

- [ ] **Step 5: Add docs**

`README.md` must include:

```markdown
# Bruno Audio Manager

Bruno Audio Manager is a Windows desktop tool for managing Equalizer APO and Peace profiles without editing configuration files manually.

## Requirements

- Windows 11
- PowerShell 7 or newer
- Equalizer APO installed at `C:\Program Files\EqualizerAPO`
- Peace installed inside the Equalizer APO config folder when Peace integration is desired

## Run

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\BrunoAudioManager.ps1
```

## Self-Test

```powershell
pwsh -NoProfile -File .\BrunoAudioManager.ps1 -SelfTest
```
```

`CHANGELOG.md` must include:

```markdown
# Changelog

## 1.0.0 - 2026-06-26

- Initial Bruno Audio Manager release.
```

`LICENSE` must contain the MIT License with copyright holder `Bruno Pieri`.

`docs/USER_GUIDE.md` must explain running the app, switching profiles, exporting backups, and importing backups.

`docs/ARCHITECTURE.md` must summarize each module and name future modules: `DeviceManager.psm1`, `TrayManager.psm1`, `HotkeyManager.psm1`, and `UpdateManager.psm1`.

- [ ] **Step 6: Verify bootstrap**

Run:

```powershell
pwsh -NoProfile -File .\BrunoAudioManager\BrunoAudioManager.ps1 -SelfTest
```

Expected output contains:

```text
Bruno Audio Manager 1.0.0 self-test bootstrap OK
```

- [ ] **Step 7: Commit**

```powershell
git add BrunoAudioManager
git commit -m "feat: scaffold bruno audio manager"
```

---

## Task 2: Add Paths, Settings, and Logging

**Files:**

- Create: `BrunoAudioManager/modules/AppPaths.psm1`
- Create: `BrunoAudioManager/modules/SettingsManager.psm1`
- Create: `BrunoAudioManager/modules/LogManager.psm1`
- Modify: `BrunoAudioManager/BrunoAudioManager.ps1`

- [ ] **Step 1: Add `AppPaths.psm1`**

```powershell
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
```

- [ ] **Step 2: Add `SettingsManager.psm1`**

```powershell
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
```

- [ ] **Step 3: Add `LogManager.psm1`**

```powershell
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

Export-ModuleMember -Function Initialize-Log, Write-ProfileChangeLog
```

- [ ] **Step 4: Update `BrunoAudioManager.ps1` imports and self-test**

The entry point must import `AppPaths`, `SettingsManager`, and `LogManager`, then in `-SelfTest` create app paths from injected `-ApoConfigRoot`, initialize settings/log folders, and print:

```text
Paths, settings, and logging self-test OK
```

- [ ] **Step 5: Verify**

Run:

```powershell
pwsh -NoProfile -File .\BrunoAudioManager\BrunoAudioManager.ps1 -SelfTest -ApoConfigRoot "$env:TEMP\BrunoAudioManager-ApoTest"
```

Expected output contains:

```text
Bruno Audio Manager 1.0.0 self-test bootstrap OK
Paths, settings, and logging self-test OK
```

- [ ] **Step 6: Commit**

```powershell
git add BrunoAudioManager
git commit -m "feat: add app paths settings and logging"
```

---

## Task 3: Add APO and Profile Management

**Files:**

- Create: `BrunoAudioManager/modules/ProfileManager.psm1`
- Create: `BrunoAudioManager/modules/ApoManager.psm1`
- Modify: `BrunoAudioManager/BrunoAudioManager.ps1`

- [ ] **Step 1: Add `ProfileManager.psm1`**

Implement functions:

```powershell
function ConvertTo-PresetFileName {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ProfileName
    )

    $safeName = $ProfileName -replace '&', 'and'
    $safeName = $safeName -replace '[\\/:*?"<>|]', ''
    $safeName = $safeName -replace '\s+', ' '
    return "$($safeName.Trim()).txt"
}

function Get-PresetRelativePath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Device,
        [Parameter(Mandatory)]
        [string]$ProfileName
    )

    Join-Path $Device (ConvertTo-PresetFileName -ProfileName $ProfileName)
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
            Ensure-PresetFile -ProfilesRoot $ProfilesRoot -Device $device -ProfileName $profile
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
            "# Bruno Audio Manager preset"
            "# Device: $Device"
            "# Profile: $ProfileName"
            "# Add Equalizer APO filters below this line."
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

    $line = Get-Content -LiteralPath $ActiveProfilePath | Where-Object { $_ -match '^Include:\s*(.+)$' } | Select-Object -First 1
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

    Ensure-PresetFile -ProfilesRoot $ProfilesRoot -Device $Device -ProfileName $ProfileName | Out-Null
    $relativePath = Get-PresetRelativePath -Device $Device -ProfileName $ProfileName
    "Include: $relativePath" | Set-Content -LiteralPath $ActiveProfilePath -Encoding UTF8

    [pscustomobject]@{
        Device      = $Device
        ProfileName = $ProfileName
        DisplayName = "$Device / $ProfileName"
        IncludeLine = "Include: $relativePath"
    }
}

Export-ModuleMember -Function ConvertTo-PresetFileName, Get-PresetRelativePath, Ensure-ProfileLibrary, Ensure-PresetFile, Get-ActiveProfile, Set-ActiveProfile
```

- [ ] **Step 2: Add `ApoManager.psm1`**

Implement functions:

```powershell
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
```

- [ ] **Step 3: Update self-test**

In `BrunoAudioManager.ps1`, import `ProfileManager.psm1` before `ApoManager.psm1`. In `-SelfTest`, create the injected APO root if `-ApoConfigRoot` is supplied, run `Initialize-ApoStructure`, switch to `HD599 / Music`, read active profile, and print:

```text
APO and profile management self-test OK
```

- [ ] **Step 4: Verify**

Run:

```powershell
pwsh -NoProfile -File .\BrunoAudioManager\BrunoAudioManager.ps1 -SelfTest -ApoConfigRoot "$env:TEMP\BrunoAudioManager-ApoTest"
```

Expected output contains:

```text
APO and profile management self-test OK
```

Also verify this file exists:

```powershell
Test-Path "$env:TEMP\BrunoAudioManager-ApoTest\Profiles\Active.txt"
```

Expected output:

```text
True
```

- [ ] **Step 5: Commit**

```powershell
git add BrunoAudioManager
git commit -m "feat: manage equalizer apo profiles"
```

---

## Task 4: Add Backup and Tool Launching

**Files:**

- Create: `BrunoAudioManager/modules/BackupManager.psm1`
- Create: `BrunoAudioManager/modules/ToolLauncher.psm1`
- Modify: `BrunoAudioManager/BrunoAudioManager.ps1`

- [ ] **Step 1: Add `BackupManager.psm1`**

Implement functions:

```powershell
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
```

- [ ] **Step 2: Add `ToolLauncher.psm1`**

Implement functions:

```powershell
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
```

- [ ] **Step 3: Update self-test**

In `BrunoAudioManager.ps1`, import backup and tool modules. In `-SelfTest`, export the temporary `Profiles/` folder to `$env:TEMP\BrunoAudioManager-ProfilesBackup.zip`, import it back into the temp APO root, and print:

```text
Backup management self-test OK
```

Do not call `Start-Process` during self-test.

- [ ] **Step 4: Verify**

Run:

```powershell
pwsh -NoProfile -File .\BrunoAudioManager\BrunoAudioManager.ps1 -SelfTest -ApoConfigRoot "$env:TEMP\BrunoAudioManager-ApoTest"
```

Expected output contains:

```text
Backup management self-test OK
```

- [ ] **Step 5: Commit**

```powershell
git add BrunoAudioManager
git commit -m "feat: add profile backups and tool launchers"
```

---

## Task 5: Build Windows Forms UI

**Files:**

- Create: `BrunoAudioManager/modules/MainForm.psm1`
- Modify: `BrunoAudioManager/BrunoAudioManager.ps1`

- [ ] **Step 1: Add `MainForm.psm1`**

Implement `Show-BrunoAudioManagerForm` with these parameters:

```powershell
function Show-BrunoAudioManagerForm {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [psobject]$Paths,
        [Parameter(Mandatory)]
        [psobject]$AppInfo,
        [Parameter(Mandatory)]
        [hashtable]$ProfileCatalog,
        [Parameter(Mandatory)]
        [psobject]$ApoStatus,
        [Parameter(Mandatory)]
        [psobject]$Preferences
    )

    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    [System.Windows.Forms.Application]::EnableVisualStyles()

    $form = New-Object System.Windows.Forms.Form
    $form.Text = $AppInfo.Name
    $form.StartPosition = 'CenterScreen'
    $form.Size = New-Object System.Drawing.Size(860, 640)
    $form.MinimumSize = New-Object System.Drawing.Size(760, 560)

    $title = New-Object System.Windows.Forms.Label
    $title.Text = "$($AppInfo.Name) v$($AppInfo.Version)"
    $title.Font = New-Object System.Drawing.Font('Segoe UI', 16, [System.Drawing.FontStyle]::Bold)
    $title.AutoSize = $true
    $title.Location = New-Object System.Drawing.Point(20, 18)
    $form.Controls.Add($title)

    $infoBox = New-Object System.Windows.Forms.GroupBox
    $infoBox.Text = 'Informacoes'
    $infoBox.Location = New-Object System.Drawing.Point(20, 60)
    $infoBox.Size = New-Object System.Drawing.Size(800, 110)
    $form.Controls.Add($infoBox)

    $active = Get-ActiveProfile -ActiveProfilePath $Paths.ActiveProfilePath
    $infoLabel = New-Object System.Windows.Forms.Label
    $infoLabel.AutoSize = $true
    $infoLabel.Location = New-Object System.Drawing.Point(15, 25)
    $infoLabel.Text = "Equalizer APO detectado: $($ApoStatus.EqualizerApoDetected)`r`nPeace detectado: $($ApoStatus.PeaceDetected)`r`nPerfil ativo: $($active.DisplayName)`r`nDispositivo selecionado: $($active.Device)"
    $infoBox.Controls.Add($infoLabel)

    $statusLabel = New-Object System.Windows.Forms.Label
    $statusLabel.AutoSize = $true
    $statusLabel.Location = New-Object System.Drawing.Point(20, 560)
    $statusLabel.Text = $ApoStatus.Message
    $form.Controls.Add($statusLabel)

    $libraryBox = New-Object System.Windows.Forms.GroupBox
    $libraryBox.Text = 'Biblioteca de Perfis'
    $libraryBox.Location = New-Object System.Drawing.Point(20, 185)
    $libraryBox.Size = New-Object System.Drawing.Size(520, 350)
    $form.Controls.Add($libraryBox)

    $x = 20
    foreach ($device in $ProfileCatalog.Keys) {
        $deviceLabel = New-Object System.Windows.Forms.Label
        $deviceLabel.Text = $device
        $deviceLabel.Font = New-Object System.Drawing.Font('Segoe UI', 10, [System.Drawing.FontStyle]::Bold)
        $deviceLabel.AutoSize = $true
        $deviceLabel.Location = New-Object System.Drawing.Point($x, 28)
        $libraryBox.Controls.Add($deviceLabel)

        $y = 58
        foreach ($profile in $ProfileCatalog[$device]) {
            $button = New-Object System.Windows.Forms.Button
            $button.Text = $profile
            $button.Size = New-Object System.Drawing.Size(220, 34)
            $button.Location = New-Object System.Drawing.Point($x, $y)
            $button.Enabled = [bool]$ApoStatus.EqualizerApoDetected
            $button.Tag = [pscustomobject]@{ Device = $device; Profile = $profile }
            $button.Add_Click({
                param($sender, $eventArgs)
                $selection = $sender.Tag
                try {
                    $old = Get-ActiveProfile -ActiveProfilePath $Paths.ActiveProfilePath
                    $new = Set-ActiveProfile -ProfilesRoot $Paths.ProfilesRoot -ActiveProfilePath $Paths.ActiveProfilePath -Device $selection.Device -ProfileName $selection.Profile
                    Write-ProfileChangeLog -AudioLogPath $Paths.AudioLogPath -OldProfile $old.DisplayName -NewProfile $new.DisplayName

                    $Preferences.selectedDevice = $selection.Device
                    $Preferences.selectedProfile = $selection.Profile
                    Save-Preferences -PreferencesPath $Paths.PreferencesPath -Preferences $Preferences

                    $infoLabel.Text = "Equalizer APO detectado: $($ApoStatus.EqualizerApoDetected)`r`nPeace detectado: $($ApoStatus.PeaceDetected)`r`nPerfil ativo: $($new.DisplayName)`r`nDispositivo selecionado: $($new.Device)"
                    $statusLabel.Text = "Perfil aplicado: $($new.DisplayName)"
                }
                catch {
                    [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Bruno Audio Manager', 'OK', 'Error') | Out-Null
                    $statusLabel.Text = 'Erro ao aplicar perfil.'
                }
            })
            $libraryBox.Controls.Add($button)
            $y += 40
        }

        $x += 250
    }

    $toolsBox = New-Object System.Windows.Forms.GroupBox
    $toolsBox.Text = 'Ferramentas'
    $toolsBox.Location = New-Object System.Drawing.Point(560, 185)
    $toolsBox.Size = New-Object System.Drawing.Size(260, 215)
    $form.Controls.Add($toolsBox)

    $toolButtons = @(
        @{ Text = 'Abrir Peace'; Path = $Paths.PeaceExePath; Name = 'Peace' },
        @{ Text = 'Abrir Configuration Editor'; Path = $Paths.ConfigEditorExePath; Name = 'Configuration Editor' },
        @{ Text = 'Abrir pasta Profiles'; Path = $Paths.ProfilesRoot; Name = 'Profiles folder' },
        @{ Text = 'Abrir pasta do projeto'; Path = $Paths.ProjectRoot; Name = 'Project folder' },
        @{ Text = 'Abrir documentacao'; Path = $Paths.UserGuidePath; Name = 'Documentation' }
    )

    $toolY = 25
    foreach ($tool in $toolButtons) {
        $button = New-Object System.Windows.Forms.Button
        $button.Text = $tool.Text
        $button.Size = New-Object System.Drawing.Size(220, 30)
        $button.Location = New-Object System.Drawing.Point(18, $toolY)
        $button.Tag = $tool
        $button.Add_Click({
            param($sender, $eventArgs)
            $toolInfo = $sender.Tag
            try {
                Open-ExistingPath -Path $toolInfo.Path -FriendlyName $toolInfo.Name
                $statusLabel.Text = "Aberto: $($toolInfo.Name)"
            }
            catch {
                [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Bruno Audio Manager', 'OK', 'Information') | Out-Null
                $statusLabel.Text = "$($toolInfo.Name) indisponivel."
            }
        })
        $toolsBox.Controls.Add($button)
        $toolY += 35
    }

    $backupBox = New-Object System.Windows.Forms.GroupBox
    $backupBox.Text = 'Backup'
    $backupBox.Location = New-Object System.Drawing.Point(560, 420)
    $backupBox.Size = New-Object System.Drawing.Size(260, 115)
    $form.Controls.Add($backupBox)

    $exportButton = New-Object System.Windows.Forms.Button
    $exportButton.Text = 'Export Profiles'
    $exportButton.Size = New-Object System.Drawing.Size(220, 30)
    $exportButton.Location = New-Object System.Drawing.Point(18, 28)
    $exportButton.Enabled = [bool]$ApoStatus.EqualizerApoDetected
    $exportButton.Add_Click({
        $dialog = New-Object System.Windows.Forms.SaveFileDialog
        $dialog.Filter = 'ZIP files (*.zip)|*.zip'
        $dialog.FileName = 'BrunoAudioManager-Profiles.zip'
        if ($dialog.ShowDialog() -eq 'OK') {
            try {
                Export-ProfilesBackup -ProfilesRoot $Paths.ProfilesRoot -DestinationZip $dialog.FileName | Out-Null
                $Preferences.lastBackupFolder = Split-Path -Parent $dialog.FileName
                Save-Preferences -PreferencesPath $Paths.PreferencesPath -Preferences $Preferences
                $statusLabel.Text = 'Profiles exportados com sucesso.'
            }
            catch {
                [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Bruno Audio Manager', 'OK', 'Error') | Out-Null
            }
        }
    })
    $backupBox.Controls.Add($exportButton)

    $importButton = New-Object System.Windows.Forms.Button
    $importButton.Text = 'Import Profiles'
    $importButton.Size = New-Object System.Drawing.Size(220, 30)
    $importButton.Location = New-Object System.Drawing.Point(18, 65)
    $importButton.Enabled = [bool]$ApoStatus.EqualizerApoDetected
    $importButton.Add_Click({
        $dialog = New-Object System.Windows.Forms.OpenFileDialog
        $dialog.Filter = 'ZIP files (*.zip)|*.zip'
        if ($dialog.ShowDialog() -eq 'OK') {
            try {
                Import-ProfilesBackup -ProfilesRoot $Paths.ProfilesRoot -SourceZip $dialog.FileName
                $activeAfterImport = Get-ActiveProfile -ActiveProfilePath $Paths.ActiveProfilePath
                $infoLabel.Text = "Equalizer APO detectado: $($ApoStatus.EqualizerApoDetected)`r`nPeace detectado: $($ApoStatus.PeaceDetected)`r`nPerfil ativo: $($activeAfterImport.DisplayName)`r`nDispositivo selecionado: $($activeAfterImport.Device)"
                $statusLabel.Text = 'Profiles importados com sucesso.'
            }
            catch {
                [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Bruno Audio Manager', 'OK', 'Error') | Out-Null
            }
        }
    })
    $backupBox.Controls.Add($importButton)

    [void]$form.ShowDialog()
}

Export-ModuleMember -Function Show-BrunoAudioManagerForm
```

- [ ] **Step 2: Update entry point normal mode**

`BrunoAudioManager.ps1` normal mode must:

1. Import all modules.
2. Build `$paths`, `$appInfo`, `$profileCatalog`, `$preferences`.
3. Initialize settings and logs.
4. Initialize APO structure.
5. Call `Show-BrunoAudioManagerForm`.

- [ ] **Step 3: Verify syntax with self-test**

Run:

```powershell
pwsh -NoProfile -File .\BrunoAudioManager\BrunoAudioManager.ps1 -SelfTest -ApoConfigRoot "$env:TEMP\BrunoAudioManager-ApoTest"
```

Expected output contains all previous self-test lines and no parser errors.

- [ ] **Step 4: Manual UI launch**

Run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\BrunoAudioManager\BrunoAudioManager.ps1 -ApoConfigRoot "$env:TEMP\BrunoAudioManager-ApoTest"
```

Expected:

- The main window opens.
- It shows app name and version.
- It shows Equalizer APO detected as true when the temp root exists.
- HD599 and WH1000XM4 profile buttons are visible.
- Clicking `HD599 / Music` updates active profile text and `Active.txt`.

- [ ] **Step 5: Commit**

```powershell
git add BrunoAudioManager
git commit -m "feat: add bruno audio manager winforms ui"
```

---

## Task 6: Final Polish and Verification

**Files:**

- Modify: `BrunoAudioManager/README.md`
- Modify: `BrunoAudioManager/docs/USER_GUIDE.md`
- Modify: `BrunoAudioManager/docs/ARCHITECTURE.md`
- Modify: `BrunoAudioManager/BrunoAudioManager.ps1`
- Modify modules if verification finds small defects.

- [ ] **Step 1: Review docs against implemented commands**

Ensure every documented command uses:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\BrunoAudioManager.ps1
```

from inside the `BrunoAudioManager/` directory, and:

```powershell
pwsh -NoProfile -File .\BrunoAudioManager.ps1 -SelfTest
```

for verification.

- [ ] **Step 2: Run full self-test**

Run:

```powershell
pwsh -NoProfile -File .\BrunoAudioManager\BrunoAudioManager.ps1 -SelfTest -ApoConfigRoot "$env:TEMP\BrunoAudioManager-ApoTest"
```

Expected output contains:

```text
Bruno Audio Manager 1.0.0 self-test bootstrap OK
Paths, settings, and logging self-test OK
APO and profile management self-test OK
Backup management self-test OK
```

- [ ] **Step 3: Inspect generated temp APO structure**

Run:

```powershell
Get-ChildItem "$env:TEMP\BrunoAudioManager-ApoTest\Profiles" -Recurse | Select-Object FullName
```

Expected:

- `Active.txt` exists.
- `HD599\Reference.txt` exists.
- `HD599\Music.txt` exists.
- `WH1000XM4\Travel.txt` exists.

- [ ] **Step 4: Check git status**

Run:

```powershell
git status --short
```

Expected:

- Only Bruno Audio Manager files changed for this feature.
- Existing unrelated workspace changes remain untouched.

- [ ] **Step 5: Commit polish**

If docs or fixes changed:

```powershell
git add BrunoAudioManager
git commit -m "docs: finalize bruno audio manager v1"
```

If no files changed, do not create an empty commit.

---

## Self-Review

Spec coverage:

- Project folder and GitHub-ready docs are covered in Tasks 1 and 6.
- PowerShell 7 and Windows Forms are covered in Tasks 1 and 5.
- Equalizer APO structure, `config.txt`, `Active.txt`, and preset directories are covered in Task 3.
- Profile buttons and UI status are covered in Task 5.
- Tool buttons are covered in Tasks 4 and 5.
- ZIP export/import is covered in Task 4.
- Logging is covered in Task 2 and wired in Task 5.
- JSON preferences are covered in Task 2 and wired in Task 5.
- Friendly missing-tool handling is covered in Tasks 3, 4, and 5.
- Future architecture extension points are covered in Task 1 documentation.

Placeholder scan:

- No placeholder markers or incomplete task references remain.

Type consistency:

- `Get-AppPaths` returns the path properties consumed by APO, profile, backup, tool, and UI modules.
- `Get-ActiveProfile` and `Set-ActiveProfile` both return `Device`, `ProfileName`, `DisplayName`, and `IncludeLine`.
- `Initialize-ApoStructure` returns `EqualizerApoDetected`, `PeaceDetected`, `ConfigEditorDetected`, and `Message`, matching the UI.

