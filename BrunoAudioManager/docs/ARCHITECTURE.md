# Bruno Audio Manager Architecture

Bruno Audio Manager is organized as a small PowerShell entry point plus focused modules. The goal is to keep Windows Forms code separate from Equalizer APO file operations so future interfaces can reuse the same management logic.

## Modules

- `AppConfig.psm1`: app metadata, profile catalog, default preferences, and managed Equalizer APO include lines.
- `AppPaths.psm1`: project, settings, logs, docs, Equalizer APO, Peace, and tool path resolution.
- `ApoManager.psm1`: Equalizer APO and Peace detection plus required config structure setup.
- `ProfileManager.psm1`: preset file naming, profile directory creation, active profile reads, and profile switching.
- `BackupManager.psm1`: ZIP export and import for profile backups.
- `LogManager.psm1`: audio profile change logging.
- `SettingsManager.psm1`: JSON preferences.
- `ToolLauncher.psm1`: safe opening of Peace, Configuration Editor, folders, and documentation.
- `MainForm.psm1`: Windows Forms UI construction and event wiring.

## Future Extension Points

- `DeviceManager.psm1`: automatic detection of connected HD599 or WH1000XM4 devices.
- `TrayManager.psm1`: system tray icon and quick profile access.
- `HotkeyManager.psm1`: global shortcuts for profile switching.
- `UpdateManager.psm1`: GitHub-based update checks and application updates.

The v1.0 modules should accept injectable paths for verification so automated checks can run against temporary folders instead of writing to `C:\Program Files`.
