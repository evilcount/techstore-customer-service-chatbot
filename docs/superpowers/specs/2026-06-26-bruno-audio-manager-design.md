# Bruno Audio Manager Design

## Goal

Build Bruno Audio Manager v1.0 as a Windows desktop application for managing Equalizer APO and Peace profiles without manual file editing.

The application will be implemented with PowerShell 7 and Windows Forms (.NET), without external dependencies, and organized so it can later become its own GitHub repository.

## Scope

Version 1.0 includes:

- A Windows Forms desktop interface.
- Equalizer APO and Peace detection.
- Automatic setup of the expected Equalizer APO profile folder structure.
- Profile switching for HD599 and WH1000XM4 presets.
- Immediate preset application by updating `Profiles\Active.txt`.
- Status display for the active profile and selected device.
- Tool buttons for Peace, Configuration Editor, profile folder, project folder, and documentation.
- ZIP export and import for profile backups.
- Audio profile change logging.
- User preferences stored in JSON.
- Friendly error handling for missing Equalizer APO, missing files, and missing folders.

Version 1.0 does not include:

- Automatic connected-device detection.
- System tray integration.
- Global hotkeys.
- Per-game or per-application profiles.
- GitHub auto-update.
- WinUI or WPF interface.

Those future features should be possible without major restructuring.

## Repository Structure

The project will live in a new isolated folder inside the current workspace:

```text
BrunoAudioManager/
  BrunoAudioManager.ps1
  modules/
    AppConfig.psm1
    AppPaths.psm1
    ApoManager.psm1
    ProfileManager.psm1
    BackupManager.psm1
    LogManager.psm1
    SettingsManager.psm1
    ToolLauncher.psm1
    MainForm.psm1
  assets/
  docs/
    USER_GUIDE.md
    ARCHITECTURE.md
  logs/
    audio.log
  settings/
    preferences.json
  README.md
  CHANGELOG.md
  LICENSE
```

## Equalizer APO Layout

The application assumes the following Equalizer APO configuration root:

```text
C:\Program Files\EqualizerAPO\config\
  config.txt
  peace.txt
  Profiles\
    Active.txt
    HD599\
    WH1000XM4\
```

`config.txt` should contain exactly the application-managed include chain:

```text
Include: Profiles\Active.txt
Include: peace.txt
```

`Profiles\Active.txt` will contain an include directive pointing to the currently selected preset, for example:

```text
Include: HD599\Music.txt
```

Each preset is a `.txt` file under its device folder and contains Equalizer APO filters.

## Profile Library

The v1.0 profile catalog is fixed in code through `AppConfig.psm1`.

HD599 profiles:

- Reference
- Music
- Rock & Metal
- Cinema
- Gaming FPS
- Gaming Immersive

WH1000XM4 profiles:

- Reference
- Music
- Cinema
- Gaming
- Travel

Each profile is represented as a button in the main window. Clicking a profile button:

1. Reads the current active profile.
2. Writes the new include line to `Profiles\Active.txt`.
3. Creates the preset file if it is absent.
4. Logs the change.
5. Saves the selected device/profile in preferences.
6. Refreshes the interface.

## Module Responsibilities

### `BrunoAudioManager.ps1`

Main entry point.

Responsibilities:

- Require or validate PowerShell 7.
- Resolve the project root.
- Import modules in dependency order.
- Initialize settings and directories.
- Start the Windows Forms interface.

### `AppConfig.psm1`

Application constants.

Responsibilities:

- App name and version.
- Profile catalog.
- Expected Equalizer APO config content.
- Default folder names and file names.
- User-facing labels.

### `AppPaths.psm1`

Path resolution.

Responsibilities:

- Return the project root.
- Return the Equalizer APO config path.
- Return paths for `Profiles`, `Active.txt`, `config.txt`, `peace.txt`, logs, settings, docs, and tools.
- Avoid scattering literal paths across the codebase.

### `ApoManager.psm1`

Equalizer APO and Peace integration.

Responsibilities:

- Detect whether Equalizer APO appears installed.
- Detect whether Peace appears available.
- Detect Configuration Editor if available.
- Ensure required folders and files exist.
- Create `Active.txt` if absent.
- Create `config.txt` if absent.
- Return status objects for the UI.

If Equalizer APO is missing, the app should still open and show a friendly warning, but profile switching and backup actions that depend on the APO folder should be disabled or guarded.

### `ProfileManager.psm1`

Profile operations.

Responsibilities:

- Return the configured profile catalog.
- Ensure device profile directories exist.
- Ensure preset files exist with safe placeholder content.
- Read the active profile from `Active.txt`.
- Change the active profile.
- Convert display profile names to file-safe preset names.

### `BackupManager.psm1`

ZIP export/import.

Responsibilities:

- Export `Profiles/` to a ZIP using `Compress-Archive`.
- Import a ZIP using `Expand-Archive`.
- Preserve device folder structure.
- Refresh active profile state after import.
- Fail with clear messages if the backup file is invalid or Equalizer APO is unavailable.

