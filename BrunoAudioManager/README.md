# Bruno Audio Manager

Bruno Audio Manager is a Windows desktop tool for managing Equalizer APO and Peace profiles without editing configuration files manually.

## Requirements

- Windows 11
- PowerShell 7 or newer
- Equalizer APO installed at `C:\Program Files\EqualizerAPO`
- Peace installed inside the Equalizer APO config folder when Peace integration is desired

## Run

From inside the `BrunoAudioManager/` directory:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\BrunoAudioManager.ps1
```

## Build Windows Launcher

From the repository root:

```powershell
pwsh -NoProfile -File .\BrunoAudioManager\tools\Build-Exe.ps1
```

The executable is generated at:

```text
BrunoAudioManager\dist\BrunoAudioManager.exe
```

The launcher requests administrator permissions and starts the PowerShell app without an interactive prompt window.
## Self-Test

From inside the `BrunoAudioManager/` directory:

```powershell
pwsh -NoProfile -File .\BrunoAudioManager.ps1 -SelfTest
```
