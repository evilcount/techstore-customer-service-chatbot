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
