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

## Self-Test

From inside the `BrunoAudioManager/` directory:

```powershell
pwsh -NoProfile -File .\BrunoAudioManager.ps1 -SelfTest
```
