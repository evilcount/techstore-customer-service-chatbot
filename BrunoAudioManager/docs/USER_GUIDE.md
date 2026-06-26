# Bruno Audio Manager User Guide

## Running the App

Open PowerShell 7, go to the `BrunoAudioManager/` directory, and run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\BrunoAudioManager.ps1
```

To verify the basic installation without opening the desktop interface, run:

```powershell
pwsh -NoProfile -File .\BrunoAudioManager.ps1 -SelfTest
```

## Switching Profiles

The main window shows profile buttons grouped by device. Select a profile under `HD599` or `WH1000XM4` to update `Profiles\Active.txt` and apply that Equalizer APO preset through the managed include chain.

## Exporting Backups

Use `Export Profiles` to save the current Equalizer APO `Profiles/` folder to a ZIP file. Keep the ZIP somewhere safe before changing or importing presets.

## Importing Backups

Use `Import Profiles` to restore presets from a ZIP backup. The app validates and extracts the backup before copying profile files into the Equalizer APO profile folder.

## Expected Equalizer APO Structure

Bruno Audio Manager expects Equalizer APO configuration files under:

```text
C:\Program Files\EqualizerAPO\config\
```

The app manages `Profiles\Active.txt` and expects `config.txt` to include:

```text
Include: Profiles\Active.txt
Include: peace.txt
```
