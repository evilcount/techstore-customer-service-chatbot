function Show-BrunoAudioManagerForm {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [psobject]$Paths,
        [Parameter(Mandatory)]
        [psobject]$AppInfo,
        [Parameter(Mandatory)]
        [System.Collections.IDictionary]$ProfileCatalog,
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
        if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
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
        if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
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

