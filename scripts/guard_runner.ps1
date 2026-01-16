$ErrorActionPreference = "Stop"

# Function to write to log
function Write-Log {
    param ([string]$Message)
    # Use $LogFile if available, otherwise try to guess it based on script location
    $LogPath = if ($script:LogFile) { $script:LogFile } else { "$PSScriptRoot\..\wallpaper_activity.log" }

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"
    try {
        Add-Content -Path $LogPath -Value $LogEntry -ErrorAction SilentlyContinue
    } catch {
        # If logging fails, we can't do much, but we tried.
    }
    Write-Host $LogEntry
}

try {
    # Configuration
    # Since this script is now in /scripts/, we need to look up one level for state/log and sibling for bat
    $ProjectRoot = (Get-Item "$PSScriptRoot\..").FullName
    $StateFile = "$ProjectRoot\wallpaper_state.json"
    $script:LogFile = "$ProjectRoot\wallpaper_activity.log" # Update script-scoped LogFile
    $WallpaperScript = "$PSScriptRoot\run_wallpaper.bat"

    # 1. Check if we already ran today
    $Today = (Get-Date).ToString("yyyy-MM-dd")

    if (Test-Path $StateFile) {
        try {
            $State = Get-Content $StateFile | ConvertFrom-Json
            if ($State.LastRunDate -eq $Today) {
                Write-Log "Skipping update: Already executed for today ($Today)."
                exit 0
            }
        } catch {
            Write-Log "Warning: Could not read/parse state file. Proceeding with update."
        }
    }

    # 2. Run the actual wallpaper update
    Write-Log "Starting wallpaper update..."
    Write-Log "Running script: $WallpaperScript"
    Write-Log "Working Directory: $ProjectRoot"

    if (-not (Test-Path $WallpaperScript)) {
        throw "Wallpaper script not found at $WallpaperScript"
    }

    $Process = Start-Process -FilePath $WallpaperScript -WorkingDirectory $ProjectRoot -Wait -NoNewWindow -PassThru

    if ($Process.ExitCode -eq 0) {
        Write-Log "Wallpaper update completed successfully."

        # 3. Update state file
        $NewState = @{
            LastRunDate = $Today
            LastRunTime = (Get-Date).ToString("HH:mm:ss")
        }
        $NewState | ConvertTo-Json | Set-Content $StateFile
    }
    else {
        Write-Log "ERROR: Wallpaper script failed with exit code $($Process.ExitCode)."
        exit 1
    }

}
catch {
    Write-Log "CRITICAL ERROR: $_"
    Write-Log "Stack Trace: $($_.ScriptStackTrace)"
    exit 1
}