### `LogManager.psm1`

Logging.

Responsibilities:

- Ensure `logs/` exists.
- Append profile changes to `logs/audio.log`.
- Record date, time, old profile, and new profile.

The log format should be simple and readable:

```text
2026-06-26 14:30:00 | Old: HD599 / Reference | New: HD599 / Music
```

### `SettingsManager.psm1`

User preferences.

Responsibilities:

- Ensure `settings/preferences.json` exists.
- Load settings as a PowerShell object.
- Save settings as JSON.
- Store selected device, selected profile, and last backup folder.

Initial JSON shape:

```json
{
  "selectedDevice": "HD599",
  "selectedProfile": "Reference",
  "lastBackupFolder": ""
}
```

### `ToolLauncher.psm1`

External launches.

Responsibilities:

- Open Peace.
- Open Configuration Editor.
- Open the Equalizer APO `Profiles` folder.
- Open the project folder.
- Open documentation.
- Show friendly messages if a tool or folder is unavailable.

### `MainForm.psm1`

Windows Forms UI.

Responsibilities:

- Build the main window.
- Render application information.
- Render profile buttons grouped by device.
- Render tools and backup buttons.
- Wire button events to the manager modules.
- Refresh UI state after actions.

This module may own UI layout code, but it should not own file operations or Equalizer APO business logic.

## UI Design

The v1.0 interface will use a single window with a practical desktop-tool layout.

Sections:

- Header: app name and version.
- Information: Equalizer APO detected, Peace detected, active profile, selected device.
- Profile Library: grouped profile buttons for HD599 and WH1000XM4.
- Tools: buttons for Peace, Configuration Editor, Profiles folder, project folder, and documentation.
- Backup: Export Profiles and Import Profiles buttons.
- Status line: last action or friendly error message.

The UI should be clear and compact rather than decorative. It should be usable on Windows 11 without requiring custom fonts, external icons, or third-party UI libraries.

## Error Handling

Missing Equalizer APO:

- Show a friendly message.
- Keep the app open.
- Disable or guard profile switching, backup import/export, and APO folder launch.

Missing `Active.txt`:

- Create automatically.
- Default to `HD599 / Reference`.

Missing folders:

- Create automatically when Equalizer APO config root exists.

Missing preset file:

- Create automatically with placeholder content.

Missing Peace or Configuration Editor:

- Show unavailable status.
- Tool button shows a friendly message instead of failing.

Backup import failure:

- Do not delete existing profiles before validating the ZIP.
- Extract to a temporary folder first, then copy validated content into `Profiles/`.

## Data Flow

Startup flow:

1. `BrunoAudioManager.ps1` imports modules.
2. Settings are loaded or created.
3. Equalizer APO paths are resolved.
4. Required APO folders/files are ensured if the APO config root exists.
5. Current active profile is read.
6. `MainForm.psm1` renders the UI.

Profile selection flow:

1. User clicks a profile button.
2. UI calls `Set-ActiveProfile`.
3. Profile manager ensures the preset file exists.
4. Profile manager writes the include line to `Active.txt`.
5. Log manager records old and new profile.
6. Settings manager saves selected device/profile.
7. UI refreshes active profile labels and status line.

Backup export flow:

1. User clicks Export Profiles.
2. UI asks for destination with a save dialog.
3. Backup manager compresses `Profiles/`.
4. UI displays success or error.

Backup import flow:

1. User clicks Import Profiles.
2. UI asks for a ZIP file.
3. Backup manager validates and extracts the ZIP.
4. Backup manager restores profile files.
5. UI refreshes active profile labels and status line.

## Maintainability

The architecture keeps file-system operations, Equalizer APO integration, settings, backup, logging, and UI in separate modules. Future features can be added by extending modules or adding new modules:

- Device detection can be added in a future `DeviceManager.psm1`.
- Tray behavior can be added in a future `TrayManager.psm1`.
- Global hotkeys can be added in a future `HotkeyManager.psm1`.
- Per-app and per-game rules can be added through a future rules module and an expanded JSON settings model.
- GitHub updates can be added in a future `UpdateManager.psm1`.
- A future WPF or WinUI interface can reuse the non-UI manager modules.

## Documentation

The project should include:

- `README.md`: purpose, requirements, quick start, folder assumptions.
- `CHANGELOG.md`: v1.0 initial release.
- `LICENSE`: MIT license text.
- `docs/USER_GUIDE.md`: how to run, switch profiles, export/import backups.
- `docs/ARCHITECTURE.md`: module responsibilities and future extension points.

## Verification

Because this is a desktop PowerShell app, verification should cover both non-UI logic and syntax:

- Run `pwsh -NoProfile -File .\BrunoAudioManager.ps1 -SelfTest` or equivalent self-test mode if implemented.
- Import each module with PowerShell 7.
- Exercise path, settings, profile, backup, and log functions against a temporary test root.
- Manually launch the UI on Windows 11 when possible.

The v1.0 implementation should avoid requiring administrative writes during automated verification by allowing test paths to be injected into the manager functions.
